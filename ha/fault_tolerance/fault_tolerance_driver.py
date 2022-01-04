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
import threading

from cortx.utils.log import Log
from ha.const import CORTX_HA_WAIT_TIMEOUT
from ha.core.config.config_manager import ConfigManager
from ha.fault_tolerance.fault_monitor import NodeFaultMonitor
from ha.fault_tolerance.cluster_stop_monitor import ClusterStopMonitor

class FaultTolerance:
    """
    Module responsible for consuming messages from message bus,
    further analyzes that event and publishes it if required
    """
    def __init__(self, wait_time=10):
        """
        Init method
        Create monitor objects and Sets the callbacks to sigterm
        """
        signal.signal(signal.SIGTERM, self.set_sigterm)
        self._wait_time = wait_time
        ConfigManager.init("fault_tolerance")
        self.node_fault_monitor = NodeFaultMonitor()
        self.cluster_stop_monitor = ClusterStopMonitor()
        # self._stop = threading.Event()

    def set_sigterm(self, signum, frame):
        Log.info(f"Received SIGTERM {signum}")
        Log.debug(f"Received signal: {signum} during execution of frame: {frame}")
        Log.info(f"Stopping the Fault Tolerance Monitor...")
        self.node_fault_monitor.stop(flush=True)
        self.cluster_stop_monitor.stop(flush=True)
        # self._stop.set()

    def start(self):
        """
        start the threads
        """
        Log.info("Starting all daemon threads of Fault Tolerance Monitor...")
        self.node_fault_monitor.start()
        self.cluster_stop_monitor.start()
        Log.info(f"Fault Tolerance Monitor with PID {os.getpid()} started successfully.")

    # def poll(self):
    #     """
    #     wait method for receiving events
    #     """
    #     Log.debug("FaultTolerance poll")
    #     try:
    #         while not self._stop.is_set():
    #             # wait on stop event with timeout
    #             self._stop.wait(timeout=self._wait_time)

    #         Log.info(f"Fault Tolerance Monitor with PID {os.getpid()} stopped successfully.")
    #     except Exception as exe:
    #         raise Exception(f'Oops, some issue in the fault tolerance_driver: {exe}')

    def wait_for_exit(self):
        """
        join and wait for monitor threads to exit
        """
        self.node_fault_monitor.join()
        self.cluster_stop_monitor.join()
        Log.info(f"The Health Monitor with PID {os.getpid()} stopped successfully.")

if __name__ == '__main__':

    fault_tolerance = FaultTolerance(wait_time=CORTX_HA_WAIT_TIMEOUT)
    fault_tolerance.start()
    fault_tolerance.wait_for_exit()
