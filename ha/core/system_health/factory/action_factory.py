#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

from ha.core.system_health.handlers.action_handler import NodeActionHandler
from ha.core.system_health.system_health_exception import InvalidResourceType
from ha.core.system_health.model.health_event import HealthEvent

EVENT_ACTION_HANDLERS_MAPPING = {
    "node:fru:psu": NodeActionHandler,
    "node:fru:fan": NodeActionHandler,
    "node:fru:disk": NodeActionHandler,
    "node:sensor:temperature": NodeActionHandler,
    "node:sensor:voltage": NodeActionHandler,
    "node:os:cpu": NodeActionHandler,
    "node:os:cpu:core": NodeActionHandler,
    "node:os:disk_space": NodeActionHandler,
    "node:os:memory_usage": NodeActionHandler,
    "node:os:memory": NodeActionHandler,
    "node:os:raid_data": NodeActionHandler,
    "node:os:raid_integrity": NodeActionHandler,
    "node:os:disk": NodeActionHandler,
    "node:interface:nw": NodeActionHandler,
    "node:interface:nw:cable": NodeActionHandler,
    "node:interface:sas": NodeActionHandler,
    "node:interface:sas:port": NodeActionHandler,
    "node:sw:os:service": NodeActionHandler
}


class ActionFactory:

    def __init__(self):
        pass

    @staticmethod
    def get_action_handler(event: HealthEvent, action: list):
        """
        Check event.resource_type and return instance of the mapped action handler class.

        Args:
            action (list): Actions list.

        Returns:
            str: Message.
        """
        if event.resource_type in EVENT_ACTION_HANDLERS_MAPPING:
            return EVENT_ACTION_HANDLERS_MAPPING[event.resource_type](event, action)
        else:
            raise InvalidResourceType()
