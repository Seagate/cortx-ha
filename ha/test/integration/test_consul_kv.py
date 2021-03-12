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

import os
import sys
import pathlib
import unittest

sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))
from ha.core.config.consul_kv_store import ConsulKvStore

class TestConsulKvStore(unittest.TestCase):
    """
    Integration test ConsulKvStore
    """

    def setUp(self):
        """
        Setup consul connection.
        """
        self._c1 = ConsulKvStore("consul://localhost:8500/cortx/ha/")
        self._c2 = ConsulKvStore("consul:///cortx/ha/")

    def test_c1(self):
        """
        Test connection c1
        """
        self._c1.delete()
        self._c1.set("cluster_name", "cortx_cluster")
        self._c1.set("cluster_user", "hacluster")
        print(self._c1.get("cluster_name"))
        print(self._c1.get())
        self._c1.update("cluster_name", "cortx_cluster1")
        self._c1.update("cluster_user", "hacluster1")
        print(self._c1.get())
        self._c1.delete("cluster_name")
        print(self._c1.get())
        self._c1.delete()
        print(self._c1.get())

    def test_c2(self):
        """
        Test connection c2
        """
        self._c2.delete()
        self._c2.set("cluster_name", "cortx_cluster")
        self._c2.set("cluster_user", "hacluster")
        print(self._c2.get("cluster_name"))
        print(self._c2.get())
        self._c2.update("cluster_name", "cortx_cluster1")
        self._c2.update("cluster_user", "hacluster1")
        print(self._c2.get())
        self._c2.delete("cluster_name")
        print(self._c2.get())
        self._c2.delete()
        print(self._c2.get())

    def tearDown(self):
        """
        Clear all consul key.
        """
        self._c1.delete()
        self._c2.delete()

if __name__ == "__main__":
    unittest.main()