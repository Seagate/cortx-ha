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

import ast
import json

from cortx.utils.log import Log

from ha import const
from ha.core.system_health.cluster_elements.element import Element
from ha.core.system_health.const import NODE_MAP_ATTRIBUTES
from ha.core.error import HaSystemHealthException
from ha.core.system_health.model.health_event import HealthEvent

class NodeElement(Element):
    """
    node.
    """

    def __init__(self):
        """
        Initalize NodeElement element.
        """
        super(NodeElement, self).__init__()

    def get_event_from_subelement(self, subelement_event: HealthEvent) -> HealthEvent:
        """
        Get element id for given healthevent.

        Args:
            subelement_event (HealthEvent): Health event for node.
        """
        pass

    def get_node_status(self, node_id: str, **kwargs):
        """
        get node status method. This method is for returning a status of a node.
        """
        try:
            # Prepare key and read the health value.
            key = self._prepare_key(const.COMPONENTS.NODE_MAP.value, node_id=node_id)
            node_map_val = self.healthmanager.get_key(key)
            if node_map_val is not None:
                node_map_dict = ast.literal_eval(node_map_val)
                key = self._prepare_key(component='node', cluster_id=node_map_dict[NODE_MAP_ATTRIBUTES.CLUSTER_ID.value],
                                        site_id=node_map_dict[NODE_MAP_ATTRIBUTES.SITE_ID.value], rack_id=node_map_dict[NODE_MAP_ATTRIBUTES.RACK_ID.value],
                                        storageset_id=node_map_dict[NODE_MAP_ATTRIBUTES.STORAGESET_ID.value], node_id=node_id, **kwargs)
                node_health_dict = json.loads(self.healthmanager.get_key(key))
                node_status = {"status": node_health_dict['events'][0]['status'],
                               "created_timestamp": node_health_dict['events'][0]['created_timestamp']}
                return node_status
            else:
                raise HaSystemHealthException(f"node_id : {node_id} doesn't exist")

        except Exception as e:
            Log.error(f"Failed reading status for component: node with Error: {e}")
            raise HaSystemHealthException(f"Failed reading status for node with node_id : {node_id}")
