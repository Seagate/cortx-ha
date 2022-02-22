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
class CLUSTER_ELEMENTS(Enum):
    CLUSTER = "cluster"
    SITE = "site"
    RACK = "rack"
    NODE = "node"
    STORAGE_SET = "storageset"
    CVG = "cvg"
    DISK = "disk"

# Health statuses
class HEALTH_STATUSES(Enum):
    STARTING = "starting"
    RECOVERING = "recovering"
    ONLINE = "online"
    DEGRADED = "degraded"
    STANDBY = "standby"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    FAILED = "failed"
    UNKNOWN = "unknown"
    REPAIRING = "repairing"
    REPAIRED = "repaired"
    REBALANCING = "rebalancing"

# Health event types
class HEALTH_EVENTS(Enum):
    FAULT = "fault"
    FAULT_RESOLVED = "fault_resolved"
    MISSING = "missing"
    INSERTION = "insertion"
    RECOVERING = "recovering"
    ONLINE = "online"
    FAILED = "failed"
    DEGRADED = "degraded"
    THRESHOLD_BREACHED_LOW = "threshold_breached:low"
    THRESHOLD_BREACHED_HIGH = "threshold_breached:high"
    UNKNOWN = "unknown"
    REPAIRING = "repairing"
    REPAIRED = "repaired"
    REBALANCING = "rebalancing"

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
    HOST_ID = "host_id"

class HEALTH_EVALUATOR_CLASSES:
    CLASS_MODULE = "ha.core.system_health.health_evaluators"
    ELEMENT_MAP: dict = {
        CLUSTER_ELEMENTS.CLUSTER.value: f"{CLASS_MODULE}.cluster_health_evaluator.ClusterHealthEvaluator",
        CLUSTER_ELEMENTS.SITE.value: f"{CLASS_MODULE}.site_health_evaluator.SiteHealthEvaluator",
        CLUSTER_ELEMENTS.RACK.value: f"{CLASS_MODULE}.rack_health_evaluator.RackHealthEvaluator"
    }

# Confstore key attributes
class CONFSTORE_KEY_ATTRIBUTES(Enum):
    STORAGE_SET_ID = "storage_set_id"

# Health event action in system health
class HEALTH_EVENT_ACTIONS(Enum):
    IGNORE = "ignore"
    UPDATE = "update"
    UPDATEPUBLISH = "updatepublish"
    PUBLISH = "publish"