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


"""
Receiver script for IEMs created and sent by HA
"""

import sys
import json
import traceback

from cortx.utils.message_bus import MessageConsumer

if __name__ == '__main__':
    consumer = MessageConsumer(consumer_id="1",
                                consumer_group='HA',
                                message_types=["IEM"],
                                auto_ack=False, offset='earliest')

    while True:
        try:
            print("In receiver")
            message = consumer.receive(timeout=0)

            msg = json.loads(message.decode('utf-8'))
            print(f"Got a request: \n {msg} \n")
            consumer.ack()

        except Exception as e:
            print(e)
            print(traceback.format_exe())
            sys.exit(0)

