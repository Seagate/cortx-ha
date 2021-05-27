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
from cortx.utils.conf_store.conf_store import Conf
from cortx.utils.log import Log
from ha import const
from ha.core.config.config_manager import ConfigManager
from ha.core.event_analyzer.event_analyzer_exceptions import EventFilterException
from ha.core.event_analyzer.event_analyzer_exceptions import InvalidFilterRules

class Filter(metaclass=abc.ABCMeta):
    """ Base class to filter alert """

    def __init__(self):
        """
        Load filter rules.
        """
        #Loads alert filter rules in the configuration
        ConfigManager.load_filter_rules()

    @staticmethod
    def validate_filter(message_type: str):
        """
        Filter type should be one of INCLUSION or EXCLUSION
        """
        filter_type = Conf.get(const.ALERT_FILTER_INDEX, f"{message_type}.filter_type")
        if filter_type not in [const.INCLUSION, const.EXCLUSION]:
            raise InvalidFilterRules(f"Invalid filter type {filter_type}")

    @abc.abstractmethod
    def filter_event(self, msg: str) -> bool:
        """
        Filter event.

        Args:
            msg (str): Msg
        """
        pass

class AlertFilter(Filter):
    """ Filter unnecessary alert. """

    MESSAGE_TYPE = "alert"

    def __init__(self):
        """
        Init method
        """
        super(AlertFilter, self).__init__()
        #Get filter type and resource types list from the alert rule file
        AlertFilter.validate_filter(AlertFilter.MESSAGE_TYPE)
        self.filter_type = Conf.get(const.ALERT_FILTER_INDEX, f"{AlertFilter.MESSAGE_TYPE}.filter_type")
        self.resource_types_list = Conf.get(const.ALERT_FILTER_INDEX, f"{AlertFilter.MESSAGE_TYPE}.resource_type")

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
            else:
                # EXCLUSION Rules
                if resource_type not in self.resource_types_list:
                    Alert_required = True

            return Alert_required

        except Exception as e:
            raise EventFilterException(f"Failed to filter event. Message: {msg}, Error: {e}")

class IEMFilter(Filter):

    MESSAGE_TYPE = "iem"

    def __init__(self):
        """
        Init method
        """
        super(IEMFilter, self).__init__()
        IEMFilter.validate_filter(IEMFilter.MESSAGE_TYPE)

    def filter_event(self, msg: str) -> bool:
        """
        Filter event.
        Args:
            msg (str): Msg
        """
        return False
