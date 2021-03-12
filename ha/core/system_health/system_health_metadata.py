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

from ha import const

# Components health update hierarchy
CLUSTER_UPDATE_HIERARCHY = ["cluster"]
SITE_UPDATE_HIERARCHY = ["site"] + CLUSTER_UPDATE_HIERARCHY
RACK_UPDATE_HIERARCHY = ["rack"] + SITE_UPDATE_HIERARCHY
STORAGESET_UPDATE_HIERARCHY = ["storageset"] + RACK_UPDATE_HIERARCHY
NODE_UPDATE_HIERARCHY = ["node"] + STORAGESET_UPDATE_HIERARCHY
SERVER_UPDATE_HIERARCHY = ["server"] + NODE_UPDATE_HIERARCHY
SERVER_HW_UPDATE_HIERARCHY = ["server_hw"] + SERVER_UPDATE_HIERARCHY
SERVER_SERVICE_UPDATE_HIERARCHY = ["server_service", "agg_service"] + SERVER_UPDATE_HIERARCHY
STORAGE_UPDATE_HIERARCHY = ["storage"] + NODE_UPDATE_HIERARCHY
STORAGE_COMPONENT_UPDATE_HIERARCHY = ["storage_component"] + STORAGE_UPDATE_HIERARCHY

# Components/resources maintained by System Health module. Note: Do not change the order.
SYSTEM_HEALTH_COMPONENTS = {"server_hw": {const.RESOURCE_LIST: ["node:fru", "node:sensor", "node:os", "node:interface"],
                                          const.UPDATE_HIERARCHY: SERVER_HW_UPDATE_HIERARCHY},
                            "server_service": {const.RESOURCE_LIST: ["node:sw"],
                                               const.UPDATE_HIERARCHY: SERVER_SERVICE_UPDATE_HIERARCHY},
                            "storage_component": {const.RESOURCE_LIST: ["enclosure"],
                                                  const.UPDATE_HIERARCHY: STORAGE_COMPONENT_UPDATE_HIERARCHY},
                            "storageset": {const.RESOURCE_LIST: ["storageset"], const.UPDATE_HIERARCHY: STORAGESET_UPDATE_HIERARCHY},
                            "server": {const.RESOURCE_LIST: ["server"], const.UPDATE_HIERARCHY: SERVER_UPDATE_HIERARCHY},
                            "storage": {const.RESOURCE_LIST: ["storage"], const.UPDATE_HIERARCHY: STORAGE_UPDATE_HIERARCHY},
                            "node": {const.RESOURCE_LIST: ["node"], const.UPDATE_HIERARCHY: NODE_UPDATE_HIERARCHY},
                            "rack": {const.RESOURCE_LIST: ["rack"], const.UPDATE_HIERARCHY: RACK_UPDATE_HIERARCHY},
                            "site": {const.RESOURCE_LIST: ["site"], const.UPDATE_HIERARCHY: SITE_UPDATE_HIERARCHY},
                            "cluster": {const.RESOURCE_LIST: ["cluster"],  const.UPDATE_HIERARCHY: CLUSTER_UPDATE_HIERARCHY}}

# Health keys
SYSTEM_HEALTH_KEYS = {
    "cluster": "/cortx/ha/system/cluster/$cluster_id/health",
    "site": "/cortx/ha/system/cluster/$cluster_id/site/$site_id/health",
    "rack": "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/health",
    "storageset": "/cortx/ha/system/cluster/$cluster_id/storageset/$storageset_id/health",
    "node": "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/health",
    "server": "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/server/$server_id/health",
    "server_hw": "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/server/$server_id/hw/$comp_type/$comp_id/health",
    "server_service": "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/server/$server_id/service/$comp_type/$comp_id/health",
    "storage": "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/storage/$storage_id/health",
    "storage_component": "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/storage/$storage_id/hw/$comp_type/$comp_id/health",
    "agg_service": "/cortx/ha/system/cluster/$cluster_id/service/$comp_type/$comp_id/health",
    "node_map": "/cortx/ha/system/cluster/node_map/$node_id"
}

# Entity health value
ENTITY_HEALTH = {"events": [{"event_timestamp": "", "created_timestamp": "", "status": ""},
                           {"event_timestamp": "", "created_timestamp": "", "status": ""}],
                 "specific_info": "",
                 "action": {"modified_timestamp": "", "status": ""},
                 "properties": {"IsFru": ""}}