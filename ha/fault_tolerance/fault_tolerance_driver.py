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

from ha import const
from ha.core.config.config_manager import ConfigManager
from ha.core.event_analyzer.event_analyzerd import EventAnalyzer
from ha.k8s_setup.const import _DELIM


class FaultTolerance:
    """
    Module responsible for consuming messages from message bus,
    further analyzes that event and publishes it if required
    """
    def __init__(self, wait_time=10):
        """Init method"""
        self._wait_time = wait_time
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
        Log.info(f'Received the message from message bus: {message}')
        try:
            EventAnalyzer(message.decode('utf-8'))
        except Exception as err:
            Log.error('Failed to analyze the event')
            return CONSUMER_STATUS.FAILED
        return CONSUMER_STATUS.SUCCESS

    def poll(self):
        """Contineously polls for message bus for k8s_event message type"""
        try:
            self._consumer.start()
            while True:
                # Get alert condition from ALertGenerator. Analyze changes
                # with the help of event analyzer and notify if required
                Log.info('Ready to analyze faults in the system')
                time.sleep(self._wait_time)
        except Exception as exe:
            raise(f'Oops, some issue in the fault tolerance_driver: {exe}')

if __name__ == '__main__':
    fault_tolerance = FaultTolerance()
    fault_tolerance.poll()
