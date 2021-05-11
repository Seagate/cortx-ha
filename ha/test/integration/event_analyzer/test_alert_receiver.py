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
from cortx.utils.message_bus import MessageConsumer
from cortx.utils.message_bus import MessageBusAdmin
from cortx.utils.message_bus.error import MessageBusError
from cortx.utils.conf_store import Conf, ConfStore
import json
import time

MESSAGE_TYPE=["Alerts"]

if __name__ == '__main__':
    try:
        admin = MessageBusAdmin(admin_id="admin")
    except MessageBusError as e:
        print("\n\n\n\n" + e.desc + "\n\n\n\n")
        if "ALREADY_EXISTS" not in e.desc:
            raise e

    consumer = MessageConsumer(consumer_id="1", consumer_group='ha_event_analyzer', message_types=MESSAGE_TYPE, auto_ack=True, offset='latest')

    while True:
        try:
            message = consumer.receive(timeout=0)
            # consumer receives the messages
            print(message)
            # To convert the message into required format
            #print(json.loads(message.decode('utf-8')))
            print("In receiver")
            consumer.ack()
            time.sleep(3)
        except Exception as e:
            pass
            #print(e)
            #sys.exit(0)