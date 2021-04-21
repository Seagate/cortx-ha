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
from cortx.utils.message_bus import MessageProducer
from cortx.utils.message_bus import MessageBusAdmin
sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))

MESSAGE_TYPE="alerts"

if __name__ == '__main__':
    admin = MessageBusAdmin(admin_id='admin')
    message_type_list = admin.list_message_types()
    if MESSAGE_TYPE not in message_type_list:
        admin.register_message_type(message_types=[MESSAGE_TYPE], partitions = 1)

    producer = MessageProducer(producer_id="sspl_sensor", message_type="alerts")
    message_list = ["This is test message 1",   "This is test message 2"]
    producer.send(message_list)
