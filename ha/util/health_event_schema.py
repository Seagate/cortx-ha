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

import time
import uuid

from ha.util.const import HEALTH_EVENT_VERSION, HEALTH_EVENT_HEADER, HEALTH_EVENT_PAYLOAD
from ha.util.const import HEALTH_EVENT_ATTRIBUTES

class Event:
    """
    Health Event. This class implements health event object,
    which will be sent by various modules to HA for updating
    the system health.
    """

    def __init__(self):
        """
        Init method.
        """

        self.event: dict = {}
        self.event[HEALTH_EVENT_HEADER] = {}
        self.event[HEALTH_EVENT_HEADER][HEALTH_EVENT_ATTRIBUTES.VERSION] = HEALTH_EVENT_VERSION
        self.event[HEALTH_EVENT_HEADER][HEALTH_EVENT_ATTRIBUTES.TIMESTAMP] = str(int(time.time()))
        self.event[HEALTH_EVENT_HEADER][HEALTH_EVENT_ATTRIBUTES.EVENT_ID] = self.event[HEALTH_EVENT_HEADER][HEALTH_EVENT_ATTRIBUTES.TIMESTAMP] + str(uuid.uuid4().hex)
        self.event[HEALTH_EVENT_PAYLOAD] = {}

    def set_payload(self, payload: dict):
        """
        Sets payload.
        """

        self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.SOURCE] = payload[HEALTH_EVENT_ATTRIBUTES.SOURCE]
        self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.CLUSTER_ID] = payload[HEALTH_EVENT_ATTRIBUTES.CLUSTER_ID]
        self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.SITE_ID] = payload[HEALTH_EVENT_ATTRIBUTES.SITE_ID]
        self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.RACK_ID] = payload[HEALTH_EVENT_ATTRIBUTES.RACK_ID]
        self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.STORAGESET_ID] = payload[HEALTH_EVENT_ATTRIBUTES.STORAGESET_ID]
        self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.NODE_ID] = payload[HEALTH_EVENT_ATTRIBUTES.NODE_ID]
        self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.RESOURCE_TYPE] = payload[HEALTH_EVENT_ATTRIBUTES.RESOURCE_TYPE]
        self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.RESOURCE_ID] = payload[HEALTH_EVENT_ATTRIBUTES.RESOURCE_ID]
        self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.RESOURCE_STATUS] = payload[HEALTH_EVENT_ATTRIBUTES.RESOURCE_STATUS]
        self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.SPECIFIC_INFO] = payload[HEALTH_EVENT_ATTRIBUTES.SPECIFIC_INFO]

    def update_event(self, key_to_update=None, value=None):
        """update event structure for a particular given key value"""

        if isinstance(key_to_update, dict):
            self.event[HEALTH_EVENT_PAYLOAD][HEALTH_EVENT_ATTRIBUTES.SPECIFIC_INFO] = key_to_update
        else:
            self.event[HEALTH_EVENT_PAYLOAD][key_to_update] = value
        return self.ret_dict()

    def ret_dict(self):
        """
        Return dictionary attribute.
        """

        return vars(self)



e = Event()
e.ret_dict()
