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
from enum import Enum
from cortx.utils.conf_store.conf_store import Conf
from cortx.utils.log import Log
from ha import const
from ha.core.config.config_manager import ConfigManager
from ha.core.error import EventAnalyzerError


class MESSAGETYPE(Enum):
    ALERT = "ALERT"
    IEM = "IEM"


class Filter(metaclass=abc.ABCMeta):
    """ Base class to filter alert """

    def __init__(self):
        """
        Init method
        """
        # Loads IEM filter rules in the configuration
        ConfigManager.load_filter_rules()

    @abc.abstractmethod
    def filter_event(self, msg: str) -> bool:
        """
        Filter event.
        Args:
            msg (str): Msg
        """
        pass

    @staticmethod
    def get_msg_type(msg: dict) -> str:
        """
        Check if the msg type is iem or alert
        """
        msg_type = msg.get("sensor_response_type")
        return msg_type["info"]["resource_type"]


class AlertFilter(Filter):
    """ Filter unnecessary alert. """

    def __init__(self):
        """
        Init method
        """
        super().__init__()

        # Get filter type and resource types list from the alert rule file
        self.filter_type = Conf.get(const.ALERT_FILTER_INDEX, "alert.filter_type")
        self.resource_types_list = Conf.get(const.ALERT_FILTER_INDEX, "alert.resource_type")

    def filter_event(self, msg: str) -> bool:
        """
        Filter event.
        Args:
            msg (str): Msg
        """
        try:
            Alert_required = False
            message = json.loads(msg)

            msg_type = message.get("actuator_response_type")
            if msg_type is not None:
                return Alert_required

            msg_type = message.get("sensor_response_type")
            resource_type = msg_type["info"]["resource_type"]

            if self.filter_type == const.INCLUSION:
                if resource_type in self.resource_types_list:
                    Alert_required = True
            elif self.filter_type == const.EXCLUSION:
                if resource_type not in self.resource_types_list:
                    Alert_required = True
            else:
                Log.error("Invalid filter type in the event filter rules")

            return Alert_required

        except Exception as e:
            raise EventAnalyzerError(f"Failed to filter event. Message: {msg}, Error: {e}")


class IEMFilter(Filter):
    """ Filter IEM consumed by watcher """

    def __init__(self):
        """
        Init method
        """
        super().__init__()

        # Get filter type and resource types list from the IEM rule file
        self.filter_type = Conf.get(const.ALERT_FILTER_INDEX, "iem.filter_type")
        self.components_list = Conf.get(const.ALERT_FILTER_INDEX, "iem.components")
        self.modules_dict = Conf.get(const.ALERT_FILTER_INDEX, "iem.modules")
        self.validate()

    def validate(self):
        """
        validate filter type
        """
        if self.filter_type not in [const.INCLUSION, const.EXCLUSION]:
            Log.error("Invalid IEM filter type in the event IEM filter rules")
            raise EventAnalyzerError(f"Invalid IEM filter type `{self.filter_type}` in the event IEM filter rules")

    def filter_event(self, msg: str) -> bool:
        """
        Filter event.
        Args:
            msg (str): Msg
        """
        try:
            iem_required = False
            message = json.loads(msg)

            _actuator_response_type = message.get('actuator_response_type')
            if _actuator_response_type is not None:
                return iem_required

            _msg_type = Filter.get_msg_type(message)
            if _msg_type.lower() != MESSAGETYPE.IEM.value.lower():
                return iem_required

            _sensor_response_type = message.get('sensor_response_type')
            _component_type = _sensor_response_type['specific_info']['component']
            _module_type = _sensor_response_type['specific_info']['module']

            if self.filter_type == const.INCLUSION:
                if _component_type in self.components_list and _module_type in self.modules_dict.get(_component_type):
                    iem_required = True
            elif self.filter_type == const.EXCLUSION:
                if _component_type not in self.components_list or _module_type not in self.modules_dict.get(
                        _component_type):
                    iem_required = True

            return iem_required

        except Exception as e:
            raise EventAnalyzerError(f"Failed to filter IEM event. Message: {msg}, Error: {e}")
