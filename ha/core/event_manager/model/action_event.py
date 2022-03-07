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
from cortx.utils.event_framework.health import HealthAttr, HealthEvent as HEvent

class RecoveryActionEvent:
    """
    Action Event. This class implements an action event object,
    that is delegated to components for taking the action.
    """

    def __init__(self, healthevent: HealthEvent):
        """
        Init method.
        """
        payload = {
            HealthAttr.SOURCE: healthevent.source,
            HealthAttr.CLUSTER_ID: healthevent.cluster_id,
            HealthAttr.SITE_ID: healthevent.site_id,
            HealthAttr.RACK_ID: healthevent.rack_id,
            HealthAttr.STORAGESET_ID: healthevent.storageset_id,
            HealthAttr.NODE_ID: healthevent.node_id,
            HealthAttr.RESOURCE_TYPE: healthevent.resource_type,
            HealthAttr.RESOURCE_ID: healthevent.resource_id,
            HealthAttr.RESOURCE_STATUS: healthevent.event_type,
        }
        self.event = HEvent(**payload)
        self.event.set_specific_info({HealthAttr.SPECIFIC_INFO: healthevent.specific_info})

    def get_event(self):
        return self.event
