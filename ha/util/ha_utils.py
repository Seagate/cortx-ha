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

import xml.etree.ElementTree as ET

from cortx.utils.log import Log

from ha import const
from ha.execute import SimpleCommand


class HaUtils:

    def __init__(self):
        self.process = SimpleCommand()

    def get_online_nodes(self):
        """
        Get list of online nodes ids.
        """
        online_nodes_xml = self.process.run_cmd(const.GET_ONLINE_NODES_CMD)
        # create element tree object
        root = ET.fromstring(online_nodes_xml[0])
        nodes_ids = []
        # iterate news items
        for item in root.findall('nodes'):
            # iterate child elements of item
            for child in item:
                if child.attrib['online'] == 'true':
                    nodes_ids.append(child.attrib['id'])
        Log.info(f"List of online node ids in cluster in sorted ascending order: {sorted(nodes_ids)}")
        return sorted(nodes_ids)

    def get_local_node(self):
        """
        Get Local node name and id.
        """
        local_node_id = self.process.run_cmd(const.GET_LOCAL_NODE_ID_CMD)
        local_node_name = self.process.run_cmd(const.GET_LOCAL_NODE_NAME_CMD)
        Log.info(f"Local node name: {local_node_name[0]} \n Local node id: {local_node_id[0]}")
        return local_node_id[0], local_node_name[0]