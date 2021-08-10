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
from typing import Callable
from threading import Thread
from cortx.utils.message_bus import MessageBusAdmin
from cortx.utils.message_bus.error import MessageBusError
from cortx.utils.message_bus import MessageProducer
from cortx.utils.message_bus import MessageConsumer

class MessageBusProducer:
    PRODUCER_METHOD = "sync"

    def __init__(self, producer_id: str, message_type: str, partitions: int):
        """
        Register message types with message bus.
        Args:
            producer_id (str): producer id.
            message_types (str): Message type.
            partitions (int, optional): No. of partitions. Defaults to 1.
        Raises:
            MessageBusError: Message bus error.
        """
        self.producer = MessageProducer(producer_id=producer_id, message_type=message_type, method=MessageBusProducer.PRODUCER_METHOD)

    def publish(self, message: any):
        """
        Produce message to message bus.
        Args:
            message (dict): Message.
        """
        if isinstance(message, dict):
            self.producer.send([json.dumps(message)])
        elif isinstance(message, str):
            self.producer.send([message])
        else:
            raise Exception(f"Invalid type of message {message}")

class MessageBusConsumer(Thread):

    def __init__(self, consumer_id: int, consumer_group: str, message_type: str,
                callback: Callable, auto_ack: bool, offset: str):
        """
        Initalize consumer.
        Args:
            consumer_id (int): Consumer ID.
            consumer_group (str): Consumer Group.
            message_type (list): Message Type.
            callback (Callable): function to get message.
            auto_ack (bool, optional): Check auto ack. Defaults to False.
            offset (str, optional): Offset for messages. Defaults to "earliest".
        """
        super(MessageBusConsumer, self).__init__(name=f"{message_type}-{str(consumer_id)}", daemon=True)
        self.callback = callback
        self.consumer = MessageConsumer(consumer_id=str(consumer_id),
                        consumer_group=consumer_group,
                        message_types=[message_type],
                        auto_ack=auto_ack, offset=offset)

    def run(self):
        """
        Overloaded of Thread.
        """
        while True:
            try:
                message = self.consumer.receive(timeout=0)
                self.callback(message)
                self.consumer.ack()
            except Exception as e:
                raise MessageBusError(f"Failed to receive message, error: {e}. Retrying to receive.")

class MessageBus:
    ADMIN_ID = "admin"

    @staticmethod
    def get_consumer(consumer_id: int, consumer_group: str, message_type: str,
                callback: Callable, auto_ack: bool = False, offset: str = "earliest") -> MessageBusConsumer:
        """
        Get consumer.
        Args:
            consumer_id (int): Consumer ID.
            consumer_group (str): Consumer Group.
            message_type (str): Message Type.
            callback (Callable): function to get message.
            auto_ack (bool, optional): Check auto ack. Defaults to False.
            offset (str, optional): Offset for messages. Defaults to "earliest".
        """
        return MessageBusConsumer(consumer_id, consumer_group, message_type, callback, auto_ack, offset)

    @staticmethod
    def get_producer(producer_id: str, message_type: str, partitions: int = 1) -> MessageBusProducer:
        """
        Register message types with message bus. and get Producer.
        Args:
            producer_id (str): producer id.
            message_types (str): Message type.
            partitions (int, optional): No. of partitions. Defaults to 1.
        Raises:
            MessageBusError: Message bus error.
        """
        MessageBus.register(message_type, partitions)
        return MessageBusProducer(producer_id, message_type, partitions)

    @staticmethod
    def register(message_type: str, partitions: int = 1):
        """
        Register message type to message bus.
        Args:
            message_type (str): Message type.
            partitions (int): Number of partition.
        """
        admin = MessageBusAdmin(admin_id=MessageBus.ADMIN_ID)
        if message_type not in admin.list_message_types():
            admin.register_message_type(message_types=[message_type], partitions=partitions)

    @staticmethod
    def deregister(message_type: str):
        """
        Deregister message type to message bus.
        Args:
            message_type (str): Message type.
        """
        admin = MessageBusAdmin(admin_id=MessageBus.ADMIN_ID)
        if message_type not in admin.list_message_types():
            admin.deregister_message_type(message_types=[message_type])
