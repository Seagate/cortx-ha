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

import time

from cortx.utils.log import Log
from ha.execute import SimpleCommand
from ha import const
from ha.cli.error import Error


class CommandExecutor:

    def validate(self):
        print("validate for ")
        print(self.__class__.__name__)

    def execute(self):
        print("execute")
        print(self.__class__.__name__)


class CLIUsage:

    @staticmethod
    def usage():
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
