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
import re
import socket
import time

from cortx.utils.log import Log
from ha.cli.exec.commandExecutor import CommandExecutor
from ha.core.error import HAClusterStart, HAClusterCLIError
from ha.core.cluster.cluster_manager import CortxClusterManager
from ha.core.error import HAUnimplemented


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
        parser = argparse.ArgumentParser(prog='cluster start all|<server>')
        parser.add_argument("cluster", help="Module")
        parser.add_argument("start", help="action to be performed")
        group = parser.add_mutually_exclusive_group(required='True')
        group.add_argument('--all', action='store_true',
                           help='All servers to start in a cluster')
        group.add_argument('--server', action='store_true',
                           help='Server to start in a cluster')
        parser.add_argument('--json', help='Required output format', action='store_true')
        self._args = parser.parse_args()
        return True

    def execute(self) -> None:
        """
        Execute the cluster start for all or only cluster
        """
        Log.info("Executing cortxha cluster start")
        _cluster_start_result = self._cluster_manager.cluster_controller.start()
        if self._args.all:
            Log.info("Executing storage start")
            # TODO : start storage enclosure

        if self._args.json:
            self._op.print_json(_cluster_start_result)
        Log.info(_cluster_start_result)


class ClusterStopExecutor(CommandExecutor):

    def __init__(self):
        '''Init method'''
        super(ClusterStopExecutor, self).__init__()
        self._cluster_manager = CortxClusterManager()
        self._op = Output()
        self._args = None

    def parse_args(self) -> None:
        '''
           Parses the command line args.
           Return: argparse
        '''
        parser = argparse.ArgumentParser(description="cluster stop")
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
        stop_cluster_message = None
        stop_cluster_message = self._cluster_manager.cluster_controller.stop(self._args.all or self._args.server)
        if self._args.json:
            self._op.print_json(stop_cluster_message)
        else:
            print(stop_cluster_message)


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
        parser = argparse.ArgumentParser(prog='cluster add node')
        parser.add_argument("cluster", help="Module")
        parser.add_argument("add", help="action to be performed")
        parser.add_argument("node", help="component on which action to be performed")
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

    def _is_valid_node_id(self, node_id) -> bool:
        '''
           Checks if node id gets resolved to some IP address or not
           Returns: bool
           Exception: socket.gaierror, socket.herror
        '''

        # TODO: change this logic and validate the node_id from the
        # list coming from system health
        ip_validator_regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"

        # node_id can be passed as IP address or FQDN or
        # some random number or just sequence of chars

        # first seperate the string from dots.
        splitted_node_id = node_id.replace('.', '')

        # If string only contains numbers, means it can be just
        # random number or can be an IP address. So, IP address
        # validation can be done. else for random number, exception will be
        # raised
        if re.search('^[0-9]*$', splitted_node_id):
            if re.search(ip_validator_regex, node_id):
                return True
            raise HAClusterCLIError(f'{node_id} is not a valid node_id')
        # else it can be combination of chars and numbers means hostname or just a
        # random meaningless string
        else:
            try:
                socket.gethostbyname(node_id)
            except Exception as err:
                raise HAClusterCLIError(f'{node_id} not a valid node_id: {err}')
        return True

    def execute(self) -> None:
        '''
           Execute CLI request by passing it to ClusterManager and
           also displays an output
        '''
        node_id = None or self._args.nodeid
        cluster_uname = self._args.username
        cluster_pwd = self._args.password
        if self._args.descfile:
            node_id = self.parse_node_desc_file(self._args.descfile)
        if self._is_valid_node_id(node_id):
            add_node_result_message = self._cluster_manager.cluster_controller.add_node(node_id, \
                                    cluster_uname, cluster_pwd)
            if self._args.json:
                self._op.print_json(add_node_result_message)
            print(add_node_result_message)
