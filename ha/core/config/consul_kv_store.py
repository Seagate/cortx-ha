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

import consul
import errno
import socket
from urllib.parse import urlparse

class ConsulKvStore:
    """ Represents a Consul kv Store """

    name = "consul"
    version = "/v1"

    def __init__(self, url: str):
        """
        Consul KV store.

        Args:
            url (str): Consul url with prefix

        Example:
            ConsulKvStore("consul://localhost:8500/cortx/ha/system/config")
            ConsulKvStore("consul:///v1/cortx/ha/system/config")
        Here localhost:8500 is connection and cortx/ha/system/config is prefix.
        """
        url_spec = urlparse(url)
        store_type = url_spec.scheme
        store_loc = url_spec.netloc
        store_path = url_spec.path
        self._prefix: str = None
        self._verify(store_type=store_type, store_loc=store_loc, store_path=store_path)
        self._consul = self._get_connection(store_loc=store_loc, store_path=store_path)
        self._consul.kv.put(self._prepare_key(""), None)

    def _verify(self, store_type: str, store_loc: str, store_path: str):
        """
        Verify connection detail.

        Args:
            store_type (str): Type of connection or DB name.
            store_loc (str): Connection detail like host and port.
            store_path (str): Prefix for connection.
        """
        if store_type != ConsulKvStore.name:
            raise Exception(f"Invalid storage type {store_type}. Correct one is {ConsulKvStore.name}")
        if store_path == "":
            raise Exception("Invalid prefix. It cannot be empty.")
        if store_loc != "":
            try:
                socket.gethostbyname(store_loc.split(":")[0])
                int(store_loc.split(":")[1])
            except Exception as e:
                raise Exception(f"Invalid host or port name. Refused connection to {store_loc}. Error: {e}")

    def _get_connection(self, store_loc: str, store_path: str):
        """
        Prepare consul connection.

        Args:
            store_type (str): Type of connection or DB name.
            store_loc (str): Connection detail like host and port.
            store_path (str): Prefix for connection.

        Return:
            Object: Consul object.
        """
        self._prefix = ConsulKvStore.version + store_path
        if store_loc == "":
            return consul.Consul()
        host: str = store_loc.split(":")[0]
        port: int = int(store_loc.split(":")[1])
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
        key: list = [x for x in self._prefix.split("/") + key.split("/") if x != ""]
        return "/".join(key)

    def key_exists(self, key: str):
        """
        Check if key exists.

        Args:
            key (str): Consul Key.

        Return:
            bool: True if key exists else False.
        """
        index, data = self._consul.kv.get(self._prepare_key(key), recurse=True)
        if data is None:
            return False
        return True

    def set(self, key: str, val: str):
        """
        Set key-val pair in consul. If key already exists return exception.

        Args:
            key (str): Key.
            val (str): Value.

        Return:
            str: Return value.
        """
        self._verify_data(key, val)
        if self.key_exists(key):
            raise Exception(f"Key {key} already exists in kv store.")
        self._consul.kv.put(self._prepare_key(key), val)
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
        self._verify_data(key, new_val)
        self._consul.kv.put(self._prepare_key(key), new_val)
        return new_val

    def get(self, key: str = ""):
        """
        Get values. Default it will return all keys.

        Args:
            key (str): Key.

        Return:
            str: Return dictionary of all key val pair.
        """
        index, data = self._consul.kv.get(self._prepare_key(key), recurse=True)
        if data is None:
            return data
        key_val: dict = {}
        for key in data:
            key_val[key['Key']] = key['Value'].decode("utf-8") if type(key['Value']) is bytes else key['Value']
        return key_val

    def delete(self, key: str = ""):
        """
        Delete values. Default it will delete all keys.

        Args:
            key (str): Key.

        Return:
            str: Return dictionary of all key val pair.
        """
        data = self.get(key)
        self._consul.kv.delete(self._prepare_key(key), recurse=True)
        return data
