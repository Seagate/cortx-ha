#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>. For any questions
# about this software or licensing, please email opensource@seagate.com or
# cortx-questions@seagate.com.

import abc
import json
from ha import const
from cortx.utils.conf_store.conf_store import Conf
from ha.core.config.config_manager import ConfigManager
from ha.core.system_health.model.health_event import HealthEvent

class Parser(metaclass=abc.ABCMeta):
    """
    Subscriber for event analyzer to pass msg.
    """

    @abc.abstractmethod
    def parse_event(self, msg: str) -> HealthEvent:
        """
        Parse event.
        Args:
            msg (str): Msg
        """
        pass

class AlertParser(Parser):
    """
    Subscriber for event analyzer to pass msg.
    """

    def parse_event(self, msg: str) -> HealthEvent:
        """
        Parse event.
        Args:
            msg (str): Msg
        """
        alert = json.loads(msg)

        event = {
            "event_id" : alert.get('sensor_response_type').get('alert_id'),
            "event_type" : alert.get('sensor_response_type').get('alert_type'),
            "severity" : alert.get('sensor_response_type').get('severity'),
            "site_id" : alert.get('sensor_response_type').get('info').get('site_id'),
            "rack_id" : alert.get('sensor_response_type').get('info').get('rack_id'),
            "cluster_id" : alert.get('sensor_response_type').get('info').get('cluster_id'),
            "storageset_id" : "TBD",
            "node_id" : alert.get('sensor_response_type').get('info').get('node_id'),
            "host_id" : alert.get('sensor_response_type').get('host_id'),
            "resource_type" : alert.get('sensor_response_type').get('info').get('resource_type'),
            "timestamp" : alert.get('sensor_response_type').get('info').get('event_time'),
            "resource_id" : alert.get('sensor_response_type').get('info').get('resource_id'),
            "specific_info" : alert.get('sensor_response_type').get('specific_info')
        }

        health_event = HealthEvent.dict_to_object(event)
        return health_event