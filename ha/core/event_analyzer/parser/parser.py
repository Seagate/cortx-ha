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
    def __init__(self):
        """
        Init method
        """
        pass

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
        Init method
        """
        #Loads event parser interfaces in the config
        ConfigManager.load_event_parser_interfaces()

    def parse_event(self, msg: str) -> HealthEvent:
        """
        Parse event.
        Args:
            msg (str): Msg
        """
        alert = json.loads(msg)

        EventIdKeyList = Conf.get(const.EVENT_PARSER_INDEX, "alert.standard.event_id").split(".")

        #Use Event id key list and access the dict
        event_id = alert.get('sensor_response_type').get('alert_id')
        event_type = None
        severity = None
        site_id = None
        rack_id = None
        cluster_id = None
        storageset_id = None
        node_id = None
        host_id = None
        resource_type = None
        timestamp = None
        resource_id = None
        specific_info = None

        health_event = HealthEvent(event_id, event_type, severity, site_id, rack_id, cluster_id, storageset_id, node_id, host_id, resource_type, timestamp, resource_id, specific_info)
        return health_event