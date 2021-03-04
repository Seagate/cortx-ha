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

from ha.core.controllers.element_controller import ElementController
from ha.execute import SimpleCommand
from ha import const
from ha.core.error import HAInvalidNode, ClusterManagerError
from ha.const import NODE_STATUSES



class PcsController(ElementController):
    """ Generic Controller for Pcs to execute common pcs command """

    def __init__(self):
        """
        Initalize pcs controller
        """
        super(PcsController, self).__init__()
        self._execute = SimpleCommand()

    def check_resource_failcount(self) -> bool:
        """
        Resource fail count check
        """
        count = 0
        while True:
            time.sleep(10)
            _output, _err, _rc = self._execute.run_cmd(const.PCS_FAILCOUNT_STATUS,
                                                       check_error=False)
            if _output == const.NO_FAILCOUNT:
                failcount_found = False
            else:
                failcount_found = True

            if count >= const.RETRY_COUNT:
                break
            if failcount_found:
                _output, _err, _rc = self._execute.run_cmd(const.PCS_CLEANUP,
                                                               check_error=False)
            count += 1
        return failcount_found

    def nodes_status(self, nodeids: list = None) -> dict:
        """
        Get pcs status of nodes.
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
        if nodeids is not None and isinstance(nodeids, list):
            for nodeid in nodeids:
                if nodeid in _output:
                    for status in _output.split("\n"):
                        nodes = status.split(":")
                        if len(nodes) > 1 and nodeid.lower() in nodes[1].strip().lower():
                            if nodes[0].strip().lower() == NODE_STATUSES.STANDBY.value.lower():
                                all_nodes_status[nodeid] = NODE_STATUSES.STANDBY.value
                            elif nodes[0].strip().lower() == NODE_STATUSES.STANDBY_WITH_RESOURCES_RUNNING.value.lower():
                                all_nodes_status[nodeid] = NODE_STATUSES.STANDBY_WITH_RESOURCES_RUNNING.value
                            elif nodes[0].strip().lower() == NODE_STATUSES.MAINTENANCE.value.lower():
                                all_nodes_status[nodeid] = NODE_STATUSES.MAINTENANCE.value
                            elif nodes[0].strip().lower() == NODE_STATUSES.OFFLINE.value.lower():
                                all_nodes_status[nodeid] = NODE_STATUSES.OFFLINE.value
                            elif nodes[0].strip().lower() == NODE_STATUSES.ONLINE.value.lower():
                                all_nodes_status[nodeid] = NODE_STATUSES.ONLINE.value
                            break
                    else:
                        all_nodes_status[nodeid] = NODE_STATUSES.UNKNOWN.value
                else:
                    raise HAInvalidNode(f"Node {nodeid} is not a part of cluster")
            return all_nodes_status
        else:
            raise ClusterManagerError("Either nodeids is None or not a list to check the status")
