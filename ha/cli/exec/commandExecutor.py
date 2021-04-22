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


import grp
import getpass
import json
import os
import re
import abc
import socket

from ha import const
from ha.const import STATUSES
from ha.cli.cli_schema import CLISchema
from cortx.utils.log import Log
from ha.core.error import HAInvalidPermission, HAClusterCLIError, HAUnimplemented
from ha.core.cluster.cluster_manager import CortxClusterManager
from ha.cli.displayOutput import Output

class CLIExecutor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self) -> None:
        """
        Abstract method of CLIExecuter.
        """
        pass

    @abc.abstractmethod
    def validate(self) -> bool:
        """
        Abstract method of CLIExecuter.
        """
        pass

    def validate_permissions(self) -> None:

        # confirm that user is root or part of haclient group"

        user = getpass.getuser()
        group_id = os.getgid()

        try:
            # find group id for root and haclient
            id_ha = grp.getgrnam(const.USER_GROUP_HACLIENT)
            id_root = grp.getgrnam(const.USER_GROUP_ROOT)

            # if group not root or haclient return error
            if group_id != id_ha.gr_gid and group_id != id_root.gr_gid:
                Log.error(f"User {user} does not have necessary permissions to execute this CLI")
                raise HAInvalidPermission(
                            f"User {user} does not have necessary permissions to execute this CLI")

            # The user name "hauser"; which is part of the "haclient" group;
            # is used by HA.
            # internal commands are allowed only if the user is "hauser"
            # As of now, every HA CLI will be internal command. So, we
            # do not need this change. We can revisit this if needed in future
            #if user == const.USER_HA_INTERNAL:
            #    self._is_hauser = True


        # TBD : If required raise seperate exception  for root and haclient
        except KeyError:
            Log.error("Group root / haclient is not defined")
            raise HAInvalidPermission("Group root / haclient is not defined ")

class CommandExecutor(CLIExecutor):
    def __init__(self):
        self._is_hauser = False
        self.cluster_manager = CortxClusterManager()
        self.op = Output()

    def validate(self) -> bool:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> None:
        raise HAUnimplemented("This operation is not implemented.")

    def is_status_failed(self, output):
        output = json.loads(output)
        if STATUSES.FAILED.value == output.get("status"):
            return True

    def is_valid_node_id(self, node_id) -> bool:
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

    def is_ha_user(self) -> bool:
        """
        Routine used by executors to confirm access permissions.
        Used to differentiate between external and internal CLIs
        """
        return self._is_hauser

    def parse_node_desc_file(self, node_desc_file):
        with open(node_desc_file) as nf:
            try:
                node_data = json.load(nf)
                node_id = node_data.get('node_id')
            except KeyError:
                raise HAClusterCLIError('node_id can not be None')
        return node_id

class CLIUsage(CLIExecutor):

    def usage(self) -> str:
        return CLISchema.get_help()

    def validate(self):
        return True

    def execute(self):
        output = Output()
        output.set_output(self.usage())
        output.dump_output()

class ClusterCLIUsage(CLIUsage):

    def usage(self) -> str:
        return CLISchema.get_help("cluster")

class NodeCLIUsage(CLIUsage):

    def usage(self) -> str:
        return CLISchema.get_help("node")

class StoragesetCLIUsage(CLIUsage):

    def usage(self) -> str:
        return CLISchema.get_help("storageset")

class ServiceCLIUsage(CLIUsage):

    def usage(self) -> str:
        return CLISchema.get_help("service")
