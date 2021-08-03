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
from ha.core.error import HaStatusMapperException

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
        "failed": "failed",
        "active": "active",
        "inactive": "inactive",
        "unknown": "unknown",
        "threshold_breached:low": "degraded",
        "threshold_breached:high": "degraded"
    }

    def __init__(self):
        """
        Init method.
        """
        super(StatusMapper, self).__init__()

    def map_event(self, event_type: str) -> str:
        """Returns the status by mapping it against the event type"""
        try:
            status = self.EVENT_TO_STATUS_MAPPING[event_type]
            return status
        except KeyError as e:
            Log.error(f"StatusMapper, map_event, No equivalent event type found: {e}")
            raise HaStatusMapperException(f"StatusMapper, map_event, No equivalent event type found: {e}")
        except Exception as e:
            Log.error(f"StatusMapper, map_event, Exception occured while mapping event_type to status: {e}")
            raise HaStatusMapperException(f"StatusMapper, map_event, Exception while mapping event: {e}")
