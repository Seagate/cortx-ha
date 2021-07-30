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

from ha.core.action_handler.error import HAActionHandlerError
from ha.core.action_handler.action_handler import ActionHandler, NodeFailureActionHandler, DefaultActionHandler
from ha.core.system_health.model.health_event import HealthEvent

EVENT_ACTION_HANDLERS_MAPPING = {
    "node": NodeFailureActionHandler
}


class ActionFactory:

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
                return EVENT_ACTION_HANDLERS_MAPPING[event.resource_type]()
            else:
                return DefaultActionHandler()
        except Exception as e:
            raise HAActionHandlerError(f"Exception occurred in action factory to get action handler: {e}")
