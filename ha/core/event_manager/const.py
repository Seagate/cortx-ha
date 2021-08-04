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

import enum
from ha.util.enum_list import EnumListMeta

class SUBSCRIPTION_LIST(enum.Enum, metaclass=EnumListMeta):
    SSPL = "sspl"
    CSM = "csm"
    S3 = "s3"
    MOTR = "motr"
    HARE = "hare"
    HA = "ha"
    TEST = "test"

class EVENT_MANAGER_KEYS(enum.Enum, metaclass=EnumListMeta):
    MESSAGE_TYPE_VALUE = "ha_event_<component_id>"
    MESSAGE_TYPE_KEY = "message_type/<component_id>"
    SUBSCRIPTION_KEY = "events/subscribe/<component_id>"
    EVENT_KEY = "events/<resource>/<state>"

ACTION_EVENT_VERSION = "2.0"
EVENT_MANAGER_LOG="event_manager"
EVENT_MGR_PRODUCER_ID = "ha_event_manager_<component_id>"
