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

from cortx.utils.log import Log
from cortx.utils.process import SimpleProcess
from ha.core.error import HACommandTerminated

# TODO: Move to utils package in SimpleProcess
class SimpleCommand:
    def __init__(self):
        pass

    def run_cmd(self, cmd, check_error=True, secret=None):
        """
        Run command and throw error if cmd failed

        Args:
            cmd ([string]): Command to execute on system.

        Raises:
            Exception: raise command failed exception.
            HACommandTerminated: Command termineted exception

        Returns:
            string: Command output.
        """
        try:
            cmd_help = cmd.replace(secret, "****") if secret is not None else cmd
            _err = ""
            _proc = SimpleProcess(cmd)
            _output, _err, _rc = _proc.run(universal_newlines=True)
            Log.debug(f"cmd: {cmd_help}, output: {_output}, err: {_err}, rc: {_rc}")
            if _rc != 0 and check_error:
                    Log.error(f"cmd: {cmd_help}, output: {_output}, err: {_err}, rc: {_rc}")
                    raise Exception(f"Failed to execute {cmd_help}")
            return _output, _err, _rc
        except Exception as e:
                Log.error(f"Failed to execute  {cmd_help} Error: {e}.")
                raise HACommandTerminated(f"Failed to execute  {cmd_help} Error: {e}.")
