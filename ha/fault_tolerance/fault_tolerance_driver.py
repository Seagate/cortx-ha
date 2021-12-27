#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

"""
   Set of periodically executable routines which accepts fault events from
   message bus and takes further action on it
"""


import time

from cortx.utils.log import Log

from ha.core.config.config_manager import ConfigManager
from ha.fault_tolerance.fault_monitor import NodeFaultMonitor
from ha.fault_tolerance.cluster_stop_monitor import ClusterStopMonitor

class FaultTolerance:
    """
    Module responsible for consuming messages from message bus,
    further analyzes that event and publishes it if required
    """
    #def __init__(self, wait_time=600):
    def __init__(self, wait_time=10):
        """Init method"""
        self._wait_time = wait_time
        ConfigManager.init("fault_tolerance")
        self.node_fault_monitor = NodeFaultMonitor()
        self.cluster_stop_monitor = ClusterStopMonitor()

    def start(self):
        self.node_fault_monitor.start()
        self.cluster_stop_monitor.start()

    def poll(self):
        Log.debug("FaultTolerance poll")

        try:
            while True:
                # Get alert condition from ALertGenerator. Analyze changes
                # with the help of event analyzer and notify if required
                time.sleep(self._wait_time)
        except Exception as exe:
            raise(f'Oops, some issue in the fault tolerance_driver: {exe}')

if __name__ == '__main__':

    fault_tolerance = FaultTolerance()
    fault_tolerance.start()
    fault_tolerance.poll()
