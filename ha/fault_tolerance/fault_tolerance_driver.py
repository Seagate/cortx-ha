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
from cortx.utils.message_bus import MessageConsumer

from ha.core.config.config_manager import ConfigManager
from ha import const
from ha.k8s_setup.const import _DELIM
from ha.core.event_analyzer.filter.filter import K8SFilter


class FaultTolerant:
    """
    Module responsible for consuming messages from message bus,
    further analyzes that event and publishes it if required
    """
    def __init__(self, poll_time=10):
        """Init method"""
        self._poll_time = poll_time
        ConfigManager.init('fault_tolerance_driver')
        self._message_type = Conf.get(const.HA_GLOBAL_INDEX, f'MONITOR{_DELIM}message_type')
        self._consumer = MessageConsumer(consumer_id='1', consumer_group='consumer-group', \
                                   message_types=[self._message_type], auto_ack=True, \
                                   offset='latest')
        Log.info(f'poll time: {self._poll_time}')

    def poll(self):
        """Contineously polls for message bus for k8s_event message type"""
        try:
            while True:
                # Get alert from message. Analyze changes
                # with the help of event analyzer filter and publish to message bus
                # if required
                Log.info('Ready to analyze faults in the system')
                message = self._consumer.receive(timeout=0)
                Log.debug(f'Received the message from message bus: {message}')
                K8SFilter.filter_event(json.dumps(message.__dict__))
                Log.error(f'Received the message from message bus: {message}')
                time.sleep(self._poll_time)
        except Exception as exe:
            raise(f'Oops, some issue in the fault tolerance_driver: {exe}')

if __name__ == '__main__':
    fault_tolerance = FaultTolerant()
    fault_tolerance.poll()
