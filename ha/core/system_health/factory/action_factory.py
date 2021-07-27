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

from ha.core.system_health.handlers.action_handler import ActionHandler, NodeFruPSUActionHandler, \
    NodeFruFanActionHandler, NodeSWActionHandler
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.system_health_exception import InvalidResourceType, HaSystemHealthException

EVENT_ACTION_HANDLERS_MAPPING = {
    "node:fru:psu": NodeFruPSUActionHandler,
    "node:fru:fan": NodeFruFanActionHandler,
    "node:fru:disk": None,
    "node:sensor:temperature": None,
    "node:sensor:voltage": None,
    "node:os:cpu": None,
    "node:os:cpu:core": None,
    "node:os:disk_space": None,
    "node:os:memory_usage": None,
    "node:os:memory": None,
    "node:os:raid_data": None,
    "node:os:raid_integrity": None,
    "node:os:disk": None,
    "node:interface:nw": None,
    "node:interface:nw:cable": None,
    "node:interface:sas": None,
    "node:interface:sas:port": None,
    "node:sw:os:service": NodeSWActionHandler
}


class ActionFactory:

    def __init__(self):
        pass

    @staticmethod
    def get_action_handler(event: HealthEvent, action: list) -> ActionHandler:
        """
        Check event.resource_type and return instance of the mapped action handler class.

        Args:
            event (HealthEvent): HealthEvent object
            action (list): Actions list.

        Returns:
            ActionHandler: return Specific object of ActionHandler like NodeFruPSUActionHandler for node:fru:psu.
        """
        try:
            if event.resource_type in EVENT_ACTION_HANDLERS_MAPPING:
                return EVENT_ACTION_HANDLERS_MAPPING[event.resource_type](event, action)
            else:
                raise InvalidResourceType()
        except InvalidResourceType:
            raise HaSystemHealthException(f"Invalid resource type {event.resource_type} to handle action {action}.")
        except Exception as e:
            raise HaSystemHealthException(f"Exception occurred in action factory to get action handler: {e}")
