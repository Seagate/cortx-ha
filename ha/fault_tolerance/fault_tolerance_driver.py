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
import os
import signal

from cortx.utils.log import Log
from ha.core.config.config_manager import ConfigManager
from ha.fault_tolerance.fault_monitor import HealthStatusMonitor
from ha.fault_tolerance.cluster_stop_monitor import ClusterStopMonitor
from ha.fault_tolerance.rest_api import CcRestApi

class FaultTolerance:
    """
    Module responsible for consuming messages from message bus,
    further analyzes that event and publishes it if required
    """
    def __init__(self):
        """
        Init method
        Create monitor objects and Sets the callbacks to sigterm
        """
        signal.signal(signal.SIGTERM, self.set_sigterm)
        ConfigManager.init("fault_tolerance")
        self.node_fault_monitor = HealthStatusMonitor()
        self.cluster_stop_monitor = ClusterStopMonitor()
        CcRestApi.init()

    def set_sigterm(self, signum, frame):
        """
        Callback function to receive a signal
        """
        Log.info(f"Received SIGTERM {signum}")
        Log.debug(f"Stopping the Fault Tolerance Monitor received a signal: {signum} during execution of frame: {frame}")
        self.node_fault_monitor.stop(flush=True)
        self.cluster_stop_monitor.stop(flush=True)

    def start(self):
        """
        start the threads
        """
        self.node_fault_monitor.start()
        self.cluster_stop_monitor.start()
        CcRestApi.start(host=None, port=8080)

    def wait_for_exit(self):
        """
        join and wait for monitor threads to exit
        """
        CcRestApi.join()
        self.node_fault_monitor.join()
        self.cluster_stop_monitor.join()

if __name__ == '__main__':

    fault_tolerance = FaultTolerance()
    Log.info(f"Starting the Fault Tolerance Monitor with PID {os.getpid()}...")
    fault_tolerance.start()
    fault_tolerance.wait_for_exit()
    Log.info(f"The Fault Tolerance Monitor with PID {os.getpid()} stopped successfully.")
