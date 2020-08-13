#!/usr/bin/env python3

"""
 ****************************************************************************
 Filename:          cleanup.py
 Description:       Cleanup Event

 Creation Date:     07/09/2020
 Author:            Ajay Paratmandali

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2020 - $Date: 07/09/2020 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 ****************************************************************************
"""

import sys

from eos.utils.schema.conf import Conf
from eos.utils.log import Log

from ha import const
from ha.utility.process import Process

class Cleanup:
    def __init__(self, decision_monitor):
        """
        Generic Cleanup class to reset fail resources.
        """
        self._decision_monitor = decision_monitor

class PcsCleanup(Cleanup):
    def __init__(self, decision_monitor):
        """
        Pcs Cleanup initialization
        """
        super(PcsCleanup, self).__init__(decision_monitor)

    def cleanup_db(self, node):
        """
        {'entity': 'enclosure', 'entity_id': '0',
        'component': 'controller', 'component_id': 'srvnode-1'}
        """
        resources = Conf.get(const.RESOURCE_GLOBAL_INDEX, "resources")
        for key in resources.keys():
            if node in key:
                self._decision_monitor.acknowledge_resource(key, True)

    def resource_reset(self, node=None):
        """
        Cleanup all history/failcount for resource
        Command: pcs resource cleanup <node-name>
        if node is not given it will do cleanup for all node.
        """
        Log.debug(f"Reset failcount of all resource for {node}")
        cmd = const.PCS_CLEANUP if node is None else f"{const.PCS_CLEANUP} --node {node}"
        Process._run_cmd(cmd)
