#!/usr/bin/env python3

# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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

"""
 ****************************************************************************
 Description:       resource_agent resource agent
 ****************************************************************************
"""

from ha.core.config.config_manager import ConfigManager
import os
import json
import consul
import unittest
import time
from datetime import datetime
from unittest.mock import patch

from cortx.utils.log import Log
from cortx.utils.ha.dm.actions import Action
from cortx.utils.ha.dm.decision_monitor import DecisionMonitor

from ha.resource.alert_monitor_resource_agent import HardwareResourceAgent
from ha import const

class TestHardwareResourceAgent(unittest.TestCase):
    """
    Unit test for hardware resource agent
    """

    def setUp(self):
        ConfigManager.init('resource_agent')
        self.ts = int(time.time())
        self.td = datetime.fromtimestamp(self.ts).strftime('%Y-%m-%dT%H:%M:%S.000000+0000')
        with open(const.RESOURCE_SCHEMA, 'r') as f:
            self.schema = json.load(f)
        self.hw_agent = HardwareResourceAgent(DecisionMonitor(), self.schema)
        self.key = "cortx"+const.HA_DELIM+"base"+const.HA_DELIM+"ha"+const.HA_DELIM+"obj"
        self.filename = 'io_path_health_c1'
        self.path = 'io'
        self.local = self.schema['nodes']['local']
        self.consul = consul.Consul()

    def tearDown(self):
        self._remove_data(self.local, True,self.key)
        if os.path.exists(const.HA_INIT_DIR + self.filename):
            os.remove(const.HA_INIT_DIR + self.filename)

    def _get_key(self, node):
        """
        Get ID and key for alert
        """
        alert_id = ''
        hw_resource  = self.schema["resource_groups"][self.path +'_'+ node][0]
        for val in self.schema["resources"][hw_resource].values():
            alert_id = alert_id + val + const.HA_DELIM
        alert_id = alert_id + str(self.ts)
        return self.key + const.HA_DELIM + alert_id, alert_id

    def _get_data(self, node):
        key, alert_id = self._get_key(node)
        index, data = self.consul.kv.get(key)
        Log.debug(f"key: {key}, alert_id: {alert_id}, index: {index}")
        return data

    def _put_data(self, state, node):
        """
        Put data to consul
        Msg:
                cortx>base>ha>obj>node>srvnode-1>nw>mgmt>1589609895
                '{"decision_id": "node>srvnode-1>nw>mgmt>1589609895",
                    "action": "failed",
                    "alert_time": "2020-05-16T06:18:15.000000+0000"
                }'
        """
        key, alert_id = self._get_key(node)
        self.consul.kv.put(key, '{"decision_id": "'+alert_id+ \
            '", "action": "'+state+'", "alert_time": "'+self.td+'"}')

    def _remove_data(self, node, recurse=False, key=None):
        """
        Remove data from consul
        consul kv delete -recurse cortx>base>ha>obj>enclosure
        """
        if key == None:
            key, alert_id = self._get_key(node)
        self.consul.kv.delete(key, recurse)

    @patch('ha.resource.alert_monitor_resource_agent.HardwareResourceAgent.get_env')
    def test_start(self, patched_get_env):
        """
        Test start for hw resource agent

        Arguments:
            patched_get_env {[alert_monitor_resource_agent method]} -- Method for resource agent to get
                pacemaker env data.
        """
        patched_get_env.return_value = {
            'OCF_RESKEY_filename': self.filename,
            'OCF_RESKEY_path': self.path
        }
        # No data in consul
        self._remove_data(self.local)
        status = self.hw_agent.start()
        self.assertEqual(status, const.OCF_SUCCESS)
        # failed state in consul
        self._put_data(Action.FAILED, self.local)
        status = self.hw_agent.start()
        self.assertEqual(status, const.OCF_ERR_GENERIC)
        self._remove_data(self.local)
        # resolved state in consul
        time.sleep(1)
        self._put_data(Action.RESOLVED, self.local)
        status = self.hw_agent.start()
        self.assertEqual(status, const.OCF_SUCCESS)

    @patch('ha.resource.alert_monitor_resource_agent.HardwareResourceAgent.get_env')
    def test_stop(self, patched_get_env):
        """
        Test stop for hw resource agent

        Arguments:
            patched_get_env {[alert_monitor_resource_agent method]} -- Method for resource agent to get
                pacemaker env data.
        """
        patched_get_env.return_value = {
            'OCF_RESKEY_filename': self.filename,
            'OCF_RESKEY_path': 'io'
        }
        # No data in consul
        self._remove_data(self.local)
        status = self.hw_agent.stop()
        self.assertEqual(status, const.OCF_SUCCESS)
        # failed state in consul
        self._put_data(Action.FAILED, self.local)
        status = self.hw_agent.stop()
        self.assertEqual(status, const.OCF_SUCCESS)
        self._remove_data(self.local)
        # resolved state in consul
        time.sleep(1)
        self._put_data(Action.RESOLVED, self.local)
        status = self.hw_agent.stop()
        self.assertEqual(status, const.OCF_SUCCESS)

    @patch('ha.resource.alert_monitor_resource_agent.HardwareResourceAgent.get_env')
    def test_monitor(self, patched_get_env):
        """
        Test monitor for hw resource agent

        Arguments:
            patched_get_env {[alert_monitor_resource_agent method]} -- Method for resource agent to get
                pacemaker env data.
        """
        patched_get_env.return_value = {
            'OCF_RESKEY_filename': self.filename,
            'OCF_RESKEY_path': 'io'
        }
        os.makedirs(const.HA_INIT_DIR, exist_ok=True)
        if os.path.exists(const.HA_INIT_DIR + self.filename):
            os.remove(const.HA_INIT_DIR + self.filename)
        status = self.hw_agent.monitor()
        self.assertEqual(status, const.OCF_NOT_RUNNING)
        if not os.path.exists(const.HA_INIT_DIR + self.filename):
            with open(const.HA_INIT_DIR + self.filename, 'w'): pass
        # No data in consul
        self._remove_data(self.local)
        status = self.hw_agent.monitor()
        self.assertEqual(status, const.OCF_SUCCESS)
        # failed state in consul
        self._put_data(Action.FAILED, self.local)
        status = self.hw_agent.monitor()
        self.assertEqual(status, const.OCF_ERR_GENERIC)
        self._remove_data(self.local)
        # resolved state in consul
        time.sleep(1)
        self._put_data(Action.RESOLVED, self.local)
        status = self.hw_agent.monitor()
        self.assertEqual(status, const.OCF_SUCCESS)

if __name__ == "__main__":
    unittest.main()
