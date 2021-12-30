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
import time
import uuid

from cortx.utils.log import Log
from cortx.utils.conf_store import Conf

from ha.const import _DELIM
from ha import const
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.event_analyzer.event_analyzer_exceptions import EventParserException
from ha.core.system_health.const import CLUSTER_ELEMENTS, HEALTH_EVENTS, EVENT_SEVERITIES
from ha.core.system_health.status_mapper import StatusMapper
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
            Log.debug(f"Parsed {event} schema")
            health_event = HealthEvent.dict_to_object(event)
            Log.info(f"Event {event[EVENT_ATTRIBUTES.EVENT_ID]} is parsed and converted to object.")
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
                EVENT_ATTRIBUTES.EVENT_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_ID],
                EVENT_ATTRIBUTES.EVENT_TYPE : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_TYPE],
                EVENT_ATTRIBUTES.SEVERITY : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SEVERITY],
                EVENT_ATTRIBUTES.SITE_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.SITE_ID],
                EVENT_ATTRIBUTES.RACK_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.RACK_ID],
                EVENT_ATTRIBUTES.CLUSTER_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.CLUSTER_ID],
                EVENT_ATTRIBUTES.STORAGESET_ID : "TBD",
                EVENT_ATTRIBUTES.NODE_ID : node_id, # TODO: Temporary fix till IEM framework is available.
                EVENT_ATTRIBUTES.HOST_ID : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.HOST_ID],
                EVENT_ATTRIBUTES.RESOURCE_TYPE : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SPECIFIC_INFO][ALERT_ATTRIBUTES.MODULE].lower(),
                EVENT_ATTRIBUTES.TIMESTAMP : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.INFO][ALERT_ATTRIBUTES.EVENT_TIME],
                EVENT_ATTRIBUTES.RESOURCE_ID : node_id,
                EVENT_ATTRIBUTES.SPECIFIC_INFO : iem_alert[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.SPECIFIC_INFO]
            }
            # To be removed after HA starts populating IEM messages
            if event.get(EVENT_ATTRIBUTES.RESOURCE_TYPE) == CLUSTER_ELEMENTS.NODE.value and event.get(EVENT_ATTRIBUTES.SEVERITY) == EVENT_SEVERITIES.WARNING.value:
                event[EVENT_ATTRIBUTES.EVENT_TYPE] = HEALTH_EVENTS.FAILED.value

            Log.debug(f"Parsed {event} schema")
            health_event = HealthEvent.dict_to_object(event)
            Log.info(f"Event {event[EVENT_ATTRIBUTES.EVENT_ID]} is parsed and converted to object.")
            return health_event

        except Exception as e:
            raise EventParserException(f"Failed to parse IEM. Message: {msg}, Error: {e}")


