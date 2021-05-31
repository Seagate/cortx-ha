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
from cortx.utils.log import Log
from ha.execute import SimpleCommand
from ha.setup.setup_error import AlertConfigError

class AlertConfig:

    ALERT_SCRIPT_PATH = ["/usr/local/bin/pcmk_alert", "/usr/bin/pcmk_alert"]
    ALERT_ID = "iem_alert"
    RECIPIENT_KEY = "sender_type"
    RECIPIENT_VALUE = "syslog"

    def __init__(self):
        self._process = SimpleCommand()

    def is_alert_exists(self) -> bool:
        """
        Check if alert already exists.
        """
        Log.info("Checking pacemaker alert if already exists ...")
        output, error, rc = self._process.run_cmd(f"pcs alert")
        for line in output.split("\n"):
            if AlertConfig.ALERT_ID in line:
                return True
        return False

    def create_alert(self):
        """
        Manage alert resource.
        """
        Log.info("Creating pacemaker alert ...")
        if self.is_alert_exists():
            self.delete_alert()
        path: str = AlertConfig._get_script()
        try:
            self._process.run_cmd(f"pcs alert create id={AlertConfig.ALERT_ID} description=send_iem_alerts path={path}")
            self._process.run_cmd(f"pcs alert recipient add {AlertConfig.ALERT_ID} id={AlertConfig.RECIPIENT_KEY} value={AlertConfig.RECIPIENT_VALUE}")
            Log.info(f"Alert {AlertConfig.ALERT_ID} created successfully.")
        except Exception as e:
            raise AlertConfigError(f"Failed to create alert {AlertConfig.ALERT_ID} Error: {e}")

    def delete_alert(self):
        """
        Delete alert on current node.
        """
        if not self.is_alert_exists():
            return
        Log.info("Deleating pacemaker alert ...")
        self._process.run_cmd(f"pcs alert remove {AlertConfig.ALERT_ID}")
        Log.info(f"Alert {AlertConfig.ALERT_ID} is deleted")

    @staticmethod
    def _get_script() -> str:
        """
        Get alert script

        Raises:
            CreateResourceConfigError: Raise error if script missing
        """
        path: str = None
        for script in AlertConfig.ALERT_SCRIPT_PATH:
            if os.path.isfile(script):
                path = script
                break
        if path is None:
            raise AlertConfigError(f"Failed to create alert missing {str(AlertConfig.ALERT_SCRIPT_PATH)} file.")
        return path
