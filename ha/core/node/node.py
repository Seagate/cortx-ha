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

from eos.utils.schema.conf import Conf
from eos.utils.log import Log
from ha import const

class Node:
    """
    Node class
    """
    def __init__(self, node_id):
        """
        Update node related info from the conf file using node id
        """
        self.node_id = node_id
        self.UUID = Conf.get(const.HA_GLOBAL_INDEX, f"Node.nodelist.{node_id}.uuid")
        self.hostname = Conf.get(const.HA_GLOBAL_INDEX, f"Node.nodelist.{node_id}.hostname")

    def get_node_id(self):
        """
        Returns minion id of the node
        """
        return self.node_id

    def get_UUID(self):
        """
        Returns UUID of the node
        """
        return self.UUID

    def get_hostname(self):
        """
        Returns hostname of the node
        """
        return self.hostname

    def start(self):
        """
        Start the node
        """
        pass

    def shutdown(self):
        """
        Shutdown the node
        """
        pass

    def status(self):
        """
        Returns the node status
        """
        pass