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

from enum import Enum

# Cluster elements supported by system health
class CLUSTERELEMENTS(Enum):
    CLUSTER = "cluster"
    SITE = "site"
    RACK = "rack"
    NODE = "node"

# Health statuses
class HEALTH_STATUSES(Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    STANDBY = "standby"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

# Health event types
class HEALTH_EVENTS(Enum):
    FAULT = "fault"
    FAULT_RESOLVED = "fault_resolved"
    MISSING = "missing"
    INSERTION = "insertion"
    THRESHOLD_BREACHED_LOW = "threshold_breached:low"
    THRESHOLD_BREACHED_HIGH = "threshold_breached:high"
    UNKNOWN = "unknown"

# Health event severities
class EVENT_SEVERITIES(Enum):
    ALERT = "alert"
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFORMATIONAL = "informational"

# Node map attributes
class NODE_MAP_ATTRIBUTES(Enum):
    CLUSTER_ID = "cluster_id"
    SITE_ID = "site_id"
    RACK_ID = "rack_id"
    STORAGESET_ID = "storageset_id"