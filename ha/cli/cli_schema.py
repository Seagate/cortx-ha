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

import json
from ha import const

class CLISchema:

    SCHEMA = None

    @staticmethod
    def get_schama():
        """
        Schama initialization
        """
        if CLISchema.SCHEMA is None:
            with open(const.CLI_SCHEMA_FILE, "r") as fi:
                CLISchema.SCHEMA = json.load(fi)
        return CLISchema.SCHEMA

    @staticmethod
    def get_help(module = None):
        schema = CLISchema.get_schama()
        help_cli = ""
        if module == None:
            for module in schema:
                if module != "version":
                    help_cli += f"\n\nFor {module} Command:\n--------------------------\n"
                    for action in schema[module]:
                        help_cli += schema[module][action]["usage"] + "\n"
        else:
            help_cli += f"\n\nFor {module} Command:\n--------------------------\n"
            for action in schema[module]:
                help_cli += schema[module][action]["usage"] + "\n"
        return help_cli

    @staticmethod
    def get_class(module_name: str, operation_name: str):
        schema = CLISchema.get_schama()
        if operation_name in ["-h", "--help"]:
            return schema[module_name]["help"]["class"]
        else:
            return schema[module_name][operation_name]["class"]

    @staticmethod
    def get_usage(module_name: str, operation_name: str):
        schema = CLISchema.get_schama()
        return schema[module_name][operation_name]["usage"]
