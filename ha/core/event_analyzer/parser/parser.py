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
import re
from ha.core.error import EventAnalyzerError
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.config.config_manager import ConfigManager
from ha import const

class Parser(metaclass=abc.ABCMeta):
    """
    Subscriber for event analyzer to pass msg.
    """

    def __init__(self):
        """
        Init method.
        """
        self._confstore = ConfigManager._get_confstore()

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
        try:
            alert = json.loads(msg)

            event = {
                "event_id" : alert['sensor_response_type']['alert_id'],
                "event_type" : alert['sensor_response_type']['alert_type'],
                "severity" : alert['sensor_response_type']['severity'],
                "site_id" : alert['sensor_response_type']['info']['site_id'],
                "rack_id" : alert['sensor_response_type']['info']['rack_id'],
                "cluster_id" : alert['sensor_response_type']['info']['cluster_id'],
                "storageset_id" : "TBD",
                "node_id" : alert['sensor_response_type']['info']['node_id'],
                "host_id" : alert['sensor_response_type']['host_id'],
                "resource_type" : alert['sensor_response_type']['info']['resource_type'],
                "timestamp" : alert['sensor_response_type']['info']['event_time'],
                "resource_id" : alert['sensor_response_type']['info']['resource_id'],
                "specific_info" : alert['sensor_response_type']['specific_info']
            }

            health_event = HealthEvent.dict_to_object(event)

            return health_event

        except Exception as e:
            raise EventAnalyzerError(f"Failed to parse alert. Message: {msg}, Error: {e}")

class IEMParser(Parser):
    """
    Parser for IEMs.
    """

    def parse_event(self, msg: str) -> HealthEvent:
        """
        Parse event.
        Args:
            msg (str): Msg
        """
        try:
            iem_alert = json.loads(msg)

            # Parse hostname and convert to node id
            iem_description = iem_alert['sensor_response_type']['info']['description']
            hostname = re.split("=", re.split(";", re.findall("host=.+", iem_description)[0])[0])[1]
            key_val = self._confstore.get(f"{const.HOSTNAME_TO_NODEID_KEY}/{hostname}")
            _, node_id = key_val.popitem()

            event = {
                "event_id" : iem_alert['sensor_response_type']['alert_id'],
                "event_type" : iem_alert['sensor_response_type']['alert_type'],
                "severity" : iem_alert['sensor_response_type']['severity'],
                "site_id" : iem_alert['sensor_response_type']['info']['site_id'],
                "rack_id" : iem_alert['sensor_response_type']['info']['rack_id'],
                "cluster_id" : iem_alert['sensor_response_type']['info']['cluster_id'],
                "storageset_id" : "TBD",
                "node_id" : iem_alert['sensor_response_type']['info']['node_id'],
                "host_id" : iem_alert['sensor_response_type']['host_id'],
                "resource_type" : iem_alert['sensor_response_type']['specific_info']['module'].lower(),
                "timestamp" : iem_alert['sensor_response_type']['info']['event_time'],
                "resource_id" : node_id,
                "specific_info" : iem_alert['sensor_response_type']['specific_info']
            }

            health_event = HealthEvent.dict_to_object(event)
            return health_event

        except Exception as e:
            raise EventAnalyzerError(f"Failed to parse IEM. Message: {msg}, Error: {e}")