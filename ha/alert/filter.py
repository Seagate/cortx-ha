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
from cortx.utils.conf_store.conf_store import Conf
from cortx.utils.log import Log
from ha.alert.const import ALERTS
from ha.const import ALERT_EVENT_INDEX
from ha.core.config.config_manager import ConfigManager
from ha.alert.alert_exceptions import AlertEventFilterError


class Filter(metaclass=abc.ABCMeta):
    """ Base class to filter alert """

    def __init__(self):
        """
        Init method
        """
        self.crm_env = None
        # Loads Alert event filter rules in the configuration
        ConfigManager.load_alert_events_rules()

    def initialize_crm(self, crm_env: dict):
        self.crm_env = crm_env

    @abc.abstractmethod
    def filter_event(self):
        """
        Filter event based on Node, Resource and Fencing type.
        Args:
            msg (str): Msg
        """
        pass


class AlertEventFilter(Filter):
    """ Filter unnecessary alert. """

    def __init__(self):
        """
        Init method
        """
        super().__init__()

        # Get filter type and resource types list from the alert monitor rule file
        self.alert_filter_components = Conf.get(ALERT_EVENT_INDEX, ALERTS.PK_ALERT_EVENT_COMPONENTS)
        self.alert_filter_modules = Conf.get(ALERT_EVENT_INDEX, ALERTS.PK_ALERT_EVENT_COMPONENT_MODULES)
        self.alert_filter_module_operations = Conf.get(ALERT_EVENT_INDEX, ALERTS.PK_ALERT_EVENT_OPERATIONS)
        Log.info("AlertEventFilter initialized.")

    def filter_event(self):
        """
        Filter event based on Node, Resource and Fencing type.
        Args:
            msg (str): Msg
        """
        ha_required_alert_module = None
        ha_required_alert_module_operation = None

        if self.crm_env is None:
            raise AlertEventFilterError(f"Identified empty events: {str(self.crm_env)}")

        try:
            alert_filter_module = self.crm_env["CRM_alert_kind"]
            alert_filter_module_operation = self.crm_env["CRM_alert_desc"]

            if alert_filter_module.lower() in self.alert_filter_modules.get(ALERTS.REQUIRED_COMPONENT):
                ha_required_alert_module = alert_filter_module

            if ha_required_alert_module and alert_filter_module_operation.lower() in self.alert_filter_module_operations.get(
                    ha_required_alert_module):
                ha_required_alert_module_operation = alert_filter_module_operation

            return ha_required_alert_module, ha_required_alert_module_operation
        except Exception as e:
            Log.error(f"Error occurred in alert event filter: {str(e)}")
            return ha_required_alert_module, ha_required_alert_module_operation
