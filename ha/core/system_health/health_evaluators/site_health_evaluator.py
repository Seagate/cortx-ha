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

from cortx.utils.log import Log
from ha.core.system_health.health_evaluators.element_health_evaluator import ElementHealthEvaluator
from ha.core.system_health.const import HEALTH_STATUSES, HEALTH_EVENTS, CLUSTER_ELEMENTS
from ha.core.system_health.model.health_event import HealthEvent

class SiteHealthEvaluator(ElementHealthEvaluator):
    """
    site.
    """

    def __init__(self):
        """
        Initalize SiteElement element.
        """
        super(SiteHealthEvaluator, self).__init__()

    def evaluate_status(self, health_event: HealthEvent) -> HealthEvent:
        """
        Evaluate health event of children and return its health event.

        Args:
            health_event (HealthEvent): Health event of children

        Returns:
            HealthEvent: Health event of current element.
        """
        site_id = health_event.site_id
        status = self.get_site_status(site_id, cluster_id=health_event.cluster_id)
        Log.info(f"Evaluated site {site_id} status as {status}")
        return self._get_new_event(
            event_type=status,
            resource_type=CLUSTER_ELEMENTS.SITE.value,
            resource_id=site_id,
            subelement_event=health_event)

    def get_site_status(self, site_id: str, **kwargs) -> str:
        """
        Apply rules and get status.

        Returns:
            str: site status.
        """
        children = self.get_children(CLUSTER_ELEMENTS.SITE.value, site_id,
                    cluster_id=kwargs["cluster_id"],
                    comp_type=CLUSTER_ELEMENTS.SITE.value)
        Log.debug(f"Children for site {site_id} are {children}")
        status_map = self.get_status_map(children, site_id=site_id, cluster_id=kwargs["cluster_id"])
        Log.info(f"Apply site rule of {site_id} {kwargs} on {status_map}")
        status = self._check_site_rules(status_map)
        Log.info(f"Status for {CLUSTER_ELEMENTS.SITE.value}:{CLUSTER_ELEMENTS.SITE.value}:{site_id} is {status}")
        return status

    def _check_site_rules(self, children) -> str:
        """
        Check site rule and return status.

        Args:
            children (dict): status mapping for its children

        Returns:
            str: Status of site
        """
        site_status: str = None
        rack_ids = children[CLUSTER_ELEMENTS.RACK.value][CLUSTER_ELEMENTS.RACK.value]
        quorum_size = int(len(rack_ids.keys())/2) + 1
        if self.count_status(rack_ids, HEALTH_STATUSES.ONLINE.value) == len(rack_ids.keys()):
            site_status = HEALTH_EVENTS.FAULT_RESOLVED.value
        elif self.count_status(rack_ids, HEALTH_STATUSES.ONLINE.value) >= quorum_size:
            site_status = HEALTH_EVENTS.THRESHOLD_BREACHED_LOW.value
        elif self.count_status(rack_ids, HEALTH_STATUSES.DEGRADED.value) >= quorum_size:
            site_status = HEALTH_EVENTS.THRESHOLD_BREACHED_LOW.value
        elif self.count_status(rack_ids, HEALTH_STATUSES.FAILED.value) >= quorum_size:
            site_status = HEALTH_EVENTS.FAILED.value
        else:
            site_status = HEALTH_EVENTS.THRESHOLD_BREACHED_LOW.value
        return site_status
