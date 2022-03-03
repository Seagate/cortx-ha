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

from ha.core.system_health.model.health_event import HealthEvent
from ha.fault_tolerance.event import Event
from ha.fault_tolerance.const import HEALTH_ATTRIBUTES

class RecoveryActionEvent:
    """
    Action Event. This class implements an action event object,
    that is delegated to components for taking the action.
    """

    def __init__(self, healthevent: HealthEvent):
        """
        Init method.
        """
        self.event = Event()
        payload = {
            HEALTH_ATTRIBUTES.SOURCE.value : healthevent.source,
            HEALTH_ATTRIBUTES.CLUSTER_ID.value : healthevent.cluster_id,
            HEALTH_ATTRIBUTES.SITE_ID.value : healthevent.site_id,
            HEALTH_ATTRIBUTES.RACK_ID.value : healthevent.rack_id,
            HEALTH_ATTRIBUTES.STORAGESET_ID.value : healthevent.storageset_id,
            HEALTH_ATTRIBUTES.NODE_ID.value : healthevent.node_id,
            HEALTH_ATTRIBUTES.RESOURCE_TYPE.value : healthevent.resource_type,
            HEALTH_ATTRIBUTES.RESOURCE_ID.value : healthevent.resource_id,
            HEALTH_ATTRIBUTES.RESOURCE_STATUS.value : healthevent.event_type,
            HEALTH_ATTRIBUTES.SPECIFIC_INFO.value : healthevent.specific_info,
        }
        self.event.set_payload(payload)

    def get_event(self):
        return self.event
