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

from cortx.utils.ha.dm.decision_monitor import DecisionMonitor
from cortx.utils.log import Log
from cortx.utils.schema.conf import Conf

from ha import const
from ha.core.node.node import Node
from ha.core.node.replacement.refresh_context import CortxRefreshContext
from ha.core.service.service_manager import CortxServiceManager
from ha.core.error import HAUnimplemented


class NodeManager:
    """
    Node Manager
    """
    def __init__(self):
        """
        Manage node operation
        """
        pass

    def process_request(self, action, args, output):
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
        self._service_manager = CortxServiceManager()

        node_list = Conf.get(const.HA_GLOBAL_INDEX, "Node.nodelist")

        for node_id in node_list.keys():
            self.node_instance_list[node_id] = Node(node_id)

        Log.debug(f"node_instance_list {self.node_instance_list}")

    def process_request(self, action, args, output):
        """
        Generic method to handle process request

        Args:
            args ([dict]): Parameter pass to request to process.
        """
        if action == const.NODE_COMMAND:
            node = None
            if args.node is None:
                local_node = Conf.get(const.HA_GLOBAL_INDEX, "Node.local")
                node = self.get_node_instance(local_node)
            else:
                node = self.get_node_instance(args.node)

            self._output = output

            if args.node_action == "start":
                _action_status, _return_code = node.start()
                self._output.output(_action_status)
                self._output.rc(_return_code)

            elif args.node_action == "stop":
                _action_status, _return_code = node.shutdown()
                self._output.output(_action_status)
                self._output.rc(_return_code)

            elif args.node_action == "status":
                _action_status, _return_code = node.status()
                self._output.output(_action_status)
                self._output.rc(_return_code)

            else:
                raise HAUnimplemented()

        elif action == const.SERVICE_COMMAND:
            self._service_manager.process_request(action, args, output)

        else:
            raise HAUnimplemented()

    def get_node_instance_list(self):
        """
        Returns node list
        """
        return self.node_instance_list

    def validate_node(self, node_id):
        """
        Validate requested node is there in the node list
        """
        valid_node = False

        if node_id in self.node_instance_list.keys():
            valid_node = True

        return valid_node

    def get_node_instance(self, node_id):
        """
        Returns instance of the node
        """
        if self.validate_node(node_id):
            node = self.node_instance_list[node_id]
        else:
            Log.error(f"Invalid node id {node_id}")

        return node
