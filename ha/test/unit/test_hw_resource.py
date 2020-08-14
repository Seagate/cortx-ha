#!/usr/bin/env python3

"""
 ****************************************************************************
 Filename:          test_hw_resource.py
 Description:       resource_agent resource agent

 Creation Date:     04/15/2020
 Author:            Ajay Paratmandali

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2020 - $Date: 04/15/2020 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 ****************************************************************************
"""

import os
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from eos.utils.log import Log
from eos.utils.ha.dm.actions import Action
from ha.resource.resource_agent import HardwareResourceAgent
from ha import const

class TestHardwareResourceAgent(unittest.TestCase):
    """
    Unit test for hardware resource agent
    """

    def setUp(self):
        Log.init(service_name='resource_agent', log_path=const.RA_LOG_DIR, level="DEBUG")
        self.decision_monitor = MagicMock()
        self.filename = 'io_path_health_c1'
        self.path = 'io'
        self.decision_monitor.get_resource_group_status.side_effect = self._side_effect_group_status
        self.schama = {
            "nodes": {
                "27534128-7ecd-4606-bf42-ebc9765095ba": "eosnode1.example.com",
                "f3c7d479-2249-40f4-9276-91ba59f50034": "eosnode2.example.com",
                "local": "eosnode1.example.com"
            }
        }
        self.status = None
        self.hw_agent = HardwareResourceAgent(self.decision_monitor, self.schama)

    def tearDown(self):
        if os.path.exists(const.HA_INIT_DIR + self.filename):
            os.remove(const.HA_INIT_DIR + self.filename)

    def _side_effect_group_status(self, key):
        if self.status is None:
            return Action.FAILED if key == self.path+'_'+self.schama['nodes']['local'] else Action.OK
        else:
            return self.status

    @patch('ha.resource.resource_agent.HardwareResourceAgent.get_env')
    def test_start(self, patched_get_env):
        """
        Test start for hw resource agent

        Arguments:
            patched_get_env {[resource_agent method]} -- Method for resource agent to get
                pacemaker env data.
        """
        patched_get_env.return_value = {
            'OCF_RESKEY_filename': self.filename,
            'OCF_RESKEY_path': self.path
        }
        self.status = Action.OK
        status = self.hw_agent.start()
        self.assertEqual(status, const.OCF_SUCCESS)
        self.status = None
        status = self.hw_agent.start()
        self.assertEqual(status, const.OCF_ERR_GENERIC)
        self.status = Action.RESOLVED
        status = self.hw_agent.start()
        self.assertEqual(status, const.OCF_SUCCESS)

    @patch('ha.resource.resource_agent.HardwareResourceAgent.get_env')
    def test_stop(self, patched_get_env):
        """
        Test stop for hw resource agent

        Arguments:
            patched_get_env {[resource_agent method]} -- Method for resource agent to get
                pacemaker env data.
        """
        patched_get_env.return_value = {
            'OCF_RESKEY_filename': self.filename,
            'OCF_RESKEY_path': 'io'
        }
        self.decision_monitor.get_resource_group_status.return_value = Action.FAILED
        status = self.hw_agent.stop()
        self.assertEqual(status, const.OCF_SUCCESS)
        status = self.hw_agent.stop()
        self.assertEqual(status, const.OCF_SUCCESS)

    @patch('ha.resource.resource_agent.HardwareResourceAgent.get_env')
    def test_monitor(self, patched_get_env):
        """
        Test monitor for hw resource agent

        Arguments:
            patched_get_env {[resource_agent method]} -- Method for resource agent to get
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
        self.status = Action.FAILED
        status = self.hw_agent.monitor()
        self.assertEqual(status, const.OCF_SUCCESS)
        self.status = None
        status = self.hw_agent.monitor()
        self.assertEqual(status, const.OCF_ERR_GENERIC)
        self.status = Action.OK
        status = self.hw_agent.monitor()
        self.assertEqual(status, const.OCF_SUCCESS)
        self.status = Action.RESOLVED
        status = self.hw_agent.monitor()
        self.assertEqual(status, const.OCF_SUCCESS)

if __name__ == "__main__":
    unittest.main()