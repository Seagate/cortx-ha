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


import ast

from ha  import const
from ha.core.system_health.system_health import SystemHealth, SystemHealthManager
from ha.core.config.config_manager import ConfigManager
from ha.core.error import ClusterManagerError

class NodeParams:
    @staticmethod
    def get_node_map(node_name: str) -> dict:
        '''
        Return cluster_id, site_id, rack_id, node_id, for the given node_name
        '''
        conf_store = ConfigManager.get_confstore()
        system_health = SystemHealth(conf_store)
        health_manager = SystemHealthManager(conf_store)

        key_val  = conf_store.get(f"{const.PVTFQDN_TO_NODEID_KEY}/{node_name}")
        _, node_id = key_val.popitem()

        key = system_health._prepare_key(const.COMPONENTS.NODE_MAP.value, node_id=node_id)

        node_map_val = health_manager.get_key(key)
        if node_map_val is None:
            raise ClusterManagerError("Failed to fetch node_map value")

        node_map_dict = ast.literal_eval(node_map_val)
        return node_map_dict
