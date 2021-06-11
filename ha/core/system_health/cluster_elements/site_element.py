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

class SiteElement(Element):
    """
    site.
    """

    def __init__(self):
        """
        Initalize SiteElement element.
        """
        super(SiteElement, self).__init__()
        self._rack_site_map: dict = self._get_rack_site_map()
        Log.info(f"Loaded Site element with rack-site map {self._rack_site_map}")

    def get_event_from_subelement(self, children_event: HealthEvent):
        """
        Get element id for given healthevent.

        Args:
            healthevent (HealthEvent): Health event.
        """
        pass

    def _get_rack_site_map(self) -> dict:
        """
        Return rack site map
        """
        site_map: dict = {}
        node_ids = self._confstore.get(const.PVTFQDN_TO_NODEID_KEY)
        for node_id in node_ids.values():
            key = self._prepare_key(const.COMPONENTS.NODE_MAP.value, node_id=node_id)
            node_map_key = dict(self._confstore.get(key))
            Log.debug(f"Node map for key {node_id} is {node_map_key}")
            node_map = json.loads(list(node_map_key.values())[0])
            rack_id = node_map.get(NODE_MAP_ATTRIBUTES.RACK_ID.value)
            site_id = node_map.get(NODE_MAP_ATTRIBUTES.SITE_ID.value)
            if site_id not in site_map.keys():
                site_map[site_id] = [rack_id]
            else:
                if rack_id not in site_map[site_id]:
                    site_map[site_id].append(site_id)
        return site_map
