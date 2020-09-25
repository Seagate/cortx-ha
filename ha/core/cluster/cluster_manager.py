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
from cortx.utils.ha.dm.decision_monitor import DecisionMonitor

from ha.core.error import HAUnimplemented
from ha.core.node.replacement.refresh_context import PcsRefreshContex
from ha.execute import SimpleCommand
from ha import const

class ClusterManager:
    def __init__(self):
        """
        Manage cluster operation
        """
        pass

    def process_request(self, action, args):
        raise HAUnimplemented()

    def node_status(self, node):
        # TODO move node logic to node manager class
        raise HAUnimplemented()

    def remove_node(self, node):
        raise HAUnimplemented()

    def add_node(self, node):
        raise HAUnimplemented()

    def start(self):
        raise HAUnimplemented()

    def stop(self):
        raise HAUnimplemented()

    def status(self):
        raise HAUnimplemented()

    def shutdown(self):
        raise HAUnimplemented()

class PcsClusterManager(ClusterManager):
    def __init__(self):
        """
        PcsCluster manage pacemaker/corosync cluster
        """
        super(PcsClusterManager, self).__init__()
        self._execute = SimpleCommand()
        self._decision_monitor = DecisionMonitor()
        # TODO: add node_manager class to handle query
        self._refresh_contex = PcsRefreshContex(self._decision_monitor)
        # TODO move node logic to node manager class
        self._node_status = [ 'Online', 'Standby', 'Maintenance', 'Offline', 'Disconnected']

    def process_request(self, action, args, output):
        """
        Generic method to handle process request

        Args:
            action ([string]): Take cluster action for each request.
            args ([dict]): Parameter pass to request to process.
        """
        # TODO Add validater
        # TODO Optimize if else
        if action == const.CLUSTER_COMMAND:
            if args.cluster_action == "add_node":
                self.add_node(args.node)
            elif args.cluster_action == "remove_node":
                self.remove_node(args.node)
            elif args.cluster_action == "start":
                self.start()
            elif args.cluster_action == "stop":
                self.stop()
            elif args.cluster_action == "status":
                self.status()
            elif args.cluster_action == "shutdown":
                self.shutdown()
        elif action == const.NODE_COMMAND:
            self._refresh_contex.process_request(action, args)
        else:
            raise HAUnimplemented()

    def node_status(self, node):
        """
        Check node status
        If node not detected return rc as 1 else 0
        Node status:
         Online:
         Standby:
         Maintenance:
         Offline:
        """
        Log.debug(f"Check {node} node status")
        # TODO: check is node is valid
        # TODO move node logic to node manager class
        _output, _err, _rc = self._execute.run_cmd("pcs status nodes")
        for status in _output.split("\n"):
            if node in status.split():
                node_rc = 0
                node_status = (status.split()[0])[:-1]
                Log.debug(f"For {node} node rc: {node_rc}, status: {node_status}")
                return node_rc, node_status
        Log.debug(f"{node} is not detected in cluster, treating as disconnected node")
        return 1, "Disconnected"

    def remove_node(self, node):
        """
        Remove node from pcs cluster
        """
        # TODO: Limitation for node remove (in cluster node cannot remove it self)
        # Check if node already removed
        _rc, status = self.node_status(node)
        if _rc != 1:
            self._execute.run_cmd(f"pcs cluster node remove {node} --force")
            _rc, status = self.node_status(node)
            Log.debug(f"For node {node} status: {status}, rc: {_rc}")
            if _rc != 1:
                Log.error(f"Failed to remove {node}")
                raise Exception(f"Failed to remove {node}")
            else:
                Log.info(f"Node {node} removed from cluster")
        else:
            Log.info(f"Node {node} already removed from cluster")

    def add_node(self, node):
        """
        Add new node to pcs cluster
        """
        # TODO: Limitation for node add (in cluster node cannot add it self)
        commands = [f"pcs cluster node add {node}",
                "pcs resource cleanup --all",
                f"pcs cluster enable {node}",
                f"pcs cluster start {node}"]
        _rc, status = self.node_status(node)
        if _rc != 0:
            for command in commands:
                self._execute.run_cmd(command)
            time.sleep(20)
            _rc, status = self.node_status(node)
            Log.debug(f"{node} status rc: {_rc}, status: {status}")
            if status != 'Online':
                Log.error(f"Failed to add {node}")
                raise Exception(f"Failed to add {node}")
            else:
                Log.info(f"Node {node} added to cluster")
        else:
            Log.info(f"Node {node} already added to cluster")

    def start(self):
        # TODO Add wrapper to hctl pcswrap
        raise HAUnimplemented()

    def stop(self):
        # TODO Add wrapper to hctl pcswrap
        raise HAUnimplemented()

    def status(self):
        # TODO Add wrapper to hctl pcswrap
        raise HAUnimplemented()

    def shutdown(self):
        raise HAUnimplemented()

class CortxClusterManager:
    def __init__(self):
        """
        Manage cluster operation
        """
        self._execute = SimpleCommand()

    def process_request(self, action, args, output):
        """
        Process cluster request

        Args:
            action (string): action taken on cluster
            args (dictonery): parameteter
            output (object): Store output

        Raises:
            HAUnimplemented: [description]
        """
        # TODO: Provide service and node management
        self._output = output
        if action == const.CLUSTER_COMMAND:
            getattr(self, args.cluster_action)()

    def remove_node(self):
        raise HAUnimplemented("Cluster remove node is not supported.")

    def add_node(self):
        raise HAUnimplemented("Cluster add node is not supported.")

    def start(self):
        Log.debug("Executing cluster start")
        _output, _err, _rc = self._execute.run_cmd(const.HCTL_START, check_error=False)
        Log.info(f"IO stack started. Output: {_output}, Err: {_err}, RC: {_rc}")
        self.status()
        if self._output.get_rc() == 0:
            Log.info("Cluster started successfully")
            self._output.output("Cluster started successfully")
            self._output.rc(0)
        else:
            Log.error("Cluster failed to start")
            self._output.output("Cluster failed to start")
            self._output.rc(1)

    def stop(self):
        Log.info("Executing cluster Stop")
        _output, _err, _rc = self._execute.run_cmd(const.HCTL_STOP, check_error=False)
        Log.info(f"Io stack stopped successfully. Output: {_output}, Err: {_err}, RC: {_rc}")
        self.status()
        if self._output.get_rc() == 1:
            Log.info("Cluster stopped successfully")
            self._output.output("Cluster stopped successfully...")
            self._output.rc(0)
        else:
            Log.error("Cluster failed to stop")
            self._output.output("Cluster failed to stop")
            self._output.rc(1)

    def status(self):
        _output, _err, _rc = self._execute.run_cmd(const.HCTL_STATUS, check_error=False)
        self._output.rc(_rc)
        status = const.HCTL_STARTED_STATUS if _rc == 0 else const.HCTL_STOPPED_STATUS
        self._output.output(status)

    def shutdown(self):
        raise HAUnimplemented("Cluster shutdown is not supported.")