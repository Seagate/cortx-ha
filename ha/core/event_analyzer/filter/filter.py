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
from ha.core.error import EventAnalyzerError

class Filter(metaclass=abc.ABCMeta):
    """ Base class to filter alert """

    def __init__(self):
        """
        Init method
        """
        pass

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

    def __init__(self):
        """
        Init method
        """
        #Loads alert flter rules in the configuration
        ConfigManager.load_filter_rules()

        #Get filter type and resource types list from the alert rule file
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

        except Exception as e:
            raise EventAnalyzerError(f"Failed to filter event. Message: {msg}, Error: {e}")

        return Alert_required
