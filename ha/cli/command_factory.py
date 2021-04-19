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
from ha.cli.cli_schema import CLISchema

class CmdFactory:

    @staticmethod
    def get_executor(module_name: str, operation_name: str) -> str:
        """ return the appropriate class name from the dictionary"""
        try:
            executor = CLISchema.get_class(module_name, operation_name)
        except Exception:
            Log.error(f"Failed to get executor Module Name: {module_name}, Operation Name: {operation_name}")
            return None
        return executor
