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
from cortx.utils.health.event import Event
from cortx.utils.health.const import HEALTH_EVENT_ATTRIBUTES

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
            HEALTH_EVENT_ATTRIBUTES.SOURCE : healthevent.source,
            HEALTH_EVENT_ATTRIBUTES.CLUSTER_ID : healthevent.cluster_id,
            HEALTH_EVENT_ATTRIBUTES.SITE_ID : healthevent.site_id,
            HEALTH_EVENT_ATTRIBUTES.RACK_ID : healthevent.rack_id,
            HEALTH_EVENT_ATTRIBUTES.STORAGESET_ID : healthevent.storageset_id,
            HEALTH_EVENT_ATTRIBUTES.NODE_ID : healthevent.node_id,
            HEALTH_EVENT_ATTRIBUTES.RESOURCE_TYPE : healthevent.resource_type,
            HEALTH_EVENT_ATTRIBUTES.RESOURCE_ID : healthevent.resource_id,
            HEALTH_EVENT_ATTRIBUTES.RESOURCE_STATUS : healthevent.event_type,
            HEALTH_EVENT_ATTRIBUTES.SPECIFIC_INFO : healthevent.specific_info,
        }
        self.event.set_payload(payload)

    def get_event(self):
        return self.event
