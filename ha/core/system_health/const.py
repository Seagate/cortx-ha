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
    THRESHOLD_BREACHED_LOW = "threshold_breached:low"
    THRESHOLD_BREACHED_HIGH = "threshold_breached:high"
    # [TBD] support needs to be added for this event type in health event
    DEGRADED = "degraded"
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
    # [TBD] To be enabled once support for "degraded" is avilable in HEALTH_EVENTS
    #"DEGRADED" : HEALTH_EVENTS.DEGRADED.value
    "DEGRADED" : HEALTH_EVENTS.FAULT.value
}

# Constants for getting health data from Discovery module
NODE_HEALTH_RETRY_COUNT = 10
NODE_HEALTH_RETRY_INTERVAL = 2
CMD_GET_MACHINE_ID = "cat /etc/machine-id"

# Mapping to identify the SEVERITY based on EVENT_TYPE
HEALTH_STATUS_TO_EVENT_SEVERITY_MAPPING = {
    "OK" : EVENT_SEVERITIES.INFORMATIONAL.value,
    "FAULT" : EVENT_SEVERITIES.CRITICAL.value,
    "NONE" : EVENT_SEVERITIES.INFORMATIONAL.value,
    "DEGRADED" : EVENT_SEVERITIES.ALERT.value
}

# Mapping resource_type received in health view schema to the one in alerts
# Note: If the KV parsing output changes the strings in this mapping will need to be modified
# [TBD] This mapping to be confirmed with SSPL
RESOURCE_TYPE_MAPPING = {
    "storage_nodes.hw.controllers" : "enclosure:hw:controller",
    "storage_nodes.hw.disks" : "enclosure:hw:disk ",
    "storage_nodes.hw.fanmodules" : "enclosure:hw:fan",
    "storage_nodes.hw.psus" : "enclosure:hw:psu",
    "storage_nodes.hw.sideplane_expander" : "enclosure:hw:sideplane",
    "storage_nodes.fw.logical_volumes" : "enclosure:cortx:logical_volume",
    "storage_nodes.fw.disk_groups" : "enclosure:cortx:disk_group",
    "storage_nodes.hw.platform_sensors.temperature_sensors" : "enclosure:sensor:temperature",
    "storage_nodes.hw.platform_sensors.voltage_sensors" : "enclosure:sensor:voltage",
    "storage_nodes.hw.platform_sensors.current_sensors" : "enclosure:sensor:current",
    "storage_nodes.hw.sas_ports" : "enclosure:interface:sas",
    "compute_nodes.hw.psus" : "node:fru:psu",
    "compute_nodes.hw.fans" : "node:fru:fan",
    "compute_nodes.hw.disks" : "node:fru:disk",
    "compute_nodes.hw.platform_sensors.temperature_sensors" : "node:sensor:temperature",
    "compute_nodes.hw.platform_sensors.voltage_sensors" : "node:sensor:voltage",
    # [TBD] this mapping should be corrected once input is received from SSPL
    "compute_nodes.hw.platform_sensors.current_sensors" : "node",
    "compute_nodes.hw.cpu" : "node:os:cpu",
    "compute_nodes.hw.memory" : "node:os:memory",
    "compute_nodes.sw.os.raid_array" : "node:os:raid_data",
    "compute_nodes.hw.nw_ports" : "node:interface:nw",
    "compute_nodes.hw.sas_hba" : "node:interface:sas",
    "compute_nodes.hw.sas_ports" : "node:interface:sas:port",
    "compute_nodes.sw.cortx_sw_services" : "node:sw:os:service",
    "compute_nodes.sw.external_sw_services" : "node:sw:os:service",
    "compute_nodes" : "node",
    "storage_nodes" : "enclosure"
}
