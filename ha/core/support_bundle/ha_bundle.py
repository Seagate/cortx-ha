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

from cortx.utils.schema.payload import Tar
from cortx.utils.process import SimpleProcess

from ha import const
from ha.core.error import SupportBundleError

class HABundle:

    def __init__(self):
        """
        This Class generates the Support Bundle for Component HA.
        This method will generate bundle for HA and include the logs in it.
        """
        # TODO Add setup detection logic
        self._id = None
        self._path = None

    def process_request(self, action, args, output):
        """
        Process support Bundle request

        Args:
            action (string): Action to be taken for support bundle.
            args (dict): Parameter for support bundle
        """
        self._output = output
        self._id = args.id
        self._path = args.path
        getattr(self, args.bundle_action)()

    def create(self):
        """
        Create support bundle on given path.
        """
        self._add_more_log()
        export_path = self._export_logs(self._check_files())
        self._output.output(f"Successfully created support bundle at {export_path}")

    def _add_more_log(self):
        """
        Collect Extra Log
        """
        cmd_list = [const.PCS_STATUS, const.PCS_FAILCOUNT_STATUS]
        with open(const.HA_CMDS_OUTPUT, "w") as file:
            for cmd in cmd_list:
                _err = ""
                _proc = SimpleProcess(cmd)
                _output, _err, _rc = _proc.run(universal_newlines=True)
                file.write("\n\n\n********************************\n")
                file.write(f"Command: {cmd}\nReturn Code: {_rc}\nOutput:\n")
                file.write(f"{_output}")
                file.write(f"Error if any: {_err}\n\n\n")

    def _check_files(self, ha_log_list=const.SUPPORT_BUNDLE_LOGS):
        """
        Check all support bundle file for HA
        and provide list of available file
        """
        ha_logs = list(ha_log_list)
        with open(const.SUPPORT_BUNDLE_ERR, "w") as file:
            for _path in ha_log_list:
                if not os.path.exists(_path):
                    ha_logs.remove(_path)
                    file.write(f"For support bundle {_path} is not available")
        return ha_logs

    def _export_logs(self, ha_logs):
        """
        Create tar for support bundle logs

        Args:
            ha_logs (list): List of support bundle files
        """
        path = os.path.join(self._path, "HA")
        os.makedirs(path, exist_ok=True)
        # Generate Tar file for Logs Folder.
        tar_file_name = os.path.join(path, f"ha_{self._id}.tar.gz")
        Tar(tar_file_name).dump(ha_logs)
        if not os.path.exists(tar_file_name):
            raise SupportBundleError(f"Failed to create support bundle at {tar_file_name}")
        return tar_file_name

class CortxHABundle(HABundle):

    def __init__(self):
        """
        This Class generates the Support Bundle for Component cortx HA.
        This method will generate bundle for HA and include the logs in it.
        """
        super(CortxHABundle, self).__init__()

    def _add_more_log(self):
        """
        Collect HA commands Log
        """
        pass

    def _check_files(self, ha_log_list=const.CORTX_SUPPORT_BUNDLE_LOGS):
        """
        Check all support bundle file for HA
        and provide list of available file
        """
        return super()._check_files(ha_log_list)