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

import json
from cortx.utils.log import Log
from ha import const
from ha.core.system_health.cluster_elements.element import Element
from ha.core.system_health.const import NODE_MAP_ATTRIBUTES
from ha.core.system_health.const import HEALTH_STATUSES, HEALTH_EVENTS, CLUSTER_ELEMENTS
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.model.entity_health import EntityAction, EntityHealth
from ha.core.system_health.system_health_exception import HealthNotFoundException

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

    def get_event_from_subelement(self, subelement_event: HealthEvent) -> HealthEvent:
        """
        Get element id for given healthevent.

        Args:
            subelement_event (HealthEvent): Health event for node.
        """
        rack_id = subelement_event.rack_id
        node_status_map: dict = self.get_status_map(rack_id, subelement_event, self._rack_node_map)
        status = self._get_rack_status(node_status_map)
        Log.info(f"Evaluated rack {rack_id} status as {status}")
        return self.get_new_event(
            event_id=subelement_event.event_id + "rack",
            event_type=status,
            resource_type=CLUSTER_ELEMENTS.RACK.value,
            resource_id=rack_id,
            subelement_event=subelement_event)

    def _get_rack_status(self, status_map: dict) -> str:
        """
        Apply rules and get status.

        Returns:
            str: Rack status.
        """
        rack_status = None
        quorum_size = (len(status_map.keys())/2) + 1
        # offline online unknown degraded pending
        if self.count_status(status_map, HEALTH_STATUSES.ONLINE.value) == len(status_map.keys()):
            rack_status = HEALTH_EVENTS.FAULT_RESOLVED.value
        # TODO: apply quorum property
        elif self.count_status(status_map, HEALTH_STATUSES.ONLINE.value) == quorum_size:
            rack_status = HEALTH_EVENTS.THRESHOLD_BREACHED_LOW.value
        elif self.count_status(status_map, HEALTH_STATUSES.PENDING.value) >= quorum_size:
            rack_status = HEALTH_EVENTS.UNKNOWN.value
        elif self.count_status(status_map, HEALTH_STATUSES.UNKNOWN.value) >= quorum_size:
            rack_status = HEALTH_EVENTS.UNKNOWN.value
        else:
            rack_status = HEALTH_EVENTS.FAULT.value
        return rack_status
