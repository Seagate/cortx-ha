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
from threading import Thread

from cortx.utils.message_bus import MessageConsumer

from ha.core.event_analyzer.filter.filter import Filter
from ha.core.event_analyzer.parser.parser import Parser
from ha.core.event_analyzer.subscriber import Subscriber
import json

class Watcher(Thread):
    """ Watch message bus to check in comming event. """

    def __init__(self, id: int, message_type: str, group: str,
                event_filter: Filter, parser: Parser, subscriber: Subscriber):
        """
        Initalize Watcher class to monitor message bus event.

        Args:
            id (int): Consumer ID for message bus.
            message_type (str): Message type for geeting event.
            group (str): Consumer Group of message bus.
            event_filter (Filter): Filter unused event.
            parser (Parser): Parse event to HealthEvent
            subscriber (Subscriber): Pass event to Subscriber.
        """
        super(Watcher, self).__init__(name=f"{message_type}-{id}", daemon=True)
        self.consumer_id = id
        self.message_type = message_type
        self.consumer_group = group
        self.filter = event_filter
        self.parser = parser
        self.subscriber = subscriber
        self._validate()
        self.consumer = self._get_connection()

    def _validate(self):
        pass

    def _get_connection(self):
        return MessageConsumer(consumer_id=str(self.consumer_id),
            consumer_group=self.consumer_group,
            message_types=[self.message_type], auto_ack=True, offset='latest')

    def run(self):
        while True:
            try:
                message = json.loads(consumer.receive(timeout=0).decode('utf-8'))
                if filter.filter_event(message):
                    event = self.parser.parse_event(message)
                    self.subscriber.process_event(event)
                consumer.ack()
                time.sleep(3)
            except Exception as e:
                pass
