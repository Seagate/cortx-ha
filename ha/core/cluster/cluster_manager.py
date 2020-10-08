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
**************************************************************************
 Description:       Cluster Management
****************************************************************************
"""

import time

from cortx.utils.log import Log
from cortx.utils.ha.dm.decision_monitor import DecisionMonitor

from ha.core.error import HAUnimplemented
from ha.core.node.replacement.refresh_context import PcsRefreshContex
from ha.execute import SimpleCommand
from ha.core.support_bundle.ha_bundle import HABundle
from ha import const

class ClusterManager:
    def __init__(self):
        """
        Manage cluster operation
        """
        pass

    def node_status(self, node):
        pass

    def remove_node(self, node):
        pass

    def add_node(self, node):
        pass

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
        if action == const.CLUSTER_COMMAND:
            if args.cluster_action in ["add_node", "remove_node"]:
                getattr(self, args.cluster_action)(args.node)
            else:
                getattr(self, args.cluster_action)()
        elif action == const.NODE_COMMAND:
            self._refresh_contex.process_request(action, args)
        elif action == const.BUNDLE_COMMAND:
            HABundle().process_request(action, args, output)
        else:
            raise HAUnimplemented("This feature is not supported...")

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
        return 1, const.NODE_DISCONNECTED

    def remove_node(self, node):
        """
        Remove node from pcs cluster
        """
        # TODO: Limitation for node remove (in cluster node cannot remove it self)
        # Check if node already removed
        _output, _err, _rc = self._execute.run_cmd(const.PCS_STATUS)
        Log.info(f"Cluster status output before remove node: {_output}, {_err}, {_rc}")
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
        _output, _err, _rc = self._execute.run_cmd(const.PCS_STATUS)
        Log.info(f"Cluster status output after remove node: {_output}, {_err}, {_rc}")

    def add_node(self, node):
        """
        Add new node to pcs cluster
        """
        _output, _err, _rc = self._execute.run_cmd(const.PCS_STATUS)
        Log.info(f"Cluster status output before add node: {_output}, {_err}, {_rc}")
        # TODO: Limitation for node add (in cluster node cannot add it self)
        commands = [f"pcs cluster node add {node}",
                f"pcs cluster enable {node}",
                f"pcs cluster start {node}",
                "pcs resource cleanup --all"]
        _rc, status = self.node_status(node)
        if _rc != 0:
            for command in commands:
                _output, _err, _rc = self._execute.run_cmd(command)
                Log.info(f"{command} : {_output}, {_err}, {_rc}")
                time.sleep(5)
            retries = 0
            add_node_flag = -1
            while retries < 12:
                _rc, status = self.node_status(node)
                Log.info(f"{node} status rc: {_rc}, status: {status}")
                if status == const.NODE_ONLINE:
                    Log.info(f"Node {node} added to cluster")
                    add_node_flag = 0
                    break
                elif status != const.NODE_DISCONNECTED:
                    add_node_flag = 1
                    Log.info(f"Node {node} added to cluster but not Online check status again.")
                retries += 1
                time.sleep(10)
            if add_node_flag == 1:
                Log.info(f"Node {node} added to cluster but not in Online state.")
            elif add_node_flag == 0:
                Log.info(f"Node {node} Successfully added to cluster and in Online state")
            else:
                raise Exception(f"Failed to add {node} to cluster")
        else:
            Log.info(f"Node {node} already added to cluster")
        _output, _err, _rc = self._execute.run_cmd(const.PCS_STATUS)
        Log.info(f"Cluster status output after add node: {_output}, {_err}, {_rc}")

    def start(self):
        # TODO Add wrapper to hctl pcswrap
        raise HAUnimplemented("This feature is not supported...")

    def stop(self):
        # TODO Add wrapper to hctl pcswrap
        raise HAUnimplemented("This feature is not supported...")

    def status(self):
        # TODO Add wrapper to hctl pcswrap
        raise HAUnimplemented("This feature is not supported...")

    def shutdown(self):
        raise HAUnimplemented("This feature is not supported...")