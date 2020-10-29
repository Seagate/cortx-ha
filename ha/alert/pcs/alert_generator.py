#!/usr/bin/env python3

# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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
from string import Template

from cortx.utils.schema.conf import Conf
from cortx.utils.log import Log
from cortx.utils.schema.payload import Json

from ha import const
from ha.alert.alert_generator import AlertGenerator

class PcsAlertGenerator(AlertGenerator):
    def __init__(self):
        """
        Initialize HA alert
        """
        self._crm_env = self._get_env()
        Conf.init()
        Conf.load(const.IEM_INDEX, Json(const.IEM_SCHAMA))
        self._known_iem_event = [ "node", "resource", "fencing"]

    def _get_env(self):
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

    def process_event(self, event=""):
        """
        Process event for alert
        """
        self._validate_pacemaker()
        self._load_recipient()
        try:
            event = self._validate_event(event)
            # TODO: Add event class for each event
            if event == "fencing":
                self.send_fencing_log()
            else:
                getattr(self, "send_"+event+"_iem")()
        except Exception as e:
            Log.error(f"{traceback.format_exc()}, {e}")

    def _validate_pacemaker(self):
        """
        Validate pacemaker
        """
        if "CRM_alert_version" not in self._crm_env.keys():
            syslog.syslog(f"Pacemaker Alert: {sys.argv[0]} must be run by Pacemaker version 1.1.15 or later")
            sys.exit(1)

    def _load_recipient(self):
        """
        Load recipient for pacemaker alert
        """
        # TODO Take log level from ha.conf
        log_path = self._crm_env["CRM_alert_recipient"]
        if not os.path.exists(log_path):
            syslog.syslog("Pacemaker Alert: Invalid path for pacemaker recipient alert")
        Log.init(service_name="pcmk_alert", log_path=log_path, level="INFO")

    def _validate_event(self, event):
        """
        Validate event
        """
        event = event if event != "" else self._crm_env["CRM_alert_kind"]
        if event in self._known_iem_event:
            Log.debug(f" Validating event: {str(self._crm_env)}")
            return event
        Log.info(f"Identified unknown event: {str(self._crm_env)}")

    def send_node_iem(self):
        """
        Send node level IEM to user
        """
        node = self._crm_env['CRM_alert_node']
        desc = self._crm_env['CRM_alert_desc']
        Log.info(f"Node {node} is now {desc}")
        node_iems = Conf.get(const.IEM_INDEX, "nodes.any_host")
        if desc in node_iems.keys():
            msg = Template(node_iems[desc]["IEM"]).substitute(host=node)
            Log.info(f"{msg}")
            syslog.syslog(msg)
        else:
            Log.warn(f"Invalid module for node level action {str(self._crm_env)}")

    def send_resource_iem(self):
        """
        Send Resource level IEM to user
        """
        task = self._crm_env['CRM_alert_task']
        resource = self._crm_env['CRM_alert_rsc']
        node = self._crm_env['CRM_alert_node']
        desc = self._crm_env['CRM_alert_desc']
        rc = self._crm_env['CRM_alert_target_rc']
        Log.info(f"Resource operation {task} for {resource} on {node}: Desc: {desc}, rc: {rc}")
        res_iems = Conf.get(const.IEM_INDEX, "resources")
        if resource in res_iems.keys():
            if task in res_iems[resource].keys():
                msg = Template(res_iems[resource][task]["IEM"]).substitute(host=node)
                Log.info(f"{msg}")
                syslog.syslog(msg)

    def send_fencing_log(self):
        """
        Send fencing level IEM to user
        """
        # Note: no iem need for fencing as it detected by node start/stop.
        Log.info(f"Fencing {self._crm_env['CRM_alert_desc']}")