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
Handler for handling events received from k8s monitor service
"""


import traceback
from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from ha.util.message_bus import MessageBus, CONSUMER_STATUS, MessageBusConsumer
from ha import const
from ha.core.event_analyzer.event_analyzerd import EventAnalyzer
from ha.k8s_setup.const import _DELIM

from consul.base import ConsulException
from cortx.utils.conf_store.error import ConfError
from ha.core.event_analyzer.event_analyzer_exceptions import EventFilterException
from ha.core.event_analyzer.event_analyzer_exceptions import EventParserException
from ha.core.event_analyzer.event_analyzer_exceptions import SubscriberException

class FaultMonitor:
    """
    Base class for all faults received from k8s monitor
    Faults can be for host, node, container, pvc etc
    Seperate derived class to be written for each of the above modules as and when required
    """

    def __init__(self):
        """Init method"""
        self._consumer = self._get_consumer()

    def start(self):
        """
        Start to listen messages.
        """
        if self._consumer is not None:
            self._consumer.start()
        else:
            Log.warn(f"Consumer not found for message type  {self._message_type} ")

class NodeFaultMonitor(FaultMonitor):
    """
    Module responsible for:
    -  consuming node messages from k8s monitor that come on message bus
    -  analyzing the message and and publishing alert if required
    """
    def __init__(self):
        """Init method"""
        super().__init__()

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
            return CONSUMER_STATUS.SUCCESS
        except Exception as e:
            Log.error(f"Unknown Exception caught {e} {traceback.format_exc()}")
            Log.error(f"Forcefully ack as success. msg: {message}")
            return CONSUMER_STATUS.SUCCESS

