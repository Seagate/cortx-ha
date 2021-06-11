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
from ha.core.system_health.cluster_elements.element import Element
from ha.core.system_health.const import NODE_MAP_ATTRIBUTES
from ha.core.system_health.model.health_event import HealthEvent
import json
from cortx.utils.log import Log

class ClusterElement(Element):
    """
    cluster.
    """

    def __init__(self):
        """
        Initalize cluster element.
        """
        super(ClusterElement, self).__init__()
        self._site_cluster_map: dict = self._get_site_cluster_map()
        Log.info(f"Loaded Cluster element with cluster-site map {self._site_cluster_map}")

    def get_event_from_subelement(self, children_event: HealthEvent):
        """
        Get element id for given healthevent.

        Args:
            healthevent (HealthEvent): Health event.
        """
        pass

    def _get_site_cluster_map(self) -> dict:
        """
        Provide map of rack and cluster
        """
        cluster_map: dict = {}
        node_ids = self._confstore.get(const.PVTFQDN_TO_NODEID_KEY)
        for node_id in node_ids.values():
            key = self._prepare_key(const.COMPONENTS.NODE_MAP.value, node_id=node_id)
            node_map_key = dict(self._confstore.get(key))
            Log.debug(f"Node map for key {node_id} is {node_map_key}")
            node_map = json.loads(list(node_map_key.values())[0])
            cluster_id = node_map.get(NODE_MAP_ATTRIBUTES.CLUSTER_ID.value)
            site_id = node_map.get(NODE_MAP_ATTRIBUTES.SITE_ID.value)
            if cluster_id not in cluster_map.keys():
                cluster_map[cluster_id] = [site_id]
            else:
                if site_id not in cluster_map[cluster_id]:
                    cluster_map[cluster_id].append(site_id)
        return cluster_map