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

from ha.core.system_health.cluster_elements.element import Element
from cortx.utils.log import Log
from ha import const
import json
from ha.core.system_health.const import NODE_MAP_ATTRIBUTES
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.system_health_metadata import SystemHealthComponents

class RackElement(Element):
    """
    rack.
    """
    def __init__(self):
        """
        Initalize RackElement element.
        """
        super(RackElement, self).__init__()
        self._rack_node_map: dict = self._get_rack_node_map()
        Log.info(f"Loaded Rack element with rack-node map {self._rack_node_map}")

    def _get_rack_node_map(self) -> dict:
        """
        Return rack rack map
        """
        rack_map: dict = {}
        node_ids = self._confstore.get(const.PVTFQDN_TO_NODEID_KEY)
        for node_id in node_ids.values():
            key = self._prepare_key(const.COMPONENTS.NODE_MAP.value, node_id=node_id)
            node_map_key = dict(self._confstore.get(key))
            Log.debug(f"Node map for key {node_id} is {node_map_key}")
            node_map = json.loads(list(node_map_key.values())[0])
            rack_id = node_map.get(NODE_MAP_ATTRIBUTES.RACK_ID.value)
            if rack_id not in rack_map.keys():
                rack_map[rack_id] = [node_id]
            else:
                if node_id not in rack_map[rack_id]:
                    rack_map[rack_id].append(node_id)
        return rack_map

    def get_event_from_subelement(self, subelement_event: HealthEvent):
        """
        Get element id for given healthevent.

        Args:
            subelement_event (HealthEvent): Health event for node.
        """
        node_status_map: dict = {}
        rack_id = subelement_event.rack_id
        self._get_node_status_map(rack_id, subelement_event)

    def _get_node_status_map(self, rack_id: str, subelement_event) -> dict:
        """
        Get all nodes status for given rack.

        Args:
            rack_id (str): Rack id

        Returns:
            dict: node status map
        """
        component = SystemHealthComponents.get_component(subelement_event.resource_type)
        component_type = subelement_event.resource_type.split(':')[-1]
        for element in self._rack_node_map.get(rack_id):
            component_id = element
            current_health = self.get_status(component, component_id, comp_type=component_type,
                                        cluster_id=subelement_event.cluster_id, site_id=subelement_event.site_id,
                                        rack_id=subelement_event.rack_id, storageset_id=subelement_event.storageset_id,
                                        node_id=subelement_event.node_id, server_id=subelement_event.node_id,
                                        storage_id=subelement_event.node_id)
