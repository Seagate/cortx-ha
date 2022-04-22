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
import ast
import json
import re

from cortx.utils.log import Log
from cortx.utils.conf_store import Conf

from ha.const import _DELIM
from ha import const
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.event_analyzer.event_analyzer_exceptions import EventParserException
from ha.core.system_health.const import CLUSTER_ELEMENTS, HEALTH_EVENTS, EVENT_SEVERITIES
from ha.core.system_health.status_mapper import StatusMapper
from ha.core.config.config_manager import ConfigManager
from ha.const import PVTFQDN_TO_NODEID_KEY, ALERT_ATTRIBUTES, EVENT_ATTRIBUTES as event_attr
from cortx.utils.event_framework.health import HealthAttr
from cortx.utils.event_framework.event import EventAttr


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

    def __init__(self):
        """
        Init method.
        """
        super(AlertParser, self).__init__()
        Log.info("Alert Parser is initialized ...")

    def parse_event(self, msg: str) -> HealthEvent:
        """
        Parse event.
        Args:
            msg (str): Msg
        """
        try:
            alert = json.loads(msg).get(ALERT_ATTRIBUTES.MESSAGE)

            event = {
                event_attr.EVENT_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_ID],
                event_attr.EVENT_TYPE : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_TYPE],
                event_attr.SEVERITY : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SEVERITY],
                event_attr.SITE_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.SITE_ID],
                event_attr.RACK_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.RACK_ID],
                event_attr.CLUSTER_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.CLUSTER_ID],
                event_attr.STORAGESET_ID : "TBD",
                event_attr.NODE_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.NODE_ID],
                event_attr.HOST_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.HOST_ID],
                event_attr.RESOURCE_TYPE : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.RESOURCE_TYPE],
                event_attr.TIMESTAMP : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.EVENT_TIME],
                event_attr.RESOURCE_ID : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.RESOURCE_ID],
                event_attr.SPECIFIC_INFO : alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SPECIFIC_INFO]
            }
            Log.debug(f"Parsed {event} schema")
            health_event = HealthEvent.dict_to_object(event)
            Log.info(f"Event {event[event_attr.EVENT_ID]} is parsed and converted to object.")
            return health_event

        except Exception as e:
            raise EventParserException(f"Failed to parse alert. Message: {msg}, Error: {e}")

class IEMParser(Parser):
    """
    Subscriber for event analyzer to pass msg.
    """

    def __init__(self):
        """
        Init method.
        """
        super(IEMParser, self).__init__()
        Log.info("IEM Parser is initialized ...")

    def parse_event(self, msg: str) -> HealthEvent:
        """
        Parse event.
        Args:
            msg (str): Msg
        """
        try:
            iem_alert = json.loads(msg).get(ALERT_ATTRIBUTES.MESSAGE)

            # Parse hostname and convert to node id
            iem_description = iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.DESCRIPTION]
            hostname = re.split("=", re.split(";", re.findall("host=.+", iem_description)[0])[0])[1]
            key_val = self._confstore.get(f"{PVTFQDN_TO_NODEID_KEY}/{hostname}")
            _, node_id = key_val.popitem()

            event = {
                event_attr.EVENT_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_ID],
                event_attr.EVENT_TYPE : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_TYPE],
                event_attr.SEVERITY : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SEVERITY],
                event_attr.SITE_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.SITE_ID],
                event_attr.RACK_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.RACK_ID],
                event_attr.CLUSTER_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.CLUSTER_ID],
                event_attr.STORAGESET_ID : "TBD",
                event_attr.NODE_ID : node_id, # TODO: Temporary fix till IEM framework is available.
                event_attr.HOST_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.HOST_ID],
                event_attr.RESOURCE_TYPE : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SPECIFIC_INFO][ALERT_ATTRIBUTES.MODULE].lower(),
                event_attr.TIMESTAMP : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.EVENT_TIME],
                event_attr.RESOURCE_ID : node_id,
                event_attr.SPECIFIC_INFO : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SPECIFIC_INFO]
            }
            # To be removed after HA starts populating IEM messages
            if event.get(event_attr.RESOURCE_TYPE) == CLUSTER_ELEMENTS.NODE.value and event.get(event_attr.SEVERITY) == EVENT_SEVERITIES.WARNING.value:
                event[event_attr.EVENT_TYPE] = HEALTH_EVENTS.FAILED.value

            Log.debug(f"Parsed {event} schema")
            health_event = HealthEvent.dict_to_object(event)
            Log.info(f"Event {event[event_attr.EVENT_ID]} is parsed and converted to object.")
            return health_event

        except Exception as e:
            raise EventParserException(f"Failed to parse IEM. Message: {msg}, Error: {e}")


