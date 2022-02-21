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
from ha.fault_tolerance.const import HEALTH_ATTRIBUTES, \
    EVENT_ATTRIBUTES

VERSION = "1.0"

class Event:

    """
    Class for health status event message schema,
    where producer can import this class object and add it
    in there existing schema.
    """

    def __init__(self):
        """
        Initialize default value for header and payload component.
        """
        self.event = {}
        header = {}
        header[HEALTH_ATTRIBUTES.VERSION.value] = VERSION
        header[HEALTH_ATTRIBUTES.TIMESTAMP.value] = str(int(time.time()))
        header[HEALTH_ATTRIBUTES.EVENT_ID.value] =  \
            header[HEALTH_ATTRIBUTES.TIMESTAMP.value] + \
            str(uuid.uuid4().hex)
        self.event[EVENT_ATTRIBUTES.HEALTH_EVENT_HEADER.value] = header

        payload = {}
        payload[HEALTH_ATTRIBUTES.SOURCE.value] = None
        payload[HEALTH_ATTRIBUTES.CLUSTER_ID.value] = None
        payload[HEALTH_ATTRIBUTES.SITE_ID.value] = None
        payload[HEALTH_ATTRIBUTES.RACK_ID.value] = None
        payload[HEALTH_ATTRIBUTES.STORAGESET_ID.value] = None
        payload[HEALTH_ATTRIBUTES.NODE_ID.value] = None
        payload[HEALTH_ATTRIBUTES.RESOURCE_TYPE.value] = None
        payload[HEALTH_ATTRIBUTES.RESOURCE_ID.value] = None
        payload[HEALTH_ATTRIBUTES.RESOURCE_STATUS.value] = None
        payload[HEALTH_ATTRIBUTES.SPECIFIC_INFO.value] = {}
        self.event[EVENT_ATTRIBUTES.HEALTH_EVENT_PAYLOAD.value] = \
            payload

    def set_payload(self, _input):
        """
        Update payload values.
        params: payload data of attributes with value type : dict
        _input = {"source" : "hare", "node_id" : "2"}
        """
        for key in _input.keys():
            if key in list(
                self.event[EVENT_ATTRIBUTES.HEALTH_EVENT_PAYLOAD.value
                    ].keys()
            ):
                self.event[EVENT_ATTRIBUTES.HEALTH_EVENT_PAYLOAD.value
                    ][key] = _input[key]

    def ret_dict(self):
        """
        Return dictionary attribute.
        """
        return vars(self)
