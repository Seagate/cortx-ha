#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>. For any questions
# about this software or licensing, please email opensource@seagate.com or
# cortx-questions@seagate.com.

from base64 import b64encode
import consul
from consul import ConsulException
from consul.base import ClientError
from requests.exceptions import RequestException
from urllib3.exceptions import HTTPError
import socket
from ha.const import HA_DELIM
from cortx.utils.log import Log
from typing import Any, Dict, List, NamedTuple, Optional

TxPutKV = NamedTuple('TxPutKV', [('key', str), ('value', str),
                                 ('cas', Optional[Any])])

#TODO: Update set/get/update function to provide blocking and non blocking function
class ConsulKvStore:
    """ Represents a Consul kv Store """

    _keys = {}

    def __init__(self, prefix: str, host: str="localhost", port: int=8500, enable_batch: bool=False):
        """
        Consul KV store.

        Args:
            prefix (str): Consul prefix
            host (str): consul host
            port (str): consul port

        Example:
            ConsulKvStore("cortx>ha", host="consul.srv", port=3000)
            ConsulKvStore("cortx>ha")
        Here (localhost:8500) is consul connection and cortx>ha is prefix.
        """
        self._prefix: str = prefix
        self._verify(prefix, host, port)
        self._consul = self._get_connection(prefix, host, port)
        self._consul.kv.put(self._prepare_key(""), None)
        self._enable_batch_put = enable_batch
        if self._enable_batch_put:
            self._payload = {}

    def _verify(self, prefix: str, host: str, port: int):
        """
        Verify connection detail.

        Args:
            prefix (str): Consul prefix
            host (str): consul host
            port (str): consul port
        """
        if prefix == "":
            raise Exception("Invalid prefix. It cannot be empty.")

    def _get_connection(self, prefix: str, host: str, port: int):
        """
        Prepare consul connection.

        Args:
            prefix (str): Consul prefix
            host (str): consul host
            port (str): consul port

        Return:
            Object: Consul object.
        """
        if host=="localhost" and port==8500:
            return consul.Consul()
        return consul.Consul(host=host, port=port)

    def _verify_data(self, *args):
        """
        Verify data.
        """
        for data in args:
            if data is None or data == "":
                raise Exception("Invalid parameter. Data cannot be none or empty.")

    def _prepare_key(self, key):
        """
        Prepare key with prefix.

        Args:
            key (str): Get Key.
        """
        key: list = [x for x in self._prefix.split(HA_DELIM) + key.split(HA_DELIM) if x != ""]
        return HA_DELIM.join(key)

    def get_prefix(self):
        return self._prefix

    def key_exists(self, key: str):
        """
        Check if key exists.

        Args:
            key (str): Consul Key.

        Return:
            bool: True if key exists else False.
        """
        k = self._prepare_key(key)

        # First find in cache if batch put is enabled
        Log.debug(f"[consul-op] is key exist in cache: {k}")
        if self._enable_batch_put and [key for key in self._payload if key.startswith(k)]:
            Log.debug(f"[consul-op] key {k} found in cache: True")
            return True

        # find in consul and check if exists
        Log.debug(f"[consul-op] is key exist: {k}")
        _, data = self._consul.kv.get(k, recurse=True)
        Log.debug(f"[consul-op] key {k} found in consul: True")

        return True if data else False

    def set(self, key: str, val: str=None):
        """
        Set key-val pair in consul. If key already exists return exception.

        Args:
            key (str): Key.
            val (str): Value.

        Return:
            str: Return value.
        """
        self._verify_data(key)
        if self.key_exists(key):
            raise Exception(f"Key {key} already exists in kv store.")
        k = self._prepare_key(key)

        if self._enable_batch_put:
            Log.debug(f"[consul-op] Putting key value in cache for key: {k}")
            self._payload[k] = val
            return val

        Log.debug(f"[consul-op] Putting key value: {k}")
        self._consul.kv.put(k, val)
        Log.debug(f"[consul-op] put Key value: {val}")
        return val

    def update(self, key: str, new_val: str):
        """
        Set key-val pair in consul. Write key-value.
        If key already exists override it.

        Args:
            key (str): Key.
            new_val (str): Value.

        Return:
            str: Return value.
        """
        self._verify_data(key)
        k = self._prepare_key(key)

        if self._enable_batch_put:
            Log.debug(f"[consul-op] Putting value in cache for key: {k}")
            self._payload[k] = new_val
            return new_val

        Log.debug(f"[consul-op] Putting value for key: {k}")
        self._consul.kv.put(k, new_val)
        Log.debug(f"[consul-op] put new value for Key: {k}")
        return new_val

    # TODO : Currently all keys with the matching prefix "key" are returned
    # add additional parameter so that only the exact matching key is returned when required
    def get(self, key: str = ""):
        """
        Get values. Default it will return all keys. It is block call,
        will take some time if consul leader is not elected.

        Args:
            key (str): Key.

        Return:
            str: Return dictionary of all key val pair.
        """
        k = self._prepare_key(key)

        # simulating consul kv get operation for _payload dict
        payload_data = None
        if self._enable_batch_put:
            # Using dictionary comprehension + startswith()
            # Prefix key match in dictionary
            Log.debug(f"[consul-op] searching key in cache: {k}")
            payload_data = {key:val for key, val in self._payload.items() if key.startswith(k)}

        Log.debug(f"[consul-op] getting the value for key: {k}")
        _, data = self._consul.kv.get(k, recurse=True)
        Log.debug(f"[consul-op] got the value for Key: {k}")

        key_val: dict = {}
        if data:
            for key in data:
                key_val[key['Key']] = key['Value'].decode("utf-8") if isinstance(key['Value'], bytes) else key['Value']

        # merge and/or overwrite the values from _payload with received data from consul kv store
        if payload_data:
            for key, val in payload_data.items():
                key_val[key] = val.decode("utf-8") if isinstance(val, bytes) else val

        return key_val if key_val else None

    def delete(self, key: str = "", recurse: bool = False):
        """
        Delete values.
        If called with no parameter then it will not delete anything.
        If called with delete(recurse=True) then delete all keys.
        If called with delete(key="key", recurse=True) then delete all under key

        Args:
            key (str): Key.

        Return:
            str: Return dictionary of all key val pair.
        """
        data = self.get(key)
        k = self._prepare_key(key)

        # if enabled batch put then delete from payload if any new value exist
        # then continue to delete from consul as old value may exist same prefix.
        if self._enable_batch_put:
            Log.debug(f"[consul-op] deleting value for key: {k} from cache, recursively : {recurse}.")
            if recurse:
                for key in list(self._payload.keys()):
                    if key.startswith(k):
                        Log.debug(f"[consul-op] deleting key: {key} from cache.")
                        del self._payload[key]
                # let it continue to delete all the matching keys from consul also
            else:
                 if k in self._payload:
                     Log.debug(f"[consul-op] deleting key: {k} from cache.")
                     del self._payload[k]
                # let it continue to delete the same key from consul if exist.

        Log.debug(f"[consul-op] deleting key value: {k}")
        self._consul.kv.delete(k, recurse=recurse)
        Log.debug(f"[consul-op] deleted Key value: {data}")
        return data

    def get_keys(self, prefix):
        """
        Get list of values match with given prefix.
        The requested keys will be stored with prefix for reference.
        Args:
            prefix(str): Prefix that matches with keys
        Return:
            List of keys
        """
        if not ConsulKvStore._keys.get(prefix):

            # get cached keys if batch put is enabled
            payload_keys = None
            if self._enable_batch_put:
                # Using dictionary comprehension + startswith()
                # Prefix key match in dictionary
                payload_keys = [key for key in self._payload if key.startswith(prefix)]

            ConsulKvStore._keys[prefix] = self._consul.kv.get(prefix, keys=True)[1]

            # Merge lists with unique values
            if payload_keys:
                ConsulKvStore._keys[prefix] = list(set(payload_keys + ConsulKvStore._keys[prefix]))

        return ConsulKvStore._keys[prefix]

    def _kv_put_in_transaction(self, tx_payload: List[TxPutKV]):
        """
         This function put all the values from provided tuple list to consul server

        Args:
            tx_payload (List[TxPutKV]): list of Tuple that needs to put in consul server see definition 'TxPutKV'.
        """
        def to_payload(v: TxPutKV) -> Dict[str, Any]:
            """
            Converted input tuple object to dict that consul transaction can understand.

            Args:
                v (TxPutKV): input tuple that to be converted refer definition of TxPutKV

            Returns:
                Dict[str, Any]: consul transaction understandable dict contains inout values.
            """
            b64: bytes = b64encode(v.value.encode())
            b64_str = b64.decode()

            if v.cas:
                return {
                    'KV': {
                        'Key': v.key,
                        'Value': b64_str,
                        'Verb': 'cas',
                        'Index': v.cas
                    }
                }
            return {'KV': {'Key': v.key, 'Value': b64_str, 'Verb': 'set'}}

        try:
            self._consul.txn.put([to_payload(i) for i in tx_payload])
        except ClientError as e:
            # If a transaction fails, Consul returns HTTP 409 with the
            # JSON payload describing the reason why the transaction
            # was rejected.
            # The library transforms HTTP 409 into generic ClientException.
            # Unfortunately, we can't easily extract the payload from it.
            raise Exception('Consul transaction failed for putting values in consul KV.') from e
        except (ConsulException, HTTPError, RequestException) as e:
            raise Exception('Failed to put values in consul KV.') from e

    def commit(self):
        """
        In case if _enable_batch_put is set to True
        This function put all the values from local dict to consul store
        through transaction in one call

        Raises:
            Exception: If batch put is not enabled or failed to put key, value in consul
        """
        if not self._enable_batch_put:
            raise Exception("Batch put is not enabled.")
        tx_payload = []
        for key, val in self._payload.items():
            tx_payload.append(TxPutKV(key=key, value=val, cas=None))

        Log.debug(f"putting data in consul, key and values: {tx_payload}")
        self._kv_put_in_transaction(tx_payload)
        self._payload.clear()
