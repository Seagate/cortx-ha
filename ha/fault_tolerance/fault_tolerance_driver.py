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

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from ha.util.message_bus import MessageBus, CONSUMER_STATUS, MessageBusConsumer

from ha.core.config.config_manager import ConfigManager
from ha import const
from ha.k8s_setup.const import _DELIM
from ha.core.event_analyzer.filter.filter import ClusterResourceFilter


class FaultTolerance:
    """
    Module responsible for consuming messages from message bus,
    further analyzes that event and publishes it if required
    """
    def __init__(self, wait_time=10):
        """Init method"""
        self._wait_time = wait_time
        self._cluster_resource_filter = ClusterResourceFilter()
        ConfigManager.init('fault_tolerance')
        Log.info(f'wait time: {self._wait_time}')
        self._consumer = self._get_consumer()

    def _get_consumer(self) -> MessageBusConsumer:
        """
           Returns an object of MessageBusConsumer class which will listen on
           cluster_event message type and callback will be executed
        """
        self._consumer_id = Conf.get(const.HA_GLOBAL_INDEX, f'FAULT_TOLERANCE{_DELIM}consumer_id')
        self._consumer_group = Conf.get(const.HA_GLOBAL_INDEX, f'FAULT_TOLERANCE{_DELIM}consumer_group')
        self._message_type = Conf.get(const.HA_GLOBAL_INDEX, f'FAULT_TOLERANCE{_DELIM}message_type')
        return MessageBus.get_consumer(consumer_id=self._consumer_id, \
                                consumer_group=self._consumer_group, \
                                message_type=self._message_type, \
                                callback=self.process_message)

    def process_message(self, message: str):
        """Callback method for MessageConsumer"""
        Log.debug(f'Received the message from message bus: {message}')
        result = False
        # EventAnalyzer class instantiation is expected.
        # This is not required. This will be called from EventAnalyzer class.
        # But as its not available yet and to check newly added filter functionality,
        # temporarily added this
        result = self._cluster_resource_filter.filter_event(message.decode('utf-8'))
        Log.info(f'Alert required: {result}')
        return CONSUMER_STATUS.SUCCESS

    def poll(self):
        """Contineously polls for message bus for k8s_event message type"""
        try:
            self._consumer.start()
            while True:
                # Get alert from message. Analyze changes
                # with the help of event analyzer filter and publish to message bus
                # if required
                Log.info('Ready to analyze faults in the system')
                time.sleep(self._wait_time)
        except Exception as exe:
            raise(f'Oops, some issue in the fault tolerance_driver: {exe}')

if __name__ == '__main__':
    fault_tolerance = FaultTolerance()
    fault_tolerance.poll()
