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

from ha.core.system_health.model.health_event import HealthEvent
from ha.core.event_analyzer.event_analyzer_exceptions import EventParserException
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.config.config_manager import ConfigManager
from ha.const import PVTFQDN_TO_NODEID_KEY, ALERT_ATTRIBUTES, EVENT_ATTRIBUTES

class Parser(metaclass=abc.ABCMeta):
    """
    Subscriber for event analyzer to pass msg.
    """

    def __init__(self):
        """
        Init method.
        """
        self._confstore = ConfigManager.get_confstore()

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
                EVENT_ATTRIBUTES.EVENT_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_ID],
                EVENT_ATTRIBUTES.EVENT_TYPE : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_TYPE],
                EVENT_ATTRIBUTES.SEVERITY : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SEVERITY],
                EVENT_ATTRIBUTES.SITE_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.SITE_ID],
                EVENT_ATTRIBUTES.RACK_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.RACK_ID],
                EVENT_ATTRIBUTES.CLUSTER_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.CLUSTER_ID],
                EVENT_ATTRIBUTES.STORAGESET_ID : "TBD",
                EVENT_ATTRIBUTES.NODE_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.NODE_ID],
                EVENT_ATTRIBUTES.HOST_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.HOST_ID],
                EVENT_ATTRIBUTES.RESOURCE_TYPE : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.RESOURCE_TYPE],
                EVENT_ATTRIBUTES.TIMESTAMP : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.EVENT_TIME],
                EVENT_ATTRIBUTES.RESOURCE_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.RESOURCE_ID],
                EVENT_ATTRIBUTES.SPECIFIC_INFO : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SPECIFIC_INFO]
            }

            health_event = HealthEvent.dict_to_object(event)

            return health_event

        except Exception as e:
            raise EventParserException(f"Failed to parse alert. Message: {msg}, Error: {e}")

class IEMParser(Parser):
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
            iem_alert = json.loads(msg)

            # Parse hostname and convert to node id
            iem_description = iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.DESCRIPTION]
            hostname = re.split("=", re.split(";", re.findall("host=.+", iem_description)[0])[0])[1]
            key_val = self._confstore.get(f"{PVTFQDN_TO_NODEID_KEY}/{hostname}")
            _, node_id = key_val.popitem()

            event = {
                EVENT_ATTRIBUTES.EVENT_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_ID],
                EVENT_ATTRIBUTES.EVENT_TYPE : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_TYPE],
                EVENT_ATTRIBUTES.SEVERITY : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SEVERITY],
                EVENT_ATTRIBUTES.SITE_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.SITE_ID],
                EVENT_ATTRIBUTES.RACK_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.RACK_ID],
                EVENT_ATTRIBUTES.CLUSTER_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.CLUSTER_ID],
                EVENT_ATTRIBUTES.STORAGESET_ID : "TBD",
                EVENT_ATTRIBUTES.NODE_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.NODE_ID],
                EVENT_ATTRIBUTES.HOST_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.HOST_ID],
                EVENT_ATTRIBUTES.RESOURCE_TYPE : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SPECIFIC_INFO][ALERT_ATTRIBUTES.MODULE].lower(),
                EVENT_ATTRIBUTES.TIMESTAMP : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.EVENT_TIME],
                EVENT_ATTRIBUTES.RESOURCE_ID : node_id,
                EVENT_ATTRIBUTES.SPECIFIC_INFO : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SPECIFIC_INFO]
            }

            health_event = HealthEvent.dict_to_object(event)
            return health_event

        except Exception as e:
            raise EventParserException(f"Failed to parse IEM. Message: {msg}, Error: {e}")
