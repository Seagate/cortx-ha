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

class TestMessageBus(unittest.TestCase):
    """
    Integration test TestMessageBus
    """

    def setUp(self):
        """
        Setup.
        """
        self.message_type = "test_ha"
        # Consumer
        self.consumer_id = 1
        self.consumer_group = "test_ha_group"
        # Producer
        producer_id="ha_producer"
        self.producer = MessageBus.get_producer(producer_id=producer_id, message_type=self.message_type)
        self.set_flag = True

    def _callback(self, message: str):
        """
        Callback
        """
        payload = json.loads(message)
        if payload.get("status") == "ok":
            print("Caught message work is done")
            self.set_flag = False
            return True

    def test_safe_close(self):
        """
        Test safe close thread by return true
        """
        consumer = MessageBus.get_consumer(consumer_id=self.consumer_id,
                                            consumer_group=self.consumer_group,
                                            message_type=self.message_type,
                                            callback=self._callback)
        # send message
        self.producer.publish({"status":"ok"})

        # Wait for message
        consumer.start()
        while self.set_flag:
            time.sleep(2)
            consumer.stop()
        print("all work is done stop thread")

    def test_safe_close(self):
        """
        Test force close thread
        """
        pass

    def tearDown(self):
        """
        destroy.
        """
        MessageBus.deregister(self.message_type)

if __name__ == "__main__":
    unittest.main()