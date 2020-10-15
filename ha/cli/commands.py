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
            help = "This command is used to manage node level operation")
        action_subparser = node_parser.add_subparsers(
            title="Node Actions",
            dest="node_action")

        refresh_parser = action_subparser.add_parser("refresh",
            help = "Refresh nodes to recheck service status and take particular action")
        refresh_parser.add_argument("--node",
            help="Provide node name to take action on particular node.")
        refresh_parser.add_argument("--soft", action='store_true',
            help="Check node status and then perform action only if require.")
        refresh_parser.add_argument("--hard", action='store_true',
            help="Perform refresh forcefully")
        refresh_parser.add_argument("--data-only", action='store_true',
            help="Forget all previous data and collect new data in db to take action.")

class ClusterCommand(Command):
    @staticmethod
    def add_args(component_parser):
        """
        Add parser for cluster command

        Args:
            component_parser (<class 'argparse._SubParsersAction'>): argparse to add subparser.
        """
        cluster_parser =  component_parser.add_parser("cluster",
            help = "Manage cluster operations like start, stop cluster.")
        action_subparser = cluster_parser.add_subparsers(
            title="Cluster Actions",
            dest="cluster_action")

        add_node_parser = action_subparser.add_parser("add_node",
            help = "Add new node to existing cluster to manage their service.")
        add_node_parser.add_argument("node",
            help="Provide node name to add it in cluster.", action="store")

        remove_node_parser = action_subparser.add_parser("remove_node",
            help = "Remove node from cluster")
        remove_node_parser.add_argument("node",
            help="Provide node name to remove it from the cluster.", action="store")

        start_parser = action_subparser.add_parser("start",
            help = "Start cluster and it's services.")

        stop_parser = action_subparser.add_parser("stop",
            help = "Stop cluster and it's services.")

        status_parser = action_subparser.add_parser("status",
            help = "Get cluster status.")

        shutdown_parser = action_subparser.add_parser("shutdown",
            help = "Shutdown cluster.")

class ServiceCommand(Command):
    @staticmethod
    def add_args(component_parser):
        """
        Add parser for cluster command

        Args:
            component_parser (<class 'argparse._SubParsersAction'>): argparse to add subparser.
        """
        service_parser =  component_parser.add_parser("service",
                    help = "Manage cluster services and it's operations.")
        action_subparser = service_parser.add_subparsers(
            title="Service Actions",
            dest="service_action")

        start_parser = action_subparser.add_parser("start",
            help = "Start Service")
        start_parser.add_argument("service_name",
            help="Service name", action="store")
        start_parser.add_argument("--node",
            help="Provide node name to start service on particular node")

        stop_parser = action_subparser.add_parser("stop",
            help = "Stop Service")
        stop_parser.add_argument("service_name",
            help="Service name", action="store")
        stop_parser.add_argument("--node",
            help="Provide node name to stop service on particular node")

        status_parser = action_subparser.add_parser("status",
            help = "Status of service")
        status_parser.add_argument("service_name",
            help="Service name", action="store")
        status_parser.add_argument("--node",
            help="Provide node name to get status of service.")

class SupportBundleCommand(Command):
    @staticmethod
    def add_args(component_parser):
        """
        Add parser for support bundle command

        Args:
            component_parser (<class 'argparse._SubParsersAction'>): argparse to add subparser.
        """
        bundle_parser =  component_parser.add_parser("support_bundle",
                                help = "Manage support bundle operation like create.")
        action_subparser = bundle_parser.add_subparsers(
            title="Support Bundle",
            dest="bundle_action")

        create_parser = action_subparser.add_parser("create",
            help = "Create Support Bundle")
        create_parser.add_argument("id",
            help="Bundle id", action="store")
        create_parser.add_argument("path",
            help="Bundle Path", action="store")