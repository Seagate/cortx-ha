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

from ha.core.error import HAUnimplemented

class Command:
    @staticmethod
    def add_args(component_parser):
        raise HAUnimplemented()

class NodeCommand(Command):
    @staticmethod
    def add_args(component_parser):
        """
        Add parser for cleanup command

        Args:
            component_parser (<class 'argparse._SubParsersAction'>): argparse to add subparser.
        """
        node_parser = component_parser.add_parser("node",
            help = "Node management")
        action_subparser = node_parser.add_subparsers(
            title="Node Actions",
            dest="node_action")

        refresh_parser = action_subparser.add_parser("refresh",
            help = "Refresh nodes")
        refresh_parser.add_argument("--node",
            help="Refresh services for given node")
        refresh_parser.add_argument("--soft", action='store_true',
            help="Check status and then perform refresh")
        refresh_parser.add_argument("--hard", action='store_true',
            help="Perform refresh forcefully")
        refresh_parser.add_argument("--data-only", action='store_true',
            help="Perform refresh forcefully")

class ClusterCommand(Command):
    @staticmethod
    def add_args(component_parser):
        """
        Add parser for cluster command

        Args:
            component_parser (<class 'argparse._SubParsersAction'>): argparse to add subparser.
        """
        cluster_parser =  component_parser.add_parser("cluster",
            help = "Manage cluster")
        action_subparser = cluster_parser.add_subparsers(
            title="Cluster Actions",
            dest="cluster_action")

        add_node_parser = action_subparser.add_parser("add_node",
            help = "Add node to cluster")
        add_node_parser.add_argument("node",
            help="Node name", action="store")

        remove_node_parser = action_subparser.add_parser("remove_node",
            help = "Remove node to cluster")
        remove_node_parser.add_argument("node",
            help="Node name", action="store")

        start_parser = action_subparser.add_parser("start",
            help = "Start cluster")

        stop_parser = action_subparser.add_parser("stop",
            help = "Stop cluster")

        status_parser = action_subparser.add_parser("status",
            help = "cluster status")

        shutdown_parser = action_subparser.add_parser("shutdown",
            help = "shutdown cluster")

class ServiceCommand(Command):
    @staticmethod
    def add_args(component_parser):
        """
        Add parser for cluster command

        Args:
            component_parser (<class 'argparse._SubParsersAction'>): argparse to add subparser.
        """
        service_parser =  component_parser.add_parser("service",
                    help = "Manage service")
        action_subparser = service_parser.add_subparsers(
            title="Service Actions",
            dest="service_action")

        start_parser = action_subparser.add_parser("start",
            help = "Start Service")
        start_parser.add_argument("service_name",
            help="Service name", action="store")
        start_parser.add_argument("--node",
            help="Node name")

        stop_parser = action_subparser.add_parser("stop",
            help = "Stop Service")
        stop_parser.add_argument("service_name",
            help="Service name", action="store")
        stop_parser.add_argument("--node",
            help="Node name")

        status_parser = action_subparser.add_parser("status",
            help = "status Service")
        status_parser.add_argument("service_name",
            help="Service name", action="store")
        status_parser.add_argument("--node",
            help="Node name")