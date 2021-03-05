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

import errno

from ha.cli.output import Output
from ha.cli.permissions import Permissions

# Sample / placeholder file for cluster commands
class Cluster:
    """cluster related CLI commands """


    def process(self, op_type, args):
        """
        Process cluster CLIs.
        Usage (arguments to be provided):
        
        """
        print("Placeholder cluster CLIs")
        #Output.print(string, "json")
        

    def validate():
        print("Placeholder validate method")      

    def is_internal_command():
        print("Placeholder check if command is internal or external")