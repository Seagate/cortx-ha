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

import json
import traceback
from cortx.utils.log import Log
from cortx.utils.iem_framework import EventMessage
from ha.util.message_bus import MessageBus
from ha.util.message_bus import CONSUMER_STATUS
from ha.core.event_analyzer.filter.filter import Filter
from ha.core.event_analyzer.parser.parser import Parser
from ha.core.event_analyzer.subscriber import Subscriber
from ha.core.event_analyzer.event_analyzer_exceptions import InvalidSubscriber
from ha.core.event_analyzer.event_analyzer_exceptions import EventFilterException
from ha.core.event_analyzer.event_analyzer_exceptions import EventParserException
from ha.core.event_analyzer.event_analyzer_exceptions import SubscriberException

class Watcher:
    """ Watch message bus to check in coming event. """

    def __init__(self, consumer_id: int, message_type: str, consumer_group: str,
                event_filter: Filter, event_parser: Parser, subscriber: Subscriber):
        """
        Initalize Watcher class to monitor message bus event.
        Args:
            consumer_id (int): Consumer ID for message bus.
            message_type (str): Message type for getting event.
            consumer_group (str): Consumer Group of message bus.
            event_filter (Filter): Filter unused event.
            event_parser (Parser): Parse event to HealthEvent
            subscriber (Subscriber): Pass event to Subscriber.
        """
        Log.info(f"Initalizing watcher {message_type}-{str(consumer_id)}")
        self.consumer_id = consumer_id
        self.message_type = message_type
        self.consumer_group = consumer_group
        self.filter = event_filter
        self.parser = event_parser
        self.subscriber = subscriber
        self._validate()
        #self.consumer = MessageBus.get_consumer(consumer_id=str(self.consumer_id),
        #                        consumer_group=self.consumer_group,
        #                        message_type=self.message_type,
        #                        callback=self.process_message)

    def _validate(self) -> None:
        """
        Validate watcher and raise exception.
        Raises:
            EventAnalyzer: event analyzer exception.
        """
        if not isinstance(self.subscriber, Subscriber):
            raise InvalidSubscriber(f"Invalid subscriber {self.subscriber}")

    def process_message(self, message: str) -> None:
        """
        Callback function to get message.
        Args:
            message (str): Message received from message bus.
        """
        #try:
        #    message = json.loads(message.decode('utf-8'))
        #except Exception as e:
        #    Log.error(f"Invalid message {message}, sollow exception and ack it. Error: {e}")
        #    return CONSUMER_STATUS.SUCCESS
        try:
            Log.debug(f"Captured message: {message}")
            Log.error(f"Captured message: {message}")
            if self.filter.filter_event(message):
                Log.info(f"Filtered Event detected: {message}")
                event = self.parser.parse_event(message)
                try:
                    Log.info(f"Processing event {event} to subscriber...")
                    self.subscriber.process_event(event)
                except Exception as e:
                    raise SubscriberException(f"Failed to process event {message}. Error: {e}")
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

    def start(self):
        """
        Start watcher to listen messages.
        """
        self.consumer.start()

