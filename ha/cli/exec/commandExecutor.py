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
import os

from ha import const
from cortx.utils.log import Log
from ha.core.error import HAInvalidPermission

class CommandExecutor:
    def __init__(self):
        self._is_hauser = False

    def validate(self) -> bool:
        raise HAUnimplemented("This operation is not implemented.")

    def execute(self) -> None:
        raise HAUnimplemented("This operation is not implemented.")

    """
    Routine used by executors to confirm acess permissions.
    Used to differentiate between external and internal CLIs
    """
    def is_ha_user(self) -> bool:
        return self._is_hauser

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

        def parse_node_desc_file(self, node_desc_file):
            # TODO: parse node description file and extract its contents
            # Same function can be used in case of parsing storage_set
            # desc file

class CLIUsage:

    @staticmethod
    def usage() -> str:
        usage_string = ("\t[-h]\n"
                        "\tcluster start [all|server] [--json]\n"
                        "\tcluster stop [all|server] [--json]\n"
                        "\tcluster restart\n"
                        "\tcluster standby [--json]\n"
                        "\tcluster active [--json]\n"
                        "\tcluster list [nodes|storagesets|services]\n"
                        "\tcluster status [all|hw|services] [--json]\n"
                        "\tcluster add node [<node id>] [ --descfile <node description file>] [--json]\n"
                        "\tcluster add storageset [<storageset id>] [ --descfile <storageset description file>] [--json]\n"
                        "\tnode start <Node> [all|server] [--json]\n"
                        "\tnode stop <Node> [all|server] [--json]\n"
                        "\tnode standby <Node> [--json]\n"
                        "\tnode active <Node> [--json]\n"
                        "\tnode status <Node> [all|hw|services] [--json]\n"
                        "\tstorageset status [all|hw|services] <storageset_id>\n"
                        "\tstorageset start <storageset_id>\n"
                        "\tstorageset stop <storageset_id>\n"
                        "\tstorageset standby <storageset_id>\n"
                        "\tstorageset active <storageset_id>\n"
                        "\tservice start <service> [--node <Node>] [--json]\n"
                        "\tservice stop <service> [--node <Node>] [--json]\n"
                        "\tservice status <service> [--node <Node>] [--json]\n")
        return usage_string


    def execute(self):
        print(self.usage())


class ClusterCLIUsage(CLIUsage):

    @staticmethod
    def usage() -> str:
        usage_string = ("\t[-h]\n"
                        "\tcluster start [all|server] [--json]\n"
                        "\tcluster stop [all|server] [--json]\n"
                        "\tcluster restart\n"
                        "\tcluster standby [--json]\n"
                        "\tcluster active [--json]\n"
                        "\tcluster list [nodes|storagesets|services]\n"
                        "\tcluster status [all|hw|services] [--json]\n"
                        "\tcluster add node [<node id>] [ --descfile <node description file>] [--json]\n"
                        "\tcluster add storageset [<storageset id>] [ --descfile <storageset description file>] [--json]\n")
        return usage_string


    def execute(self):
        print(self.usage())

class NodeCLIUsage(CLIUsage):

    @staticmethod
    def usage() -> str:
        usage_string = ("\t[-h]\n"
                        "\tnode start <Node> [all|server] [--json]\n"
                        "\tnode stop <Node> [all|server] [--json]\n"
                        "\tnode standby <Node> [--json]\n"
                        "\tnode active <Node> [--json]\n"
                        "\tnode status <Node> [all|hw|services] [--json]\n")
        return usage_string


    def execute(self):
        print(self.usage())

class StoragesetCLIUsage(CLIUsage):

    @staticmethod
    def usage() -> str:
        usage_string = ("\t[-h]\n"
                        "\tstorageset status [all|hw|services] <storageset_id>\n"
                        "\tstorageset start <storageset_id>\n"
                        "\tstorageset stop <storageset_id>\n"
                        "\tstorageset standby <storageset_id>\n"
                        "\tstorageset active <storageset_id>\n")
        return usage_string


    def execute(self):
        print(self.usage())


class ServiceCLIUsage(CLIUsage):

    @staticmethod
    def usage() -> str:
        usage_string = ("\t[-h]\n"
                        "\tservice start <service> [--node <Node>] [--json]\n"
                        "\tservice stop <service> [--node <Node>] [--json]\n"
                        "\tservice status <service> [--node <Node>] [--json]\n")
        return usage_string


    def execute(self):
        print(self.usage())
