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

"""
 ****************************************************************************
 Description:       Node Manager
 ****************************************************************************
"""
from node import Node
from ha.utility.error import HAUnimplemented, HACommandTerminated

from eos.utils.schema.conf import Conf
from eos.utils.log import Log
from ha import const


class NodeManager:
    def __init__(self):
        """
        Manage node operation
        """
        pass

    def process_request(self, action, args):
        """
        Generic method to handle process request

        Args:
            action ([string]): Take cluster action for each request.
            args ([dict]): Parameter pass to request to process.

        Raises:
            HAUnimplemented: Unimplemented method.
        """
        raise HAUnimplemented()

    def get_node_instance_list(self):
        """
        Returns node list
        """
        raise HAUnimplemented()

    def get_node_instance(self, node_id):
        """
        Returns instance of the node
        """
        raise HAUnimplemented()

    def validate_node(self, node_id):
        """
        Validate requested node is there in the node list
        """
        raise HAUnimplemented()

class CortxNodeManager(NodeManager):
    def __init__(self):
        """
        Prepare node instance list
        """
        self.node_instance_list = {}
        nodelist = Conf.get(const.HA_GLOBAL_INDEX, "Node.nodelist")

        for node_id in nodelist.keys():
            self.node_instance_list[node_id] = Node(node_id)

        Log.debug(f"node_instance_list {self.node_instance_list}")

    def process_request(self, action, args):
        """
        Generic method to handle process request

        Args:
            args ([dict]): Parameter pass to request to process.
        """
        if args.action == const.NODE_COMMAND:
            if args.command == "start":
                if self.validate_node(args.node):
                    Node = self.get_node_instance(args.node)
                    Node.start()
                else:
                    Log.error(f"Invalid node id {args.node}")

            elif args.command == "stop":
                if self.validate_node(args.node):
                    Node = self.get_node_instance(args.node)
                    Node.shutdown()
                else:
                    Log.error(f"Invalid node id {args.node}")

            elif args.node == "status":
                if self.validate_node(args.node):
                    Node = self.get_node_instance(args.node)
                    Node.status()
                else:
                    Log.error(f"Invalid node id {args.node_id}")

            else:
                raise HAUnimplemented()

        elif args.action == const.SERVICE_COMMMAND:
            pass

        elif args.action == const.CLEANUP_COMMAND:
            pass

        else:
            raise HAUnimplemented()

    def get_node_instance_list(self):
        """
        Returns node list
        """
        return self.node_instance_list

    def get_node_instance(self, node_id):
        """
        Returns instance of the node
        """
        return self.node_instance_list[node_id]

    def validate_node(self, node_id):
        """
        Validate requested node is there in the node list
        """
        Valid_Node = False

        if node_id in self.node_instance_list.keys():
            Valid_Node = True

        return Valid_Node

class PcsNodeManager(NodeManager):
    def __init__(self):
        pass

    def process_request(self, action, args):
        pass

    def get_node_instance_list(self):
        pass

    def get_node_instance(self, node_id):
        pass

    def validate_node(self, node_id):
        pass