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
from ha import const

class HealthEvent:
    """
    Health Event. This class implements an event object,
    required by System Health module for updating the health.
    """

    VERSION = const.DATASTORE_VERSION

    def __init__(self, source: str, event_id: str, event_type: str, severity: str, site_id: int, rack_id: int, cluster_id: str, storageset_id: int,
                 node_id: int, host_id: str, resource_type: str, timestamp: str, resource_id: str, specific_info: dict=None):
        """
        Init method.
        """
        self.source = source
        self.event_id = event_id
        self.event_type = event_type
        self.severity = severity
        self.site_id = site_id
        self.rack_id = rack_id
        self.cluster_id = cluster_id
        self.storageset_id = storageset_id
        self.node_id = node_id
        self.host_id = host_id
        self.resource_type = resource_type
        self.timestamp = timestamp
        self.resource_id = resource_id
        self.specific_info = specific_info

    @staticmethod
    def dict_to_object(event):
        return HealthEvent(
            source = event["source"],
            event_id = event["event_id"],
            event_type = event["event_type"],
            severity = event["severity"],
            site_id = event["site_id"],
            rack_id = event["rack_id"],
            cluster_id = event["cluster_id"],
            storageset_id = event["storageset_id"],
            node_id = event["node_id"],
            host_id = event["host_id"],
            resource_type = event["resource_type"],
            timestamp = event["timestamp"],
            resource_id = event["resource_id"],
            specific_info = event["specific_info"]
        )

    def __str__(self):
        return json.dumps({
            "source": self.source,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "severity": self.severity,
            "site_id": self.site_id,
            "rack_id": self.rack_id,
            "cluster_id": self.cluster_id,
            "storageset_id": self.storageset_id,
            "node_id": self.node_id,
            "host_id": self.host_id,
            "resource_type": self.resource_type,
            "timestamp": self.timestamp,
            "resource_id": self.resource_id,
            "specific_info": self.specific_info
        })
