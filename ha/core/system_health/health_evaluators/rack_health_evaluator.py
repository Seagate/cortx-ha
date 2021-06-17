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

import time
import uuid
from cortx.utils.log import Log
from ha.core.system_health.health_evaluators.element_health_evaluator import ElementHealthEvaluator
from ha.core.system_health.const import HEALTH_STATUSES, HEALTH_EVENTS, CLUSTER_ELEMENTS
from ha.core.system_health.model.health_event import HealthEvent

class RackHealthEvaluator(ElementHealthEvaluator):
    """
    rack.
    """
    def __init__(self):
        """
        Initalize RackHealthEvaluator element.
        """
        super(RackHealthEvaluator, self).__init__()

    def evaluate_status(self, health_event: HealthEvent) -> HealthEvent:
        """
        Evaluate health event of children and return its health event.

        Args:
            health_event (HealthEvent): Health event of children

        Returns:
            HealthEvent: Health event of current element.
        """
        rack_id = health_event.rack_id
        status = self.get_rack_status(rack_id,
                                        cluster_id=health_event.cluster_id,
                                        site_id=health_event.site_id)
        Log.info(f"Evaluated rack {rack_id} status as {status}")
        return self._get_new_event(
            event_id=str(int(time.time())) + str(uuid.uuid4().hex),
            event_type=status,
            resource_type=CLUSTER_ELEMENTS.RACK.value,
            resource_id=rack_id,
            subelement_event=health_event)

    def get_rack_status(self, rack_id: str, **kwargs) -> str:
        """
        Apply rules and get status.

        Returns:
            str: Rack status.
        """
        children = self.get_children(CLUSTER_ELEMENTS.RACK.value, rack_id,
                    cluster_id=kwargs["cluster_id"],
                    site_id=kwargs["site_id"],
                    comp_type=CLUSTER_ELEMENTS.RACK.value)
        Log.debug(f"Children for rack {rack_id} are {children}")
        status_map = self.get_status_map(children, rack_id=rack_id, cluster_id=kwargs["cluster_id"], site_id=kwargs["site_id"])
        Log.info(f"Apply rack rule of {rack_id} {kwargs} on {status_map}")
        status = self._check_rack_rules(status_map)
        Log.info(f"Status for {CLUSTER_ELEMENTS.RACK.value}:{CLUSTER_ELEMENTS.RACK.value}:{rack_id} is {status}")
        return status

    def _check_rack_rules(self, children) -> str:
        """
        Check rack rule and return status.

        Args:
            children (dict): status mapping for its children

        Returns:
            str: Status of rack
        """
        # Considering rack have only node as element and element_type
        node_ids = children[CLUSTER_ELEMENTS.NODE.value][CLUSTER_ELEMENTS.NODE.value]
        quorum_size = int(len(node_ids.keys())/2) + 1
        if self.count_status(node_ids, HEALTH_STATUSES.ONLINE.value) == len(node_ids.keys()):
            rack_status = HEALTH_EVENTS.FAULT_RESOLVED.value
        elif self.count_status(node_ids, HEALTH_STATUSES.ONLINE.value) >= quorum_size:
            rack_status = HEALTH_EVENTS.THRESHOLD_BREACHED_LOW.value
        elif self.count_status(node_ids, HEALTH_STATUSES.PENDING.value) >= quorum_size:
            rack_status = HEALTH_EVENTS.UNKNOWN.value
        elif self.count_status(node_ids, HEALTH_STATUSES.UNKNOWN.value) >= quorum_size:
            rack_status = HEALTH_EVENTS.UNKNOWN.value
        #TODO: add failed status
        else:
            rack_status = HEALTH_EVENTS.FAULT.value
        return rack_status