class ClusterResourceParser(Parser):
    """
    Subscriber for event analyzer to pass msg.
    """

    def __init__(self, conf_store=None):
        """
        Init method.
        """
        super(ClusterResourceParser, self).__init__()
        ConfigManager.init("event_analyzer")
        self._conf_store = conf_store
        self.cluster_id = Conf.get(const.HA_GLOBAL_INDEX, f"COMMON_CONFIG{_DELIM}cluster_id")
        self.site_id = Conf.get(const.HA_GLOBAL_INDEX, f"COMMON_CONFIG{_DELIM}site_id")
        self.rack_id = Conf.get(const.HA_GLOBAL_INDEX, f"COMMON_CONFIG{_DELIM}rack_id")
        self.predefined_config = {"cluster_id": self.cluster_id, "site_id": self.site_id, "rack_id": self.rack_id}
        self.system_health_node_key_template = "cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/health"
        Log.info("ClusterResource Parser is initialized ...")

    def prepare_key(self, res_alert: dict) -> str:
        """Prepares a key to be searched in confstore"""
        replacable_patterns = re.findall(r"\$\w+", self.system_health_node_key_template)
        for pattern in replacable_patterns:
            replacable_string = pattern[1:]
            if replacable_string in self.predefined_config:
                config_val = self.predefined_config[replacable_string]
                key = self.system_health_node_key_template.replace(pattern, config_val)
            else:
                config_val = res_alert["_resource_name"]
                key = self.system_health_node_key_template.replace(pattern, config_val)
            self.system_health_node_key_template = key
        return self.system_health_node_key_template

    def _create_health_event_format(self, cluster_resource_alert: dict, specific_info: dict = None) -> dict:
        """
        Creates the defined structure to send an helath event to system health
        for further processing
        """
        timestamp = str(int(time.time()))
        event_id = timestamp + str(uuid.uuid4().hex)
        node_id = cluster_resource_alert["_resource_name"]
        resource_type = cluster_resource_alert["_resource_type"]
        event_type = cluster_resource_alert["_event_type"]
        timestamp = cluster_resource_alert["_timestamp"]

        event = {
                    EVENT_ATTRIBUTES.EVENT_ID : event_id,
                    EVENT_ATTRIBUTES.EVENT_TYPE : event_type,
                    EVENT_ATTRIBUTES.SEVERITY : StatusMapper.EVENT_TO_SEVERITY_MAPPING[event_type],
                    EVENT_ATTRIBUTES.SITE_ID : self.site_id, # TODO: Should be fetched from confstore
                    EVENT_ATTRIBUTES.RACK_ID : self.rack_id, # TODO: Should be fetched from confstore
                    EVENT_ATTRIBUTES.CLUSTER_ID : self.cluster_id, # TODO: Should be fetched from confstore
                    EVENT_ATTRIBUTES.STORAGESET_ID : node_id,
                    EVENT_ATTRIBUTES.NODE_ID : node_id,
                    EVENT_ATTRIBUTES.HOST_ID : node_id,
                    EVENT_ATTRIBUTES.RESOURCE_TYPE : resource_type,
                    EVENT_ATTRIBUTES.TIMESTAMP : timestamp,
                    EVENT_ATTRIBUTES.RESOURCE_ID : node_id,
                    EVENT_ATTRIBUTES.SPECIFIC_INFO : specific_info
                }

        Log.debug(f"Parsed {event} schema")
        # Log.error(f"########## Parsed {event} schema")
        return event

    @staticmethod
    def _get_sys_health_key_val(key_to_search: str, conf_store) -> (dict,int,str):
        """
        Fetches the value from confstore for the given key
        returns value in dictionary format assoscoiated with
        the key. and value of pod_restart_val assoscaited with
        that key(node)
        conf_store.get will return following strcture
        {'cortx/ha/v1/cortx/ha/system/cluster/d6b77d52dc0a4fdc8dabd036f57b49eb/site/1/rack/1/node/8f6e76bd96f44fdd8abc7fd7589bf925/health': '{"events": [{"event_timestamp": "1640685608", "created_timestamp": "1640685610", "status": "online", "specific_info": {"generation_id": "cortx-data-pod-ssc-vm-g2-rhev4-2693-68fb57f57-h9kzf", "pod_restart": 0}}], "action": {"modified_timestamp": "1640685610", "status": "pending"}
        """
        sys_health_key_val = {}
        current_pod_restart_val = None
        sys_health_key_val = conf_store.get(key_to_search)
        if sys_health_key_val:
            events_str = sys_health_key_val["cortx/ha/v1/"+key_to_search]
            # the dict value of sys health key will be string and hence str
            # to dict conversion needed
            events = json.loads(events_str)
            # Get the first latest event to find the pod_restart value
            current_event = events["events"][0]
            current_pod_restart_val = current_event["specific_info"]["pod_restart"]
            generation_id = current_event["specific_info"]["generation_id"]
        # Log.error(f'$$$$$$$$$$$$$$$$$ {events}')
        return events, current_pod_restart_val, generation_id

    def _create_health_event_object(self, cluster_resource_alert: dict, specific_info: dict = None) -> HealthEvent:
        """
        convert health event dictionary to object using HealthEvent class
        """
        health_event = None
        health_event_format = self._create_health_event_format(cluster_resource_alert, specific_info)
        health_event = HealthEvent.dict_to_object(health_event_format)
        Log.debug(f"Event {health_event} is parsed and converted to object.")
        return health_event

    def parse_event(self, msg: str) -> list:
        """
        Parse event.
        Args:
            msg (str): Msg
        """
        try:
            message = json.dumps(ast.literal_eval(msg))
            cluster_resource_alert = json.loads(message)
            health_event_list = []
            if self._conf_store is not None:
                key_to_search = self.prepare_key(cluster_resource_alert)
                # Log.error(key_to_search)
                if self._conf_store.key_exists(key_to_search):
                    sys_health_key_val, current_pod_restart_val, gen_id = \
                       ClusterResourceParser._get_sys_health_key_val(key_to_search, self._conf_store)
                    # Log.error(f'{cluster_resource_alert["_generation_id"]} {gen_id}')
                    if cluster_resource_alert["_generation_id"] != gen_id:
                        if current_pod_restart_val is not None and current_pod_restart_val:
                            # If the incoming generation id doesn't match with already stored
                            # value and assosciated pod_restart count is 1. That means,
                            # its a pod restart case and this alert is already handled
                            sys_health_key_val["events"][0]["specific_info"]["pod_restart"] = 0
                            self._conf_store.update(key_to_search, json.dumps(sys_health_key_val))
                        else:
                            # generation id is different and pod_restart value assosciated with
                            # this pod is also zero. Means, pod restart happened and online event
                            # came first(before delete event). So, handle two events here itself

                            # One potantial problem in sending two alerts here is if after pod
                            # comes up on some other node, then failed alert "node" will be wrongly sent.
                            current_alert_received = json.dumps(cluster_resource_alert)
                            # First send the failure alert
                            cluster_resource_alert["_event_type"] = "failed"
                            health_event = self._create_health_event_object(cluster_resource_alert, {"generation_id": gen_id, "pod_restart": 1})
                            health_event_list.append(health_event)
                            # and now append the incoming online alert
                            health_event = self._create_health_event_object(json.loads(current_alert_received), {"generation_id": cluster_resource_alert["_generation_id"],"pod_restart": 1})
                            health_event_list.append(health_event)
                    else:
                        # Normal pod failure occured where node id and its assosciated machine
                        # id is alredy present in the store
                        health_event = self._create_health_event_object(cluster_resource_alert, {"generation_id": gen_id, "pod_restart": 0})
                        health_event_list.append(health_event)
                # TODO: Check if this can be out of first if itself
                else:
                    # Handle altogether a new node event here
                    health_event = self._create_health_event_object(cluster_resource_alert, {"generation_id": cluster_resource_alert["_generation_id"], "pod_restart": 0})
                    health_event_list.append(health_event)
            else:
                # TODO: Check if exception needs to be raised here
                raise EventParserException("Failed to parse cluster resource alert. \
                                             ConfStore object is None")
            return health_event_list

        except Exception as err:
            raise EventParserException(f"Failed to parse cluster resource alert. Message: {msg}, Error: {err}")
