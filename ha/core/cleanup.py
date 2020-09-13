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
 Description:       Cleanup Event
 ****************************************************************************
"""

import sys

from cortx.utils.schema.conf import Conf
from cortx.utils.ha.dm.decision_monitor import DecisionMonitor

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
