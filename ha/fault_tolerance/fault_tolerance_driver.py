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
import traceback

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from ha.util.message_bus import MessageBus, CONSUMER_STATUS, MessageBusConsumer

from ha import const
from ha.core.config.config_manager import ConfigManager
from ha.core.event_analyzer.event_analyzerd import EventAnalyzer
from ha.k8s_setup.const import _DELIM

from consul.base import ConsulException
from cortx.utils.conf_store.error import ConfError
from ha.core.event_analyzer.event_analyzer_exceptions import EventFilterException
from ha.core.event_analyzer.event_analyzer_exceptions import EventParserException
from ha.core.event_analyzer.event_analyzer_exceptions import SubscriberException

class FaultTolerance:
    """
    Module responsible for consuming messages from message bus,
    further analyzes that event and publishes it if required
    """
    def __init__(self, wait_time=10):
        """Init method"""
        self._wait_time = wait_time
        ConfigManager.init("fault_tolerance")
        self._consumer = self._get_consumer()

    def _get_consumer(self) -> MessageBusConsumer:
        """
           Returns an object of MessageBusConsumer class which will listen on
           cluster_event message type and callback will be executed
        """
        self._consumer_id = Conf.get(const.HA_GLOBAL_INDEX, f'FAULT_TOLERANCE{_DELIM}consumer_id')
        self._consumer_group = Conf.get(const.HA_GLOBAL_INDEX, f'FAULT_TOLERANCE{_DELIM}consumer_group')
        self._message_type = Conf.get(const.HA_GLOBAL_INDEX, f'FAULT_TOLERANCE{_DELIM}message_type')
        MessageBus.init()
        return MessageBus.get_consumer(consumer_id=self._consumer_id, \
                                consumer_group=self._consumer_group, \
                                message_type=self._message_type, \
                                callback=self.process_message)

    def process_message(self, message: str):
        """Callback method for MessageConsumer"""
        Log.debug(f'Received the message from message bus: {message}')
        try:
            EventAnalyzer(message.decode('utf-8'))
            return CONSUMER_STATUS.SUCCESS
        except ConsulException as e:
            Log.error(f"consule exception {e} {traceback.format_exc()} for {message}. Ack Message.")
            return CONSUMER_STATUS.SUCCESS
        except ConfError as e:
            Log.error(f"config exception {e} {traceback.format_exc()} for {message}. Ack Message.")
            return CONSUMER_STATUS.SUCCESS
        except EventFilterException as e:
            Log.error(f"Filter exception {e} {traceback.format_exc()} for {message}. Ack Message.")
            return CONSUMER_STATUS.SUCCESS
        except EventParserException as e:
            Log.error(f"Parser exception {e} {traceback.format_exc()} for {message}.  Ack Message.")
            return CONSUMER_STATUS.SUCCESS
        except SubscriberException as e:
            Log.error(f"Subscriber exception {e} {traceback.format_exc()} for {message}, retry without ack.")
            return CONSUMER_STATUS.FAILED
        except Exception as e:
            Log.error(f"Unknown Exception caught {e} {traceback.format_exc()}")
            Log.error(f"Forcefully ack failed msg: {message}")
            return CONSUMER_STATUS.FAILED

    def poll(self):
        """Contineously polls for message bus for k8s_event message type"""
        try:
            Log.info(f'Starting poll for fault tolerance alterts with consumer id: {self._consumer_id}.')
            self._consumer.start()
            while True:
                # Get alert condition from ALertGenerator. Analyze changes
                # with the help of event analyzer and notify if required
                time.sleep(self._wait_time)
        except Exception as exe:
            raise(f'Oops, some issue in the fault tolerance_driver: {exe}')

if __name__ == '__main__':
    fault_tolerance = FaultTolerance()
    fault_tolerance.poll()
