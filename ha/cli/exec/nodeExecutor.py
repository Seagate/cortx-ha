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

import argparse
from cortx.utils.log import Log
from ha.core.error import HAUnimplemented
from ha.cli.exec.commandExecutor import CommandExecutor
from ha.cli.cli_schema import CLISchema

class NodeStartExecutor(CommandExecutor):

    def __init__(self):
        """
        Init node start executor
        """
        super(NodeStartExecutor, self).__init__()
        self._args = None

    def validate(self) -> bool:
        """
        Validate the command arguments
        """
        if self.parse_cluster_args():
            return True
        return False

    def parse_cluster_args(self) -> bool:
        """
        Parses the command line args.
        Return: argparse
        """
        parser = argparse.ArgumentParser(prog='node start',
            usage = CLISchema.get_usage("node", "start"),
            formatter_class = argparse.RawDescriptionHelpFormatter)
        parser.add_argument("node", help="Module")
        parser.add_argument("start", help="action to be performed")
        parser.add_argument("nodeid",
            help="Provide node name to add it in cluster.", action="store")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--all', action='store_true',
                           help='Start both server & storage in a node')
        group.add_argument('--server', action='store_false',
                           help='Start only server in a node')
        parser.add_argument('--json', help='Required output format', action='store_true')
        self._args = parser.parse_args()
        return True

    def execute(self) -> None:
        """
        Execute the node start
        """
        Log.info("Executing cortx node start")
        node_id = None or self._args.nodeid
        if self.is_valid_node_id(node_id):
            node_start_result = self.cluster_manager.node_controller.start(node_id)
            if self._args.all:
                Log.info("Executing storage start")
                # TODO : start storage enclosure
            Log.debug(node_start_result)
            if self.is_status_failed(node_start_result):
                self.op.set_rc(1)
            self.op.set_output(node_start_result)
            if self._args.json:
                self.op.set_format(self.op.JSON)
            self.op.dump_output()

class NodeStopExecutor(CommandExecutor):

    def validate(self) -> str:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> str:
        raise HAUnimplemented("This operation is not implemented.")


class NodeStandbyExecutor(CommandExecutor):

    def validate(self) -> str:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> str:
        raise HAUnimplemented("This operation is not implemented.")


class NodeActiveExecutor(CommandExecutor):

    def validate(self) -> str:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> str:
        raise HAUnimplemented("This operation is not implemented.")


class NodeStatusExecutor(CommandExecutor):

    def validate(self) -> str:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> str:
        raise HAUnimplemented("This operation is not implemented.")
