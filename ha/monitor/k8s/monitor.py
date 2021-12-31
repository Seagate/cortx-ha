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

import signal

from ha.util.message_bus import MessageBus
from ha.monitor.k8s.object_monitor import ObjectMonitor
from ha.monitor.k8s.const import K8SClientConst

from cortx.utils.conf_store import Conf
from ha.k8s_setup.const import _DELIM
from ha import const
from ha.core.config.config_manager import ConfigManager

class ResourceMonitor:
    """
    Manages the Monitor threads
    """
    def __init__(self, wait_time=10):
        """
        Init method
        Create monitor objects and Sets the callbacks to sigterm
        """
        # set sigterm handler
        signal.signal(signal.SIGTERM, self.set_sigterm)

        # Read I/O pod selector label from ha.conf . Will be received from provisioner confstore
        # provisioner needs to be informed to add it in confstore  (to be added there )
        ConfigManager.init("k8s_resource_monitor")

        # event output in pretty format
        kwargs = {K8SClientConst.PRETTY : True}

        # Seting a timeout value, 'timout_seconds', for the stream.
        # timeout value for connection to the server
        # If do not set then we will not able to stop immediately,
        # becuase synchronus function watch.stream() will not come back
        # until catch any event on which it is waiting.
        kwargs[K8SClientConst.TIMEOUT_SECONDS] = K8SClientConst.VAL_WATCH_TIMEOUT_DEFAULT

        # Get MessageBus producer object for all monitor threads
        producer = self._get_producer()

        # Change to multiprocessing
        # Creating NODE monitor object
        self.node_monitor = ObjectMonitor(producer, K8SClientConst.NODE, **kwargs)

        pod_labels = Conf.get(const.HA_GLOBAL_INDEX, "data_pod_label")
        pod_label_str = ', '.join(pod_label for pod_label in pod_labels)
        # TODO : Change 'name' field to 'app' in label_selector if required.
        kwargs[K8SClientConst.LABEL_SELECTOR] = f'name in ({pod_label_str})'

        # Creating POD monitor object
        self.pod_monitor = ObjectMonitor(producer, K8SClientConst.POD, **kwargs)

    def _get_producer(self):
        message_type = Conf.get(const.HA_GLOBAL_INDEX, f"MONITOR{_DELIM}message_type")
        producer_id = Conf.get(const.HA_GLOBAL_INDEX, f"MONITOR{_DELIM}producer_id")
        MessageBus.init()
        return MessageBus.get_producer(producer_id, message_type)

    def set_sigterm(self, signum, frame):
        self.node_monitor.set_sigterm(signum, frame)
        self.pod_monitor.set_sigterm(signum, frame)

    def start(self):
        """
        start the threads
        """
        self.node_monitor.start()
        self.pod_monitor.start()

    def wait_for_exit(self):
        """
        join and wait for all threads to exit
        """
        self.node_monitor.join()
        self.pod_monitor.join()


if __name__ == "__main__":
    monitor = ResourceMonitor()

    monitor.start()

    monitor.wait_for_exit()
    print("k8s monitor is exiting .")
