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

from ha.core.error import HAUnimplemented
from ha.core.controllers.pcs.pcs_controller import PcsController
from ha.core.controllers.node_controller import NodeController
from ha.core.controllers.controller_annotation import controller_error_handler
from ha import const
from cortx.utils.log import Log


class PcsNodeController(NodeController, PcsController):
    """ Controller to manage node. """

    def __init__(self):
        """
        Initalize PcsNodeController
        """
        super(PcsNodeController, self).__init__()

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
        Stop node with nodeid.

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
        raise HAUnimplemented("This operation is not implemented.")

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
        all_nodes_status = dict()
        _output, _err, _rc = self._execute.run_cmd(const.PCS_STATUS_NODES, check_error=False)
        if nodeids is not None:
            for nodeid in nodeids:
                if nodeid in _output:
                    _node_status = "unknown"
                    for status in _output.split("\n"):
                        nodes = status.split(":", 1)
                        if nodeid in nodes[1]:
                            _node_status = nodes[0].trim()
                    all_nodes_status[nodeid] = _node_status
        return {"status": "Succeeded", "msg": all_nodes_status}


class PcsVMNodeController(PcsNodeController):
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
        _res = self.status([nodeid])
        _all_node_status = _res.get("msg")
        _node_status = _all_node_status.get(nodeid)
        if _node_status == "Standby":
            # make node unstandby
            _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_UNSTANDBY.replace("<node>", nodeid),
                                                       check_error=False)
            return {"status": "", "msg": _output}
        elif _node_status == "Offline":
            # start node not in scope of VM
            Log.error("Operation not available for VM")
        return {"status": "Succeeded", "msg": "Node s"}

    @controller_error_handler
    def stop(self, nodeid: str) -> dict:
        """
        Stop node with nodeid.

        Args:
            nodeid (str): Node ID from cluster nodes.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

class PcsHWNodeController(PcsNodeController):
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
        Stop node with nodeid.

        Args:
            nodeid (str): Node ID from cluster nodes.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")
