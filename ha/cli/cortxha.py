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

import os
import sys
import traceback
import argparse
import pathlib


from cortx.utils.log import Log
from cortx.utils.conf_store.conf_store import Conf


class Output:
    def __init__(self):
        """
        Provide output for cluster command
        """
        self._output = "Success"
        self._rc = 0

    def output(self, output):
        self._output = output

    def rc(self, rc):
        self._rc = rc

    def get_output(self):
        return self._output

    def get_rc(self):
        return self._rc

#TODO - Move the cli to cortxcli framework once cortxcli is created as a separate module.
class HACli:
    """
    HACLI
    """
    def __init__(self):
        """
        Initialization of HA CLI.
        """
        # TODO Check product env and load specific conf
        ConfigManager.init('cortxha')

        # get version from ha.conf
        version = Conf.get(const.HA_GLOBAL_INDEX, "VERSION.version")
        major_version = version.split('.')
        self._version = major_version[0]

    @staticmethod
    def _usage():
        return """
    Use below command for more detail
    cortxha --help
    """

    def command(self):
        try:
            argParser = argparse.ArgumentParser(
                usage = "%(prog)s\n\n" +  HACli._usage(),
                formatter_class = argparse.RawDescriptionHelpFormatter)

            component_parser = argParser.add_subparsers(
                help = "Select one of given component.",
                dest = "cortxha_action")

            CommandFactory.get_command(component_parser)
            args = argParser.parse_args()

            Log.info(f"Executing: {' '.join(sys.argv)}")
            if len(sys.argv) <= 1:
                argParser.print_help(sys.stderr)
            else:
                output = Output()
                if self._version == const.CORTX_VERSION_1:
                    cluster = CortxClusterManager()
                else:
                    cluster = PcsClusterManager()
                cluster.process_request(args.cortxha_action, args, output)
                sys.stdout.write(f"{output.get_output()}\n")
                sys.exit(output.get_rc())
        except Exception as e:
            sys.stderr.write(f"{e}\n")
            Log.error(f"{traceback.format_exc()}, {e}")
            print(f"{traceback.format_exc()}")
            sys.exit(1)

if __name__ == '__main__':
    """
    Entry point for cortxha CLI
    """
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..'))
    from ha import const
    from ha.core.config.config_manager import ConfigManager
    from ha.cli.command_factory import CommandFactory
    ha_cli = HACli()

    if ha_cli._version == const.CORTX_VERSION_1:
        from ha.core.cluster.cluster_manager import CortxClusterManager
    else:
        from ha.core.cluster.cluster_manager import PcsClusterManager
    ha_cli.command()
