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

import json

from ha.core.system_health.model.health_event import HealthEvent
from ha.const import DATASTORE_VERSION

class RecoveryActionEvent:
    """
    Action Event. This class implements an action event object,
    that is delegated to components for taking the action.
    """

    def __init__(self, healthevent: HealthEvent):
        """
        Init method.
        """
        self.version = DATASTORE_VERSION
        self.event_type = healthevent.event_type
        self.event_id = healthevent.event_id
        self.resource_type = healthevent.resource_type
        self.cluster_id = healthevent.cluster_id
        self.site_id = healthevent.site_id
        self.rack_id = healthevent.rack_id
        self.storageset_id = healthevent.storageset_id
        self.node_id = healthevent.node_id
        self.resource_id = healthevent.resource_id
        self.timestamp = healthevent.timestamp
        self.event_specific_info = healthevent.specific_info
        self.namespace = healthevent.namespace
        self.pod_name = healthevent.pod_name

    def __str__(self):
        return json.dumps({
            "version": self.version,
            "event_type": self.event_type,
            "event_id": self.event_id,
            "resource_type": self.resource_type,
            "cluster_id": self.cluster_id,
            "site_id": self.site_id,
            "rack_id": self.rack_id,
            "storageset_id": self.storageset_id,
            "node_id": self.node_id,
            "resource_id": self.resource_id,
            "timestamp": self.timestamp,
            "event_specific_info": self.event_specific_info,
            "namespace": self.namespace,
            "pod_name": self.pod_name
        })
