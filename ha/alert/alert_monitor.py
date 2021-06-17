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


import os
import sys
import syslog
import traceback

from cortx.utils.log import Log
from ha.core.config.config_manager import ConfigManager
from ha.alert.alert_factory import AlertFactory
from ha.alert.const import ALERTS
from ha.alert.filter import AlertEventFilter


class AlertMonitor:

    def __init__(self):
        """
        Init alert monitor
        """
        super(AlertMonitor, self).__init__()
        ConfigManager.init("alert_monitor")

        # get environment variables
        self.crm_env = self._get_env()
        alert_event_filter = AlertEventFilter()
        alert_event_filter.initialize_crm(self.crm_env)
        # Modules like Node, Resource, Fencing / Modules event like node became member or node lost
        self.alert_event_module, self.alert_event_type = alert_event_filter.filter_event()

    def _get_env(self):
        """
        Get env variable and parameter provided by pacemaker
        """
        crm_env = None
        try:
            crm_env = {}
            env = os.environ
            for key in env.keys():
                if key.startswith("CRM_"):
                    crm_env[key] = env[key]
            return crm_env
        except Exception as e:
            Log.error(e)
            return crm_env

    def process_alert(self):
        """
        Process alert
        """
        self._validate_pacemaker()
        self._load_recipient()

        # validate event type and get class
        try:
            # Redirect the alert to appropriate monitor for further processing
            if self.alert_event_module and self.alert_event_type:
                Log.info(f"Handling the event: {str(self.crm_env)}")
                self._redirect_alert()
            else:
                Log.info(f"Identified unknown / unsupported event by HA: {str(self.crm_env)}")
        except Exception as e:
            Log.error(f"{traceback.format_exc()}, {e}")

    def _redirect_alert(self):
        """
        Get appropriate class based on event  and redirect alert to it
        """
        alert_monitor = AlertFactory.get_alert_monitor_instance(self.alert_event_module)
        alert = alert_monitor()
        alert.process_alert()

    def _validate_pacemaker(self):
        """
        Validate pacemaker
        """
        if "CRM_alert_version" not in self.crm_env.keys():
            syslog.syslog(f"Pacemaker Alert: {sys.argv[0]} must be run by Pacemaker version 1.1.15 or later")
            Log.error(f"Pacemaker Alert: {sys.argv[0]} must be run by Pacemaker version 1.1.15 or later")
            sys.exit(1)

    def _load_recipient(self):
        """
        Load recipient for pacemaker alert
        """
        # TODO to be implemented when recipient is required
        pass
