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
import os
from cortx.utils.log import Log
from ha.cli.exec.commandExecutor import CommandExecutor
from ha.core.error import HAUnimplemented
from ha.cli.cli_schema import CLISchema

class ClusterStartExecutor(CommandExecutor):

    def __init__(self):
        """
        Init cluster start executor
        """
        super(ClusterStartExecutor, self).__init__()
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
        parser = argparse.ArgumentParser(prog='cluster start cli',
                        usage = CLISchema.get_usage("cluster", "start"),
                        formatter_class = argparse.RawDescriptionHelpFormatter)
        parser.add_argument("cluster", help="Module")
        parser.add_argument("start", help="action to be performed")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--all', action='store_true',
                           help='All servers to start in a cluster')
        group.add_argument('--server', action='store_false',
                           help='Server to start in a cluster')
        parser.add_argument('--json', help='Required output format', action='store_true')
        self._args = parser.parse_args()
        return True

    def execute(self) -> None:
        """
        Execute the cluster start for all or only cluster
        """
        Log.info("Executing cortxha cluster start")
        _cluster_start_result = self.cluster_manager.cluster_controller.start()
        if self._args.all:
            Log.info("Executing storage start")
            # TODO : start storage enclosure
        Log.info(_cluster_start_result)
        if self.is_status_failed(_cluster_start_result):
            self.op.set_rc(1)
        self.op.set_output(_cluster_start_result)
        if self._args.json:
            self.op.set_format(self.op.JSON)
        self.op.dump_output()

class ClusterStopExecutor(CommandExecutor):

    def __init__(self):
        '''Init method'''
        super(ClusterStopExecutor, self).__init__()
        self._args = None

    def parse_args(self) -> None:
        '''
           Parses the command line args.
           Return: argparse
        '''
        parser = argparse.ArgumentParser(prog='cluster stop cli',
                        usage = CLISchema.get_usage("cluster", "stop"),
                        formatter_class = argparse.RawDescriptionHelpFormatter)
        parser.add_argument("cluster", help="Module")
        parser.add_argument("stop", help="action to be performed")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--all', action='store_true', \
                            help='Server and storage stop')
        group.add_argument('--server', action='store_false', \
                            help='server stop')
        parser.add_argument('--json', help='Required output format', action='store_true')
        return parser.parse_args()

    def validate(self) -> bool:
        '''
           Validates permission and command line arguments.
           Return: bool
        '''
        self._args = self.parse_args()
        if self._args:
            return True
        return False

    def execute(self) -> None:
        '''
           Execute CLI request by passing it to ClusterManager and
           also displays an output
        '''
        Log.info("Executing cluster stop")
        stop_cluster_message = None
        if self._args.all:
            Log.info("Executing storageset stop")
            # TODO: Perform storageset stop

        stop_cluster_message = self.cluster_manager.cluster_controller.stop()
        Log.info(stop_cluster_message)
        if self.is_status_failed(stop_cluster_message):
            self.op.set_rc(1)
        self.op.set_output(stop_cluster_message)
        if self._args.json:
            self.op.set_format(self.op.JSON)
        self.op.dump_output()

class ClusterRestartExecutor(CommandExecutor):
    def validate(self) -> bool:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> None:
        raise HAUnimplemented("This operation is not implemented.")


class ClusterStandbyExecutor(CommandExecutor):
    def validate(self) -> bool:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> None:
        raise HAUnimplemented("This operation is not implemented.")


class ClusterActiveExecutor(CommandExecutor):
    def validate(self) -> bool:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> None:
        raise HAUnimplemented("This operation is not implemented.")


class ClusterListExecutor(CommandExecutor):
    def validate(self) -> bool:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> None:
        raise HAUnimplemented("This operation is not implemented.")


class ClusterStatusExecutor(CommandExecutor):
    def validate(self) -> bool:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> None:
        raise HAUnimplemented("This operation is not implemented.")


class ClusterNodeAddExecutor(CommandExecutor):
    '''
        Module which will accept the request for cluster add node
        functionality and which is responsible for delegating that request
        to Cluster Manager
    '''
    def __init__(self):
        '''Init Method'''
        super(ClusterNodeAddExecutor, self).__init__()
        self._args = None

    def parse_cluster_args(self) -> bool:
        '''
           Parses the command line args.
           Return: argparse
        '''
        parser = argparse.ArgumentParser(prog='cluster add_node cli',
                        usage = CLISchema.get_usage("cluster", "add_node"),
                        formatter_class = argparse.RawDescriptionHelpFormatter)
        parser.add_argument("cluster", help="Module")
        parser.add_argument("add_node", help="action to be performed")
        group = parser.add_mutually_exclusive_group(required='True')
        group.add_argument('--nodeid', action='store', \
                           help='ID of a node which needs to be added in a cluster')
        group.add_argument('--descfile', action='store', \
                           help='A file which describes the node to be added in a cluster', \
                           type=self._is_file_extension_valid)
        parser.add_argument('--username', help='cluster username', required=True)
        parser.add_argument('--password', help='cluster password', required=True)
        parser.add_argument('--json', help='Required output format', action='store_true')
        self._args = parser.parse_args()
        return True

    def _is_file_extension_valid(self, filename) -> str:
        '''
           Checks if file extension which is passed is correct or not
           Returns: str
           Exception: ArgumentTypeError
        '''
        _, ext = os.path.splitext(filename)
        if ext.lower() not in ('.json'):
            raise argparse.ArgumentTypeError('File must have a json extension')
        return filename

    def validate(self) -> bool:
        '''
           Validates permission and command line arguments.
           Exception: HAInvalidPermission
           Return: bool
        '''
        # Every CLI command will be an internal command now. So,
        # we do not need this change. If required, can be revisited later.
        # if not self.is_ha_user():
        #    raise HAInvalidPermission('Not enough permissions to invoke this command')
        if self.parse_cluster_args():
            return True
        return False

    def execute(self) -> None:
        '''
           Execute CLI request by passing it to ClusterManager and
           also displays an output
        '''
        Log.info("Executing cluster add node")
        node_id = None or self._args.nodeid
        cluster_uname = self._args.username
        cluster_pwd = self._args.password
        if self._args.descfile:
            node_id = self.parse_node_desc_file(self._args.descfile)
        if self.is_valid_node_id(node_id):
            add_node_result_message = self.cluster_manager.cluster_controller.add_node(node_id, \
                                    cluster_uname, cluster_pwd)
            Log.info(add_node_result_message)
            if self._args.json:
                self.op.set_format(self.op.JSON)
            self.op.set_output(add_node_result_message)
            if self.is_status_failed(add_node_result_message):
                self.op.set_rc(1)
        else:
            self.op.set_output("Invalid node")
            self.op.set_rc(1)
        self.op.dump_output()
