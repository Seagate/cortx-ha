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
from ha.util.consul_kv_store import ConsulKvStore

class TestConsulKvStore(unittest.TestCase):
    """
    Integration test ConsulKvStore
    """

    def setUp(self):
        """
        Setup consul connection.
        """
        test_ha_prefix = "cortx/ha/"
        self._c1 = ConsulKvStore(test_ha_prefix, host="0.0.0.0", port=8500)
        self._c2 = ConsulKvStore(test_ha_prefix)

    def test_c1(self):
        """
        Test connection c1
        """
        self._c1.delete()
        self._c1.set("res")
        self._c1.set("cluster_name", "cortx_cluster")
        self._c1.set("cluster_user", "hacluster")
        _output: dict = {'cortx/ha/cluster_name': 'cortx_cluster'}
        self.assertEqual(self._c1.get("cluster_name"), _output)
        _output: dict = {'cortx/ha/cluster_name': 'cortx_cluster',
                    'cortx/ha/cluster_user': 'hacluster',
                    'cortx/ha/res': None}
        self.assertEqual(self._c1.get(), _output)
        self._c1.update("cluster_name", "cortx_cluster1")
        self._c1.update("cluster_user", "hacluster1")
        _output: dict = {'cortx/ha/cluster_name': 'cortx_cluster1',
                    'cortx/ha/cluster_user': 'hacluster1',
                    'cortx/ha/res': None}
        self.assertEqual(self._c1.get(), _output)
        self._c1.delete("cluster_name")
        _output: dict = {'cortx/ha/cluster_user': 'hacluster1', 'cortx/ha/res': None}
        self.assertEqual(self._c1.get(), _output)
        self._c1.delete()
        self.assertEqual(self._c1.get(), None)

    def test_c2(self):
        """
        Test connection c2
        """
        self._c2.delete()
        self._c2.set("res")
        self._c2.set("cluster_name", "cortx_cluster")
        self._c2.set("cluster_user", "hacluster")
        _output: dict = {'cortx/ha/cluster_name': 'cortx_cluster'}
        self.assertEqual(self._c2.get("cluster_name"), _output)
        _output: dict = {'cortx/ha/cluster_name': 'cortx_cluster',
                    'cortx/ha/cluster_user': 'hacluster',
                    'cortx/ha/res': None}
        self.assertEqual(self._c2.get(), _output)
        self._c2.update("cluster_name", "cortx_cluster1")
        self._c2.update("cluster_user", "hacluster1")
        _output: dict = {'cortx/ha/cluster_name': 'cortx_cluster1',
                    'cortx/ha/cluster_user': 'hacluster1',
                    'cortx/ha/res': None}
        self.assertEqual(self._c2.get(), _output)
        self._c2.delete("cluster_name")
        _output: dict = {'cortx/ha/cluster_user': 'hacluster1', 'cortx/ha/res': None}
        self.assertEqual(self._c2.get(), _output)
        self._c2.delete()
        self.assertEqual(self._c2.get(), None)

    def tearDown(self):
        """
        Clear all consul key.
        """
        self._c1.delete()
        self._c2.delete()

if __name__ == "__main__":
    unittest.main()