class ClusterResourceParser(Parser):
    """
    Subscriber for event analyzer to pass msg.
    """

    def __init__(self):
        """
        Init method.
        """
        super(ClusterResourceParser, self).__init__()
        self.cluster_id = Conf.get(const.HA_GLOBAL_INDEX, f"COMMON_CONFIG{_DELIM}cluster_id")
        self.site_id = Conf.get(const.HA_GLOBAL_INDEX, f"COMMON_CONFIG{_DELIM}site_id")
        self.rack_id = Conf.get(const.HA_GLOBAL_INDEX, f"COMMON_CONFIG{_DELIM}rack_id")
        Log.info("ClusterResource Parser is initialized ...")

    def parse_event(self, msg: str) -> HealthEvent:
        """
        Parse event.
        Args:
            msg (str): Msg
        """
        try:
            message = json.dumps(ast.literal_eval(msg))
            cluster_resource_alert = json.loads(message)
            timestamp = cluster_resource_alert[EventAttr.EVENT_HEADER.value][EventAttr.TIMESTAMP.value]
            event_id = cluster_resource_alert[EventAttr.EVENT_HEADER.value][EventAttr.EVENT_ID.value]
            source = cluster_resource_alert[EventAttr.EVENT_PAYLOAD.value][HealthAttr.SOURCE.value]
            node_id = cluster_resource_alert[EventAttr.EVENT_PAYLOAD.value][HealthAttr.NODE_ID.value]
            resource_type = cluster_resource_alert[EventAttr.EVENT_PAYLOAD.value][HealthAttr.RESOURCE_TYPE.value]
            resource_id = cluster_resource_alert[EventAttr.EVENT_PAYLOAD.value][HealthAttr.RESOURCE_ID.value]
            event_type = cluster_resource_alert[EventAttr.EVENT_PAYLOAD.value][HealthAttr.RESOURCE_STATUS.value]
            specific_info = cluster_resource_alert[EventAttr.EVENT_PAYLOAD.value][HealthAttr.SPECIFIC_INFO.value]

            # Doesnot should be overwrite specific_info
            if resource_type == CLUSTER_ELEMENTS.NODE.value:
                if specific_info and specific_info["generation_id"]:
                    specific_info.update({"pod_restart": 0})

            event = {
                event_attr.SOURCE : source,
                event_attr.EVENT_ID : event_id,
                event_attr.EVENT_TYPE : event_type,
                event_attr.SEVERITY : StatusMapper.EVENT_TO_SEVERITY_MAPPING[event_type],
                event_attr.SITE_ID : self.site_id, # TODO: Should be fetched from confstore
                event_attr.RACK_ID : self.rack_id, # TODO: Should be fetched from confstore
                event_attr.CLUSTER_ID : self.cluster_id, # TODO: Should be fetched from confstore
                event_attr.STORAGESET_ID : node_id,
                event_attr.NODE_ID : node_id,
                event_attr.HOST_ID : node_id,
                event_attr.RESOURCE_TYPE : resource_type,
                event_attr.TIMESTAMP : timestamp,
                event_attr.RESOURCE_ID : resource_id,
                event_attr.SPECIFIC_INFO : specific_info
            }

            Log.debug(f"Parsed {event} schema")
            health_event = HealthEvent.dict_to_object(event)
            Log.debug(f"Event {event[event_attr.EVENT_ID]} is parsed and converted to object.")
            return health_event

        except Exception as err:
            raise EventParserException(f"Failed to parse cluster resource alert. Message: {msg}, Error: {err}")
