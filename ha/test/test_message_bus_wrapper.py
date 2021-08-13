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

import os
import sys
import pathlib
import unittest
import time
import json
sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))
from ha.util.message_bus import MessageBus
from ha.util.message_bus import CONSUMER_STATUS

class TestMessageBus(unittest.TestCase):
    """
    Integration test TestMessageBus
    """

    def setUp(self):
        """
        Setup.
        """
        self.message_type = "test_ha"
        MessageBus.deregister(self.message_type)
        # Consumer
        self.consumer_id = 1
        self.consumer_group = "test_ha_group"
        # Producer
        producer_id="ha_producer"
        self.producer = MessageBus.get_producer(producer_id=producer_id, message_type=self.message_type)
        self.status = None
        self.stop_thread = False
        self.count = 1
        self.consumer = MessageBus.get_consumer(consumer_id=self.consumer_id,
                                            consumer_group=self.consumer_group,
                                            message_type=self.message_type,
                                            callback=self._callback)

    def _callback(self, message: str):
        """
        Callback
        """
        payload = json.loads(message)
        if self.status == CONSUMER_STATUS.SUCCESS:
            print(f"Caught message {payload}")
            if payload.get("status") == "stop":
                self.stop_thread = True
                return CONSUMER_STATUS.SUCCESS_STOP
            return CONSUMER_STATUS.SUCCESS
        elif self.status == CONSUMER_STATUS.FAILED:
            # Receive same message 3 time and then return fail stop
            if self.count <= 3 and payload.get("status") == "failed":
                print(f"Received same {payload} with count {self.count}")
                self.count += 1
                return CONSUMER_STATUS.FAILED
            elif payload.get("status") == "failed":
                self.stop_thread = True
                print(f"Received same {payload} with count {self.count} stopping forcefully.")
                return CONSUMER_STATUS.FAILED_STOP
            else:
                print(f"Received same {payload} as no responce")
                self.stop_thread = True
                return CONSUMER_STATUS.SUCCESS_STOP

    def test_message_bus(self):
        """
        Test safe close thread by return true
        """
        self._check_success_case()
        self._check_failed_case()

    def _check_success_case(self):
        """
        Return SUCCESS and SUCCESS_STOP
        """
        # send message
        self.producer.publish({"status":"start"})
        self.producer.publish({"status":"working"})
        self.producer.publish({"status":"stop"})

        # Wait for message
        self.status = CONSUMER_STATUS.SUCCESS
        self.consumer.start()
        while not self.stop_thread:
            time.sleep(2)
        self.consumer.stop()
        self.stop_thread = False
        print("Successfully tested SUCCESS and SUCCESS_STOP")

    def _check_failed_case(self):
        self.producer.publish({"status":"failed"})
        self.status = CONSUMER_STATUS.FAILED

        # Wait for message
        self.consumer.start()
        while not self.stop_thread:
            time.sleep(5)
            print("5 sec sleep completed produce one message again")
            self.producer.publish({"status":"no_responce_seen"})
        self.consumer.stop()
        print("Successfully tested SUCCESS and SUCCESS_STOP")

    def tearDown(self):
        """
        destroy.
        """
        MessageBus.deregister(self.message_type)

if __name__ == "__main__":
    unittest.main()