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
from ha.alert.K8s_alert import K8SAlert


class RecoveryActionEvent:
    """
    Action Event. This class implements an action event object,
    that is delegated to components for taking the action.
    """

    def __init__(self, k8s_event: K8SAlert):
        """
        Init method.
        """
        self.version = "v1"
        self.event_type = k8s_event.status
        self.event_id = "id1"
        self.resource_type = k8s_event.resource_type
        self.cluster_id = "1"
        self.site_id = "1"
        self.rack_id = "1"
        self.storageset_id = "1"
        self.node_id = k8s_event.node_name
        self.resource_id = k8s_event.pod_name
        self.timestamp = k8s_event.timestamp
        self.event_specific_info = None
        self.namespace = k8s_event.namespace
        self.pod_name = k8s_event.pod_name
        self.status = k8s_event.status

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
            "pod_name": self.pod_name,
            "status": self.status
        })
