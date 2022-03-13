#!/usr/bin/env python3

# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
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

from cortx.utils.log import Log
from ha.core.system_health.health_evaluators.element_health_evaluator import ElementHealthEvaluator
from ha.core.system_health.const import HEALTH_STATUSES, HEALTH_EVENTS, CLUSTER_ELEMENTS
from ha.core.system_health.model.health_event import HealthEvent


class NodeHealthEvaluator(ElementHealthEvaluator):
    """ Node Health Evaluator."""

    def __init__(self):
        """
        Initalize NodeHealthEvaluator element.
        """
        super(NodeHealthEvaluator, self).__init__()

    def evaluate_status(self, health_event: HealthEvent) -> HealthEvent:
        """
        Evaluate health event of children and return its health event.

        Args:
            health_event (HealthEvent): Health event of children

        Returns:
            HealthEvent: Health event of current element.
        """
        node_id = health_event.node_id
        status = self.get_node_status(node_id, rack_id=health_event.rack_id,
                                      cluster_id=health_event.cluster_id,
                                      site_id=health_event.site_id)
        Log.info(f"Evaluated Node {node_id} status as {status}")
        return self._get_new_event(
            event_type=status,
            resource_type=CLUSTER_ELEMENTS.NODE.value,
            resource_id=node_id,
            subelement_event=health_event)

    def get_node_status(self, node_id: str, **kwargs) -> str:
        """
        Apply rules and get status.

        Returns:
            str: Node status.
        """
        children = self.get_children(CLUSTER_ELEMENTS.NODE.value, node_id,
                                     cluster_id=kwargs["cluster_id"],
                                     site_id=kwargs["site_id"],
                                     rack_id=kwargs["rack_id"],
                                     comp_type=CLUSTER_ELEMENTS.NODE.value)
        Log.debug(f"Children for Node {node_id} are {children}")
        status_map = self.get_status_map(children, node_id=node_id, rack_id=kwargs["rack_id"],
                                         cluster_id=kwargs["cluster_id"], site_id=kwargs["site_id"])
        Log.info(f"Apply Node rule of {node_id} {kwargs} on {status_map}")
        status = self._check_node_rules(status_map)
        Log.info(f"Status for {CLUSTER_ELEMENTS.NODE.value}:{CLUSTER_ELEMENTS.NODE.value}:{node_id} is {status}")
        return status

    def _check_node_rules(self, children) -> str:
        """
        Check Node rule and return status.

        Args:
            children (dict): status mapping for its children

        Returns:
            str: Status of Node
        """
        # Considering Node have only cvg as element and element_type
        cvg_ids = children[CLUSTER_ELEMENTS.CVG.value][CLUSTER_ELEMENTS.CVG.value]
        quorum_size = int(len(cvg_ids.keys())/2) + 1
        if self.count_status(cvg_ids, HEALTH_STATUSES.ONLINE.value) == len(cvg_ids.keys()):
            node_status = HEALTH_EVENTS.FAULT_RESOLVED.value
        elif self.count_status(cvg_ids, HEALTH_STATUSES.ONLINE.value) >= quorum_size:
            node_status = HEALTH_EVENTS.THRESHOLD_BREACHED_LOW.value
        elif self.count_status(cvg_ids, HEALTH_STATUSES.FAILED.value) >= quorum_size:
            node_status = HEALTH_EVENTS.FAILED.value
        elif self.count_status(cvg_ids, HEALTH_STATUSES.UNKNOWN.value) >= quorum_size:
            node_status = HEALTH_EVENTS.UNKNOWN.value
        else:
            node_status = HEALTH_EVENTS.THRESHOLD_BREACHED_LOW.value
        return node_status
