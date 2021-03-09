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

class StatusMapper:
    """
    Setup Mapper. This class provides methods for mapping event to status.
    """

    EVENT_TO_STATUS_MAPPING = {
        "fault": "offline",
        "fault_resolved": "online",
        "missing": "offline",
        "insertion": "online",
        "unknown": "unknown",
        "threshold_breached:low": "degraded",
        "threshold_breached:high": "degraded"
    }

    def __init__(self):
        """
        Init method.
        """
        super(StatusMapper, self).__init__()

    def map_event(self, event_type):
        """Returns the status by mapping it against the event type"""
        try:
            status = self.EVENT_TO_STATUS_MAPPING[event_type]
            return status
        except KeyError as e:
            raise Exception('StatusMapper, map_event, No equivalent \
                            event type found: %s' % e)
            return
        except Exception as e:
            logger.error('StatusMapper, map_event, Exception occured \
                         while mapping event_type to status: %s ' % e)
            return