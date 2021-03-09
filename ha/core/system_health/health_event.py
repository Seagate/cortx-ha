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

class HealthEvent:
    """
    Health Event. This class implements an event object,
    required by System Health module for updating the health.
    """

    def __init__(self, event_id, event_type, severity, site_id, rack_id, cluster_id, storageset_id,
                 node_id, host_id, resource_type, timestamp, resource_id, specific_info):
        """
        Init method.
        """
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
