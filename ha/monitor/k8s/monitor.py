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

"""
   Monitoring and processing the Kubernetes events
"""

import os
import signal
from cortx.utils.log import Log

from cortx.utils.conf_store import Conf
from ha.k8s_setup.const import _DELIM
from ha import const
from ha.core.config.config_manager import ConfigManager
from ha.util.message_bus import MessageBus
from ha.util.conf_store import ConftStoreSearch
from ha.monitor.k8s.object_monitor import ObjectMonitor
from ha.monitor.k8s.const import K8SClientConst, K8SEventsConst

class ResourceMonitor:
    """
    Manages the Monitor threads
    """
    def __init__(self, wait_time=10):
        """
        Init method
        Create monitor objects and Sets the callbacks to sigterm
        """
        try:
            # set sigterm handler
            signal.signal(signal.SIGTERM, self.set_sigterm)

            # Read I/O pod selector label from ha.conf . Will be received from provisioner confstore
            # provisioner needs to be informed to add it in confstore  (to be added there )
            ConfigManager.init("k8s_resource_monitor")
            _conf_stor_search = ConftStoreSearch()

            self.monitors = []
            monitor_args = {}

            # event output in pretty format
            monitor_args['watch_args'] = {K8SClientConst.PRETTY : True}

            # Setting a timeout value, 'timeout_seconds', for the stream.
            # timeout value for connection to the server
            # If do not set then we will not able to stop immediately,
            # because synchronous function watch.stream() will not come back
            # until catch any event on which it is waiting.
            monitor_args['watch_args'][K8SClientConst.TIMEOUT_SECONDS] = wait_time

            # Get MessageBus producer object for all monitor threads
            producer = self._get_producer()

            # Change to multiprocessing
            # Creating NODE monitor object
            Log.info("Instantiating monitor for all the nodes in cluster.")
            node_monitor = ObjectMonitor(producer, K8SClientConst.NODE, **monitor_args)
            self.monitors.append(node_monitor)

            _, label_id_map, resource_id_map = _conf_stor_search.get_cluster_cardinality()
            Log.debug(f"label id map: {label_id_map}, resource id map: {resource_id_map}")

            # NOTE: Currently running two pod monitors with the label 'cortx.io/machine-id' and
            #  'statefulset.kubernetes.io/pod-name'. in any deployment, both labels will not co-exist,
            #  so either one pod monitor will not be receiving any events.
            # TODO: CORTX-31875 So once the label 'statefulset.kubernetes.io/pod-name' is available,
            #  the pod monitor with the label 'cortx.io/machine-id' needs to be removed as,
            #  it is running only for backward compatibility.
            # 1. pod monitor for pods with 'cortx.io/machine-id' labels
            if label_id_map:
                Log.info(f"Instantiating monitor for pods with 'cortx.io/machine-id' labels: {label_id_map.keys()}")
                label_ids = ', '.join(label_id for label_id in label_id_map.keys())
                monitor_args['watch_args'][K8SClientConst.LABEL_SELECTOR] = \
                    f'{K8SEventsConst.LABEL_MACHINEID} in ({label_ids})'
                monitor_args['resource_id_map'] = label_id_map
                # Creating POD monitor object watching on label machine id
                pod_monitor_for_machineids = ObjectMonitor(producer, K8SClientConst.POD, **monitor_args)
                self.monitors.append(pod_monitor_for_machineids)
            # 2. pod monitor for pods with 'statefulset.kubernetes.io/pod-name' labels
            elif resource_id_map:
                Log.info(f"Instantiating monitor for pods with names: {resource_id_map.keys()}")
                pod_names = ', '.join(pod_name for pod_name in resource_id_map.keys())
                monitor_args['watch_args'][K8SClientConst.LABEL_SELECTOR] = \
                    f'{K8SEventsConst.LABEL_PODNAME} in ({pod_names})'
                monitor_args['resource_id_map'] = resource_id_map
                # Creating POD monitor object watching on label pod name
                pod_monitor_for_podnames = ObjectMonitor(producer, K8SClientConst.POD, **monitor_args)
                self.monitors.append(pod_monitor_for_podnames)
            else:
                Log.warn(f"No pods found to monitor in resource id map: {resource_id_map}"\
                    " and machine id map {label_id_map} ")

        except Exception as err:
            Log.error(f'Monitor failed to start watchers: {err}')

    def _get_producer(self):
        """
        Get message bus producer
        """
        message_type = Conf.get(const.HA_GLOBAL_INDEX, f"MONITOR{_DELIM}message_type")
        producer_id = Conf.get(const.HA_GLOBAL_INDEX, f"MONITOR{_DELIM}producer_id")
        MessageBus.init()
        Log.info(f"Getting producer {producer_id} for message type: {message_type}")
        return MessageBus.get_producer(producer_id, message_type)

    def set_sigterm(self, signum, frame):
        """
        Callback function to receive a signal
        This sets sigterm in all monitors
        """
        Log.info(f"Received SIGTERM {signum}.")
        for monitor in self.monitors:
            monitor.set_sigterm(signum, frame)

    def start(self):
        """
        start the threads
        """
        for monitor in self.monitors:
            monitor.start()

    def wait_for_exit(self):
        """
        join and wait for all threads to exit
        """
        for monitor in self.monitors:
            monitor.join()

if __name__ == "__main__":
    monitor = ResourceMonitor(K8SClientConst.VAL_WATCH_TIMEOUT_DEFAULT)
    Log.info(f"Starting the k8s Monitor with PID {os.getpid()}...")
    monitor.start()
    monitor.wait_for_exit()
    Log.info(f"K8s Monitor with PID {os.getpid()} stopped successfully.")
