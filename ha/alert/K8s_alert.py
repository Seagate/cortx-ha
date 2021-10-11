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

import json
from ha.const import K8S_ALERT_RESOURCE_TYPE, K8S_ALERT_STATUS


class K8SAlert:
    """
    Alert class
    This class creates an object with the k8s alert data
    """
    # namespace , pod_name will be ignored for RESOURCE_TYPE_NODE
    def __init__(self, namespace: str, node_name: str, pod_name: str, status: K8S_ALERT_STATUS, resource_type: K8S_ALERT_RESOURCE_TYPE, timestamp: str):
        """
        Init method.
        """
        self.namespace = namespace
        self.pod_name = pod_name
        self.node_name = node_name
        self.status = status
        self.resource_type = resource_type
        self.timestamp = timestamp

    def __str__(self):
        return json.dumps({
            "namespace": self.namespace,
            "pod_name": self.pod_name,
            "node_name": self.node_name,
            "status": self.status,
            "resource_type": self.resource_type,
            "timestamp": self.timestamp
        })
