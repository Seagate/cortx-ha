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

from ha import const
from cortx.utils.log import Log
from cortx.utils.conf_store.conf_store import Conf
from ha.core.config.config_manager import ConfigManager
from ha.alert.alert_factory import AlertFactory

# Can be moved to const.py
REQUIRED_EVENTS = ["node" , "resource"]

class AlertMonitor:

    def __init__(self):
        """
        Init alert monitor
        """
        super(AlertMonitor, self).__init__()
        ConfigManager.init("alert_monitor")

        # get environment variables
        self.crm_env = self.get_env()

    def get_env(self):
        """
        Get env variable and parameter provided by pacemaker
        """
        try:
            key = None
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

        self.validate_pacemaker()
        self.load_recipient()

        # validate event type and get class
        try:
             event_type = self.validate_event()
             # Redirect the alert to appropriate monitor for further processing
             self.redirect_alert(event_type)
        except Exception as e:
            Log.error(f"{traceback.format_exc()}, {e}")

    def redirect_alert(self, event_type):
        """
        Get appropriate class based on event  and redirect alert to it
        """
        alert_monitor = AlertFactory.get_alert_monitor_instance(event_type)
        alert = alert_monitor()
        alert.process_alert()


    def validate_pacemaker(self):
        """
        Validate pacemaker
        """
        if "CRM_alert_version" not in self.crm_env.keys():
            syslog.syslog(f"Pacemaker Alert: {sys.argv[0]} must be run by Pacemaker version 1.1.15 or later")
            Log.error(f"Pacemaker Alert: {sys.argv[0]} must be run by Pacemaker version 1.1.15 or later")
            sys.exit(1)

    def load_recipient(self):
        """
        Load recipient for pacemaker alert
        """
        log_path = self.crm_env["CRM_alert_recipient"]
        log_level = Conf.get(const.HA_GLOBAL_INDEX, "LOG.level")
        if not os.path.exists(log_path):
            syslog.syslog("Pacemaker Alert: Invalid path for pacemaker recipient alert")
        Log.init(service_name="pcmk_alert", log_path=log_path, level=log_level)

    def validate_event(self):
        """
        Validate event
        """
        event_type = self.crm_env["CRM_alert_kind"]

        if event_type in REQUIRED_EVENTS:
            Log.debug(f" Validating event: {str(self.crm_env)}")
            return event_type
        Log.info(f"Identified unknown event: {str(self.crm_env)}")
        return ""

    def create_IEM(self):
        pass
