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

import traceback
from cortx.utils.log import Log
from ha.core.config.config_manager import ConfigManager
from ha.core.error import HAInvalidCommand
from ha.cli.command_factory import CmdFactory
from ha.cli.exec.commandExecutor import CLIUsage
from ha.cli.exec.commandExecutor import CommandExecutor as cmdExecutor
from ha.core.error import HACommandTerminated

class Command:
    """  Parse the CLI and call appropriate executor """
    def __init__(self):
        ConfigManager.init("cortxcli")
        self.module_name = None
        self.operation_name = None
        self.options = None

    def parse(self, args: list) -> None:
        """ Parse the CLI string to identify parameters"""
        self.module_name, self.operation_name, _ = CmdFactory.parse(args)

    def get_class(self, cmd_exec: cmdExecutor):
        """ get class object for the appropriate executor """

        parts = cmd_exec.split('.')
        module = ".".join(parts[:-1])
        exec_mod = __import__(module)
        for comp in parts[1:]:
            exec_mod = getattr(exec_mod, comp)
        return exec_mod

    def process(self, args: list):
        """ Process the command """

        self.parse(args)
        command_executor = CmdFactory.get_executor(self.module_name, self.operation_name)
        exec_class = self.get_class(command_executor)
        # Call execute function of the appropriate executor class
        executor_class = exec_class()

        # Raise exception if user does not have proper permissions
        executor_class.validate_permissions()

        if executor_class.validate():
            try:
                executor_class.execute()
            except Exception as err:
                Log.error(f"{traceback.format_exc()}, {err}")
                raise HACommandTerminated(f"CLI execution failed, Error: {err}")


"""
SupportBundleCommand is currently broken, so removed the code.
This will be added when the support bundle user story [ EOS-17931 ] is started
"""
