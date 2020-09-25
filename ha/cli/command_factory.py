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

import inspect

from ha.cli import commands

class CommandFactory:
    """
    Factory for representing and creating command objects using
    a generic skeleton.
    """

    @staticmethod
    def get_command(component_parser):
        """
        Get command from command factory

        Args:
            component_parser (<class 'argparse._SubParsersAction'>): argparse to add subparser.
        """
        command_class = inspect.getmembers(commands, inspect.isclass)
        for cmd_name, cmd in command_class:
            if cmd_name != "Command" and "Command" in cmd_name:
                cmd.add_args(component_parser)
