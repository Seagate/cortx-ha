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
from ha.core.system_health.const import HEALTH_STATUSES, HEALTH_EVENTS, CLUSTER_ELEMENTS
from ha.core.system_health.system_health_metadata import SystemHealthComponents
from ha.core.system_health.model.entity_health import EntityEvent, EntityAction, EntityHealth
from ha.core.system_health.system_health_exception import HealthNotFoundException

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

    def get_event_from_subelement(self, subelement_event: HealthEvent) -> HealthEvent:
        """
        Get element id for given healthevent.

        Args:
            subelement_event (HealthEvent): Health event for site.
        """
        site_id = subelement_event.site_id
        status_map: dict = self.get_status_map(site_id, subelement_event, self._rack_site_map)
        status = self._get_site_status(status_map)
        Log.info(f"Evaluated site {site_id} status as {status}")
        return self.get_new_event(
            event_id=subelement_event.event_id + "site",
            event_type=status,
            resource_type=CLUSTER_ELEMENTS.SITE.value,
            resource_id=site_id,
            subelement_event=subelement_event)

    def _get_site_status(self, node_status_map):
        return "fault"