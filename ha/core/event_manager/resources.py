#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
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

import enum
from ha.util.enum_list import EnumListMeta
from ha.core.system_health.const import HEALTH_STATUSES

class SUBSCRIPTION_LIST(enum.Enum, metaclass=EnumListMeta):
    SSPL = "sspl"
    CSM = "csm"
    S3 = "s3"
    MOTR = "motr"
    HARE = "hare"
    HA = "ha"
    TEST = "test"

RESOURCE_STATUS = HEALTH_STATUSES

class RESOURCE_TYPES(enum.Enum, metaclass=EnumListMeta):
    NODE = "node"
    SITE = "site"
    RACK = "rack"
    CLUSTER = "cluster"
    ENCLOSURE_HW_CONTROLLER = "enclosure:hw:controller"
    ENCLOSURE_HW_DISK = "enclosure:hw:disk"
    ENCLOSURE_HW_FAN = "enclosure:hw:fan"
    ENCLOSURE_HW_PSU = "enclosure:hw:psu"
    ENCLOSURE_HW_SIDEPLANE = "enclosure:hw:sideplane"
    ENCLOSURE_CORTX_LOGICAL_VOLUME = "enclosure:cortx:logical_volume"
    ENCLOSURE_CORTX_DISK_GROUP = "enclosure:cortx:disk_group"
    ENCLOSURE_SENSOR_TEMPERATURE = "enclosure:sensor:temperature"
    ENCLOSURE_SENSOR_VOLTAGE = "enclosure:sensor:voltage"
    ENCLOSURE_SENSOR_CURRENT = "enclosure:sensor:current"
    ENCLOSURE_INTERFACE_SAS = "enclosure:interface:sas"
    NODE_FRU_PSU = "node:fru:psu"
    NODE_FRU_FAN = "node:fru:fan"
    NODE_FRU_DISK = "node:fru:disk"
    NODE_SENSOR_TEMPERATURE = "node:sensor:temperature"
    NODE_SENSOR_VOLTAGE = "node:sensor:voltage"
    NODE_OS_CPU = "node:os:cpu"
    NODE_OS_CPU_CORE = "node:os:cpu:core"
    NODE_OS_DISK_SPACE = "node:os:disk_space"
    NODE_OS_MEMORY_USAGE = "node:os:memory_usage"
    NODE_OS_MEMORY = "node:os:memory"
    NODE_OS_RAID_DATA = "node:os:raid_data"
    NODE_OS_RAID_INTEGRITY = "node:os:raid_integrity"
    NODE_OS_DISK = "node:os:disk"
    NODE_INTERFACE_NW = "node:interface:nw"
    NODE_INTERFACE_NW_CABLE = "node:interface:nw:cable"
    NODE_INTERFACE_SAS = "node:interface:sas"
    NODE_INTERFACE_SAS_PORT = "node:interface:sas:port"
    NODE_SW_OS_SERVICE = "node:sw:os:service"