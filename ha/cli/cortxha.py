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
import argparse
import pathlib

#from cortx.utils.schema.conf import Conf
#from cortx.utils.log import Log
#from cortx.utils.schema.payload import *

#if __name__ == '__main__':
def main(argv):
    """
    Entry point for cortx CLI
    """
    description = "CORTX HA CLI"

    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..'))
    # from ha import const
    from ha.cli.command_factory import cmdFactory
    from ha.cli.permissions import Permissions
#    from ha.core.cluster.cluster_manager import CortxClusterManager

    ha_cli = cmdFactory()
    
    #ha_cli.usage(argv[0])
    command = ha_cli.get_command(description, argv[1:])
    permissions = Permissions()
    permissions.validate_permissions()
    command.execute()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
