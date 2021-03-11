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
import json

from cortx.utils.log import Log
from ha import const
from ha.core.error import HaEntityHealthException

class EntityHealth:
    """
    Entity Health. This class implements a health object, which will be stored in store
    for every component.
    """

    def __init__(self, event_timestamp, health_status, action_status,
                 is_fru=None, previous_health: json=None, **kwargs):
        """
        Init method.
        """
        self.event_timestamp = event_timestamp
        self.health_status = health_status
        self.action_status = action_status
        self.is_fru = is_fru
        self.previous_health = previous_health
        self.specific_info = kwargs

    def __str__(self):
        try:
            epoch_time = str(int(time.time()))
            # If previous health is passed, the we need to modity and return.
            if self.previous_health:
                healthvalue = json.loads(self.previous_health)
                # Keep the history of events as per the configuration
                num_events = const.NUM_ENTITY_HEALTH_EVENTS - 1
                while num_events:
                    healthvalue['events'][num_events] = healthvalue['events'][num_events - 1]
                    num_events = num_events - 1
            else:
                healthvalue = const.ENTITY_HEALTH

            # Update health status
            healthvalue['events'][0] = {"event_timestamp": self.event_timestamp,
                                        "created_timestamp": epoch_time, "status": self.health_status}
            # Update action
            healthvalue['action']['modified_timestamp'] = epoch_time
            healthvalue['action']['status'] = self.action_status

            # Update properties if present.
            if self.is_fru is not None:
                healthvalue['properties']['IsFru'] = self.is_fru
            # Add any additional key/values to the specific info
            specific_info_temp = dict(healthvalue['specific_info'])
            for key, value in self.specific_info.items():
                specific_info_temp[key] = value
            healthvalue['specific_info'] = specific_info_temp

            # Dump the entiry health into json string and return the same.
            return json.dumps(healthvalue)

        except Exception as e:
            Log.error(f"Failed populating entiry health with Error: {e}")
            raise HaEntityHealthException("Failed populating entity health")