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
import ast

from cortx.utils.schema.conf import Conf
from ha import const
from ha.execute import SimpleCommand

execute = SimpleCommand()
node_list, err, rc = execute.run_cmd("provisioner grains_get uuid node_id nodename")

if node_list is not None:
    node_list = ast.literal_eval(node_list)

    for node in node_list.keys():
        Conf.set(const.HA_GLOBAL_INDEX, f"Node.nodelist.{node}.uuid", f"{node_list[node]['uuid']}")
        Conf.set(const.HA_GLOBAL_INDEX, f"Node.nodelist.{node}.hostname", f"{node_list[node]['nodename']}")

    # Needs to remove Conf._payloads line and uncommet below line once the bug inside save method get resolved
    #Conf.save(const.HA_GLOBAL_INDEX)
    Conf._payloads[const.HA_GLOBAL_INDEX].dump()
