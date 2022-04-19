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
from ha.const import HA_DELIM
from ha.util.enum_list import EnumListMeta

class EVENT_MANAGER_KEYS(enum.Enum, metaclass=EnumListMeta):
    MESSAGE_TYPE_VALUE = "ha_event_<component_id>"
    MESSAGE_TYPE_KEY = f"message_type{HA_DELIM}<component_id>"
    SUBSCRIPTION_KEY = f"events{HA_DELIM}subscribe{HA_DELIM}<component_id>"
    EVENT_KEY = f"events{HA_DELIM}<resource>{HA_DELIM}<state>"

ACTION_EVENT_VERSION = "2.0"
EVENT_MANAGER_LOG="event_manager"
EVENT_MGR_PRODUCER_ID = "ha_event_manager_<component_id>"
FUNCTIONAL_TYPE = "functional_type"
