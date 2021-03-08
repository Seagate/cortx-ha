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

import inspect
import argparse
import errno
#import traceback

from ha.cli import commands
from ha.cli.error import Error
from ha.core.config.config_manager import ConfigManager
#from cortx.utils.log import Log


class cmdFactory:
    def __init__(self):
        """
        init of command factory
        """
        # Init logging to  cortxcli.log file
        ConfigManager.init("cortxcli")

        #from  ha.cli import commands
        self.command = commands

    #@staticmethod
    def get_command(self, description, argv):
        """
        parse the cli and return the right executor
        """

        parser = argparse.ArgumentParser(
            usage = "%(prog)s\n\n" +  self.usage(),
            formatter_class = argparse.RawDescriptionHelpFormatter)

        subparsers = parser.add_subparsers()

        # inspect the commands.py file containing all classes including base class
        cmds = inspect.getmembers(self.command, inspect.isclass)

        cli_modules = []
        for name, cmd in cmds:
            # Command is the base class name
            if name != "Command" and "Command" in name:
                cmd.add_args(subparsers, cmd, name)
                cli_modules.append(name.replace("Command",''))

        # Raise exception if correct but insufficient parameters are passed
        if len(argv) < 2:
            if (len(argv) == 0) or (len(argv) == 1 and argv[0] in cli_modules):
                print(self.usage())
                raise Error(errno.EINVAL,
                    "Insufficient parameters; refer to help for details")

        args = parser.parse_args(argv)
        return args.command(args)



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

    

