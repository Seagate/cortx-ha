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

# Health statuses
class HEALTH_STATUSES(Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    STANDBY = "standby"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    FAILED = "failed"
    UNKNOWN = "unknown"

# Health event types
class HEALTH_EVENTS(Enum):
    FAULT = "fault"
    FAULT_RESOLVED = "fault_resolved"
    MISSING = "missing"
    INSERTION = "insertion"
    FAILED = "failed"
    ACTIVE = "active"
    INACTIVE = "inactive"
    THRESHOLD_BREACHED_LOW = "threshold_breached:low"
    THRESHOLD_BREACHED_HIGH = "threshold_breached:high"
    # [TBD] support needs to be added for this event type in health event
    DEGRADED = "degraded"
    UNRECOVERABLE = "unrecoverebale"
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


# Mapping HEALTH_EVENTS to the Status data received from Discovery API
RESOURCE_TO_HEALTH_STATUS_MAPPING = {
    "OK" : HEALTH_EVENTS.INSERTION.value,
    "FAULT" : HEALTH_EVENTS.FAULT.value,
    "NONE" : HEALTH_EVENTS.UNKNOWN.value,
    "ACTIVE" : HEALTH_EVENTS.ACTIVE.value,
    "INACTIVE" : HEALTH_EVENTS.INACTIVE.value,
    "FAILED" : HEALTH_EVENTS.FAILED.value,
    "DISABLED/FAILED" : HEALTH_EVENTS.FAILED.value,
    "DEGRADED" : HEALTH_EVENTS.DEGRADED.value,
    "UNRECOVERABLE" : HEALTH_EVENTS.UNRECOVERABLE.value
    #"DEGRADED" : HEALTH_EVENTS.FAULT.value
}

# Constants for getting health data from Discovery module
NODE_HEALTH_RETRY_COUNT = 30
NODE_HEALTH_RETRY_INTERVAL = 2
CMD_GET_MACHINE_ID = "cat /etc/machine-id"

# Mapping to identify the SEVERITY based on EVENT_TYPE
HEALTH_STATUS_TO_EVENT_SEVERITY_MAPPING = {
    "OK" : EVENT_SEVERITIES.INFORMATIONAL.value,
    "ACTIVE" : EVENT_SEVERITIES.INFORMATIONAL.value,
    "INACTIVE" : EVENT_SEVERITIES.WARNING.value,
    "FAULT" : EVENT_SEVERITIES.CRITICAL.value,
    "FAILED" : EVENT_SEVERITIES.ALERT.value,
    "DISABLED/FAILED" : EVENT_SEVERITIES.ALERT.value,
    "NONE" : EVENT_SEVERITIES.INFORMATIONAL.value,
    "DEGRADED" : EVENT_SEVERITIES.ALERT.value,
    "UNRECOVERABLE": EVENT_SEVERITIES.CRITICAL.value
}

# Mapping resource_type received in health view schema to the one in alerts
# Note: If the KV parsing output changes the strings in this mapping will need to be modified
# [TBD] This mapping to be confirmed with SSPL
RESOURCE_TYPE_MAPPING = {
    "node.storage.hw.controller" : "enclosure:hw:controller",
    "node.storage.hw.disk" : "enclosure:hw:disk ",
    "node.storage.hw.fan" : "enclosure:hw:fan",
    "node.storage.hw.psu" : "enclosure:hw:psu",
    "node.storage.hw.sideplane_expander" : "enclosure:hw:sideplane",
    "node.storage.fw.logical_volume" : "enclosure:cortx:logical_volume",
    "node.storage.fw.disk_group" : "enclosure:cortx:disk_group",
    "node.storage.hw.platform_sensor.temperature" : "enclosure:sensor:temperature",
    "node.storage.hw.platform_sensor.voltage" : "enclosure:sensor:voltage",
    "node.storage.hw.platform_sensor.current" : "enclosure:sensor:current",
    "node.storage.hw.sas_port" : "enclosure:interface:sas",
    "node.storage.hw.nw_port" : "enclosure:interface:nw",
    "node.compute.hw.psu" : "node:fru:psu",
    "node.compute.hw.cpu" : "node:os:cpu",
    "node.compute.hw.memory" : "node:os:memory",
    "node.compute.hw.fan" : "node:fru:fan",
    "node.compute.hw.nw_port" : "node:interface:nw",
    "node.compute.hw.sas_hba" : "node:interface:sas",
    "node.compute.hw.sas_port" : "node:interface:sas:port",
    "node.compute.hw.disk" : "node:fru:disk",
    "node.compute.hw.platform_sensor.temperature" : "node:fru:psu",
    "node.compute.hw.platform_sensor.voltage" : "node:fru:psu",
    "node.compute.hw.platform_sensor.current" : "node:fru:psu",
    "node.compute.sw.raid" : "node:os:raid_data",
    "node.compute.sw.cortx_sw_services" : "node:sw:os:service",
    "node.compute.sw.external_sw_services" : "node:sw:os:service",
    "node.compute" : "node",
    "node.storage" : "enclosure"
}
