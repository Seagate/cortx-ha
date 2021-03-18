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
import json

from ha.core.controllers.element_controller import ElementController
from ha.execute import SimpleCommand
from ha import const
from ha.core.error import HAInvalidNode, ClusterManagerError
from ha.const import NODE_STATUSES
from cortx.utils.log import Log


class PcsController(ElementController):
    """ Generic Controller for Pcs to execute common pcs command """

    def __init__(self):
        """
        Initialize pcs controller
        """
        super(PcsController, self).__init__()
        self._execute = SimpleCommand()

    @staticmethod
    def load_json_file(json_file):
        """
        Load json file to read node & the cluster details to auth node
        :param json_file:
        """
        try:
            with open(json_file) as f:
                return json.load(f)
        except Exception as e:
            raise ClusterManagerError(f"Error in reading desc_file, reason : {e}")

    def heal_resource(self, node_id):
        """
        Heal the resources if there are any fail count exists
        """
        count = 0
        resources_healed = False
        while True:
            if count >= const.RETRY_COUNT:
                break
            fail_count_exists = self.check_resource_failcount(node_id)
            if fail_count_exists:
                self.clean_failure_count(node_id)
            else:
                resources_healed = True
                break
            count += 1
            time.sleep(10)
        return resources_healed

    def check_resource_failcount(self, node_id) -> bool:
        """
        Resource fail count check
        """
        _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_FAILCOUNT_STATUS.replace("<node>", node_id),
                                                   check_error=False)
        if const.NO_FAILCOUNT in _output:
            return False
        else:
            return True

    def clean_failure_count(self, node_id):
        """
        Cleanup resources fail count
        """
        _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_CLEANUP.replace("<node>", node_id),
                                                   check_error=False)

    def _auth_node(self, node_id, cluster_user, cluster_password):
        """
        Auth node to add
        """
        try:
            _output, _err, _rc = self._execute.run_cmd(const.PCS_CLUSTER_NODE_AUTH.replace("<node>", node_id)
                                                       .replace("<username>", cluster_user)
                                                       .replace("<password>", cluster_password))
        except Exception as e:
            Log.error(f"Failed to authenticate node : {node_id} with reason : {e}")
            raise ClusterManagerError(f"Failed to authenticate node : {node_id}, Please check username or password")

    def _get_cluster_size(self):
        """
        Auth node to add
        """
        try:
            _output, _err, _rc = self._execute.run_cmd(const.PCS_CLUSTER_PCSD_STATUS)
            return len(_output.split("\n"))
        except Exception as e:
            raise ClusterManagerError(f"Unable to get cluster : with reason : {e}")

    def nodes_status(self, nodeids: list) -> dict:
        """
        Get pcs status of nodes.
        Args:
            nodeids (list): List of Node IDs from cluster nodes.
                Default provide list of all node status.
                if 'local' then provide local node status.

        Returns:
            ([dict]): Return dictionary. {"node_id1": "status of node_id1",
                                          "node_id2": "status of node_id2"...}
        """
        all_nodes_status = dict()
        _output, _err, _rc = self._execute.run_cmd(const.PCS_STATUS_NODES, check_error=False)
        if not isinstance(nodeids, list):
            raise ClusterManagerError(f"Invalid nodeids type `{type(nodeids)}`, required `list`")
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
