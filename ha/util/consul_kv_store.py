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
import socket

#TODO: Update set/get/update function to provide blocking and non blocking function
class ConsulKvStore:
    """ Represents a Consul kv Store """

    def __init__(self, prefix: str, host: str="localhost", port: int=8500):
        """
        Consul KV store.

        Args:
            prefix (str): Consul prefix
            host (str): consul host
            port (str): consul port

        Example:
            ConsulKvStore("cortx/ha", host="consul.srv", port=3000)
            ConsulKvStore("cortx/ha")
        Here (localhost:8500) is consul connection and cortx/ha is prefix.
        """
        self._prefix: str = prefix
        self._verify(prefix, host, port)
        self._consul = self._get_connection(prefix, host, port)
        self._consul.kv.put(self._prepare_key(""), None)

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
        if host != "localhost":
            try:
                socket.gethostbyname(host)
                int(port)
            except Exception as e:
                raise Exception(f"Invalid host or port name. Refused connection to {host}. Error: {e}")

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
        _, data = self._consul.kv.get(self._prepare_key(key), recurse=True)
        if data is None:
            return False
        return True

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
        self._verify_data(key)
        self._consul.kv.put(self._prepare_key(key), new_val)
        return new_val

    def get(self, key: str = ""):
        """
        Get values. Default it will return all keys. It is block call,
        will take some time if consul leader is not elected.

        Args:
            key (str): Key.

        Return:
            str: Return dictionary of all key val pair.
        """
        _, data = self._consul.kv.get(self._prepare_key(key), recurse=True)
        if data is None:
            return data
        key_val: dict = {}
        for key in data:
            key_val[key['Key']] = key['Value'].decode("utf-8") if isinstance(key['Value'], bytes) else key['Value']
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
