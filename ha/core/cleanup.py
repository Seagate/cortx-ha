#!/usr/bin/env python3

"""
 ****************************************************************************
 Filename:          cleanup.py
 Description:       Cleanup Event

 Creation Date:     07/09/2020
 Author:            Ajay Paratmandali

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2001 - $Date: 2015/01/14 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 ****************************************************************************
"""

import sys

from eos.utils.schema.conf import Conf
from eos.utils.ha.dm.decision_monitor import DecisionMonitor

from ha import const

class Cleanup:
    def __init__(self, args):
        self._args = args
        self._decision_monitor = DecisionMonitor()

    def cleanup_db(self):
        """
        {'entity': 'enclosure', 'entity_id': '0',
        'component': 'controller', 'component_id': 'srvnode-1'}
        """
        resources = Conf.get(const.RESOURCE_GLOBAL_INDEX, "resources")
        for key in resources.keys():
            if self._args.node in key:
                self._decision_monitor.acknowledge_resource(key, True)
