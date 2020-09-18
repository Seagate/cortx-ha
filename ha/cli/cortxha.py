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
 Description:       Entry point for cortxha CLI
 ****************************************************************************
"""

import os
import sys
import traceback
import argparse
import pathlib

from cortx.utils.schema.conf import Conf
from cortx.utils.log import Log
from cortx.utils.schema.payload import *

#TODO - Move the cli to cortxcli framework once cortxcli is created as a separate module.
class HACli:

    def __init__(self):
        """
        Initialize HACLI
        """
        self._provider = {
            "cleanup": ""
        }
        Conf.init()
        Conf.load(const.RESOURCE_GLOBAL_INDEX, Json(const.RESOURCE_SCHEMA))
        log_level = Conf.get(const.RESOURCE_GLOBAL_INDEX, "log", "INFO")
        Log.init(service_name='cortxha', log_path=const.RA_LOG_DIR, level=log_level)

    @staticmethod
    def _usage():
        return """

    Example:
    cortxha cleanup db --node <node_minion_id>
    cortxha cluster add_node <node_minion_id>
    cortxha cluster remove_node <node_minion_id>
    """

    def command(self):
        try:
            argParser = argparse.ArgumentParser(
                usage = "%(prog)s\n\n" +  HACli._usage(),
                formatter_class = argparse.RawDescriptionHelpFormatter)

            component_parser = argParser.add_subparsers(
                help = "Select one of given component.")

            # Cleanup
            cleanup_parser = component_parser.add_parser("cleanup",
                                help = "Cleanup db and resource")
            cleanup_parser.add_argument("cleanup",
                help = "Select singlenode or multinode.",
                choices = ["db"])

            cleanup_parser.add_argument("-n", "--node",
                help="Cleanup data for node")

            # Cluster
            cluster_parser =  component_parser.add_parser("cluster",
                                help = "Manage cluster")
            cluster_parser.add_argument("cluster",
                help = "Cluster add remove node",
                choices = ["add_node", "remove_node"])
            cluster_parser.add_argument("node",
                help="Node name", action="store")

            args = argParser.parse_args()

            if len(sys.argv) <= 1:
                argParser.print_help(sys.stderr)
            elif sys.argv[1] == "cluster":
                cluster = PcsCluster()
                if args.cluster == "add_node":
                    cluster.add_node(args.node)
                elif args.cluster == "remove_node":
                    cluster.remove_node(args.node)
            elif sys.argv[1] == "cleanup":
                Cleanup(args).cleanup_db()
            else:
                argParser.print_help(sys.stderr)
        except Exception as e:
            Log.error(f"{traceback.format_exc()}, {e}")
            sys.exit(1)

if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..'))
    from ha import const
    from ha.core.cleanup import Cleanup
    from ha.core.cluster import PcsCluster
    ha_cli = HACli()
    ha_cli.command()
