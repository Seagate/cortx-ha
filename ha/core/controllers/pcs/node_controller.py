#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
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

from ha.core.error import HAUnimplemented, ClusterManagerError
from ha.core.controllers.pcs.pcs_controller import PcsController
from ha.core.controllers.node_controller import NodeController
from ha.core.controllers.controller_annotation import controller_error_handler
from ha import const
from ha.const import NODE_STATUSES
from cortx.utils.log import Log


class PcsNodeController(NodeController, PcsController):
    """ Controller to manage node. """

    def __init__(self):
        """
        Initalize PcsNodeController
        """
        super(PcsNodeController, self).__init__()

    def initialize(self, controllers):
        """
        Initialize the node controller
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def start(self, nodeid: str) -> dict:
        """
        Start node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def stop(self, nodeid: str) -> dict:
        """
        Stop Cluster on node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        node_status = self.nodes_status([nodeid]).get(nodeid)
        # TODO: node_status should give diff between poweroff and offline
        if node_status.lower() == NODE_STATUSES.OFFLINE.value.lower():
            Log.info(f"For stop {nodeid}, Node already in offline state.")
            status = f"Node {nodeid} is already in offline state."
        else:
            if self.heal_resource(nodeid):
                time.sleep(const.BASE_WAIT_TIME)
            try:
                self._execute.run_cmd(const.PCS_STOP_NODE.replace("<node>", nodeid))
                Log.info(f"Executed node stop for {nodeid}, Waiting to stop resource")
                time.sleep(const.BASE_WAIT_TIME)
                status = f"Stop for {nodeid} is in progress, waiting to stop resource"
            except Exception as e:
                raise ClusterManagerError(f"Failed to stop {nodeid}, Error: {e}")
        return {"status": const.STATUSES.IN_PROGRESS.value, "msg": status}

    @controller_error_handler
    def shutdown(self, nodeid: str) -> dict:
        """
        Shutdown node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def standby(self, nodeid: str) -> dict:
        """
        Standby node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        status: str = ""
        # Check node status
        node_status = self.nodes_status([nodeid]).get(nodeid).lower()
        Log.info(f"Current {nodeid} status is {node_status}")
        if node_status == NODE_STATUSES.STANDBY.value.lower():
            status = f"Node {nodeid} is already running in standby mode."
        elif node_status.lower() != NODE_STATUSES.ONLINE.value.lower():
            return {"status": const.STATUSES.FAILED.value,
                    "msg": f"Failed to put node in standby as node is in {node_status}"}
        else:
            if self.heal_resource(nodeid):
                time.sleep(const.BASE_WAIT_TIME)
            self._execute.run_cmd(const.PCS_NODE_STANDBY.replace("<node>", nodeid))
            Log.info(f"Waiting to standby {nodeid} node.")
            time.sleep(const.BASE_WAIT_TIME * 2)
            node_status = self.nodes_status([nodeid]).get(nodeid).lower()
            Log.info(f"After standby, current {nodeid} status is {node_status}")
            status = f"Waiting for resource to stop, {nodeid} standby is in progress"
        return {"status": const.STATUSES.IN_PROGRESS.value, "msg": status}

    @controller_error_handler
    def active(self, nodeid: str) -> dict:
        """
        Activate node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def status(self, nodeids: list = None) -> dict:
        """
        Get status of nodes.
        Args:
            nodeids (list): List of Node IDs from cluster nodes.
                Default provide list of all node status.
                if 'local' then provide local node status.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":{}}}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

class PcsVMNodeController(PcsNodeController):
    def initialize(self, controllers):
        """
        Initialize the node controller
        """
        self._controllers = controllers

    @controller_error_handler
    def start(self, nodeid: str) -> dict:
        """
        Start node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        _res = self.nodes_status([nodeid])
        _node_status = _res.get(nodeid)
        if _node_status.lower() == NODE_STATUSES.ONLINE.value.lower():
            return {"status": const.STATUSES.SUCCEEDED.value, "msg": f"Node {nodeid}, is already in Online status"}
        elif _node_status.lower() == NODE_STATUSES.STANDBY_WITH_RESOURCES_RUNNING.value.lower():
            return {"status": const.STATUSES.SUCCEEDED.value, "msg": f"Node {nodeid}, is going in standby mode, "
                                                  f"We need to wait to complete the resource shutdown"}
        elif _node_status.lower() == NODE_STATUSES.STANDBY.value.lower():
            # make node unstandby
            if self.heal_resource(nodeid):
                _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_UNSTANDBY.replace("<node>", nodeid),
                                                           check_error=False)
                return {"status": const.STATUSES.IN_PROGRESS.value, "msg": f"Node {nodeid} : Node was in standby mode, "
                                                       f"Unstandby operation started successfully"}
            else:
                Log.error(f"Node {nodeid} is in standby mode : Resource failcount found on the node, "
                          f"cleanup not worked after 2 retries")
                return {"status": const.STATUSES.FAILED.value, "msg": f"Node {nodeid} is in standby mode: Resource "
                                                   f"failcount found on the node cleanup not worked after 2 retries"}

        elif _node_status.lower() == NODE_STATUSES.OFFLINE.value.lower():
            # start node not in scope of VM
            Log.error("Operation not available for node type VM")
            raise ClusterManagerError(f"Node {nodeid} : Node was in offline mode, "
                                      "Node start : Operation not available for VM")

class PcsHWNodeController(PcsNodeController):
    def initialize(self, controllers):
        """
        Initialize the storageset controller
        """
        self._controllers = controllers

    @controller_error_handler
    def start(self, nodeid: str) -> dict:
        """
        Start node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def shutdown(self, nodeid: str) -> dict:
        """
        Shutdown node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")
