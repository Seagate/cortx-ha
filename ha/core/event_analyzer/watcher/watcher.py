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

import time
import json
import traceback
from threading import Thread

from cortx.utils.message_bus import MessageConsumer
from cortx.utils.log import Log

from ha.core.error import EventAnalyzer
from ha.core.event_analyzer.filter.filter import Filter
from ha.core.event_analyzer.parser.parser import Parser
from ha.core.event_analyzer.subscriber import Subscriber

class Watcher(Thread):
    """ Watch message bus to check in coming event. """

    def __init__(self, consumer_id: int, message_type: str, consumer_group: str,
                event_filter: Filter, event_parser: Parser, subscriber: Subscriber):
        """
        Initalize Watcher class to monitor message bus event.

        Args:
            id (int): Consumer ID for message bus.
            message_type (str): Message type for getting event.
            group (str): Consumer Group of message bus.
            event_filter (Filter): Filter unused event.
            parser (Parser): Parse event to HealthEvent
            subscriber (Subscriber): Pass event to Subscriber.
        """
        super(Watcher, self).__init__(name=f"{message_type}-{str(consumer_id)}", daemon=True)
        Log.info(f"Initalizing watcher {message_type}-{str(consumer_id)}")
        self.consumer_id = consumer_id
        self.message_type = message_type
        self.consumer_group = consumer_group
        self.filter = event_filter
        self.parser = event_parser
        self.subscriber = subscriber
        self._validate()
        self.consumer = self._get_connection()

    def _validate(self) -> None:
        """
        Validate watcher and raise exception.

        Raises:
            EventAnalyzer: event analyser exception.
        """
        if not isinstance(self.subscriber, Subscriber):
            raise EventAnalyzer(f"Invaid subscriber {self.subscriber}")

    def _get_connection(self) -> MessageConsumer:
        """
        Get message consumer connection.

        Returns:
            MessageConsumer: Return instance of MessageConsumer.
        """
        return MessageConsumer(consumer_id=str(self.consumer_id),
                                consumer_group=self.consumer_group,
                                message_types=[self.message_type],
                                auto_ack=False, offset='latest')

    def run(self):
        """
        Overloaded of Thread.
        """
        while True:
            try:
                message = self.consumer.receive(timeout=0)
                msg_schema = json.loads(message.decode('utf-8'))
                Log.info(f"Captured message: {msg_schema}")
                if self.filter.filter_event(msg_schema):
                    Log.info(f"Found filtered alert: {msg_schema}")
                    event = self.parser.parse_event(msg_schema)
                    self.subscriber.process_event(event)
                self.consumer.ack()
            except Exception as e:
                Log.error(f"Exception caught: {traceback.format_exc()}, failed to process {msg_schema}")
                Log.error(f"Forcefully ack failed msg: {msg_schema}")
                self.consumer.ack()
