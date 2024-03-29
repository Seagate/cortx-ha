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

import sys
import json
from cortx.utils.message_bus import MessageConsumer

if __name__ == '__main__':
    message_types = ["alerts", "health_events", "ha_event_test"] \
        if len(sys.argv) == 1 else [sys.argv[1]]
    consumer = MessageConsumer(consumer_id="1",
                                consumer_group='iem_analyzer',
                                message_types=message_types,
                                auto_ack=False, offset='earliest')

    while True:
        try:
            print("In receiver")
            message = consumer.receive(timeout=0)
            msg = json.loads(message.decode('utf-8'))
            print(msg)
            consumer.ack()
        except Exception as e:
            print(e)
            sys.exit(0)