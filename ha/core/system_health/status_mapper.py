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
from ha.fault_tolerance.const import HEALTH_EVENT_SOURCES
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.const import HEALTH_EVENTS, HEALTH_STATUSES
from ha.core.error import HaStatusMapperException
from ha.core.system_health.const import CLUSTER_ELEMENTS

class StatusMapper:
    """
    Setup Mapper. This class provides methods for mapping event to status.
    """
    #TODO: use HEALTH_EVENTS
    EVENT_TO_STATUS_MAPPING = {
        "fault": "offline",
        "fault_resolved": "online",
        "missing": "offline",
        "insertion": "online",
        "recovering": "recovering",
        "online": "online",
        "failed": "failed",
        "unknown": "unknown",
        "degraded": "degraded",
        "threshold_breached:low": "degraded",
        "threshold_breached:high": "degraded",
        "offline":"offline",
        "repairing": "repairing",
        "repaired": "repaired",
        "rebalancing": "rebalancing"
    }

    EVENT_TO_SEVERITY_MAPPING = {
        "starting"    : "informational",
        "recovering"  : "informational",
        "online"      : "informational",
        "degraded"    : "informational",
        "repairing"   : "informational",
        "repaired"    : "informational",
        "rebalancing" : "informational",
        "failed"      : "error",
        "offline"     : "informational"
    }

    def __init__(self):
        """
        Init method.
        """
        super(StatusMapper, self).__init__()

    def map_event(self, event: HealthEvent) -> str:
        """Returns the status by mapping it against the source and event type."""
        try:
            component_type = event.resource_type
            if event.source == HEALTH_EVENT_SOURCES.MONITOR.value and event.event_type == HEALTH_EVENTS.ONLINE.value and \
                component_type in [CLUSTER_ELEMENTS.NODE.value]:
                status = HEALTH_STATUSES.STARTING.value
            else:
                status = self.EVENT_TO_STATUS_MAPPING[event.event_type]
            return status
        except KeyError as e:
            Log.error(f"StatusMapper, map_event, No equivalent event type found: {e}")
            raise HaStatusMapperException(f"StatusMapper, map_event, No equivalent event type found: {e}")
        except Exception as e:
            Log.error(f"StatusMapper, map_event, Exception occured while mapping event_type to status: {e}")
            raise HaStatusMapperException(f"StatusMapper, map_event, Exception while mapping event: {e}")
