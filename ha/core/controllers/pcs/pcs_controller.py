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
import re
import socket

from ha.core.controllers.element_controller import ElementController
from ha.execute import SimpleCommand
from ha import const
from ha.core.error import HAInvalidNode, ClusterManagerError, HAClusterCLIError
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

    def _check_non_empty(self, **kwargs):
        """
        Check if params are not empty.

        Raises:
            ClusterManagerError: [description]
        """
        for key in kwargs.keys():
            if kwargs[key] is None or kwargs[key] == "":
                raise ClusterManagerError(f"Failed: Invalid parameter, {key} cannot be empty.")

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
        _output, _err, _rc = self._execute.run_cmd(const.PCS_FAILCOUNT_STATUS, check_error=False)
        if node_id in _output:
            return True
        else:
            return False

    def clean_failure_count(self, node_id):
        """
        Cleanup resources fail count
        """
        _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_CLEANUP.replace("<node>", node_id),
                                                   check_error=False)

    def _get_cluster_size(self):
        """
        Auth node to add
        """
        try:
            _output, _err, _rc = self._execute.run_cmd(const.PCS_CLUSTER_PCSD_STATUS)
            return len(_output.split("\n"))
        except Exception as e:
            raise ClusterManagerError(f"Unable to get cluster : with reason : {e}")

    def _get_node_list(self) -> list:
        """
        Return list of nodes.
        """
        #TODO: This is temporary implementation and It should be removed once nodelist is available in the system health.
        nodelist = []
        _output, _err, _rc = self._execute.run_cmd(const.PCS_STATUS_NODES, check_error=False)

        if _rc != 0:
            raise ClusterManagerError("Failed to get nodes status")
        for status in _output.split("\n"):
            nodes = status.split(":")
            if len(nodes) > 1:
                nodelist.extend(nodes[1].split())
        return nodelist

    def nodes_status(self, nodeids: list = None) -> dict:
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
        nodeids = self._get_node_list() if nodeids == None or len(nodeids) == 0 else nodeids
        all_nodes_status = dict()
        _output, _err, _rc = self._execute.run_cmd(const.PCS_STATUS_NODES, check_error=False)
        if not isinstance(nodeids, list):
            raise ClusterManagerError(f"Invalid nodeids type `{type(nodeids)}`, required `list`")
        for nodeid in nodeids:
            if nodeid in _output:
                for status in _output.split("\n"):
                    nodes = status.split(":")
                    if len(nodes) > 1 and nodeid.lower() in nodes[1].strip().lower():
                        if nodes[0].strip().lower() == NODE_STATUSES.STANDBY.value:
                            all_nodes_status[nodeid] = NODE_STATUSES.STANDBY.value
                        elif nodes[0].strip().lower() == NODE_STATUSES.STANDBY_WITH_RESOURCES_RUNNING.value:
                            all_nodes_status[nodeid] = NODE_STATUSES.STANDBY_WITH_RESOURCES_RUNNING.value
                        elif nodes[0].strip().lower() == NODE_STATUSES.MAINTENANCE.value:
                            all_nodes_status[nodeid] = NODE_STATUSES.MAINTENANCE.value
                        elif nodes[0].strip().lower() == NODE_STATUSES.CLUSTER_OFFLINE.value:
                            all_nodes_status[nodeid] = NODE_STATUSES.CLUSTER_OFFLINE.value
                        elif nodes[0].strip().lower() == NODE_STATUSES.ONLINE.value:
                            all_nodes_status[nodeid] = NODE_STATUSES.ONLINE.value
                        break
                else:
                    all_nodes_status[nodeid] = NODE_STATUSES.UNKNOWN.value
            else:
                raise HAInvalidNode(f"Node {nodeid} is not a part of cluster")
        for node in all_nodes_status.keys():
            status = all_nodes_status[node]
            if status == NODE_STATUSES.CLUSTER_OFFLINE.value:
                _output, _err, _rc = self._execute.run_cmd(f"ping -c 1 {node}", check_error=False)
                if _rc != 0:
                    all_nodes_status[node] = NODE_STATUSES.POWEROFF.value
        return all_nodes_status

    def _get_filtered_nodes(self, status: list) -> list:
        """
        List of node matches from above status.

        Args:
            status (list): Status list of node

        Returns:
            list: List of node
        """
        nodelist = []
        node_status = self.nodes_status()
        for node in node_status.keys():
            if node_status[node] in status:
                nodelist.append(node)
        return nodelist

    def is_valid_node_id(self, node_id) -> bool:
        '''
           Checks if node id gets resolved to some IP address or not
           Returns: bool
           Exception: socket.gaierror, socket.herror
        '''

        # TODO: change this logic and validate the node_id from the
        # list coming from system health
        ip_validator_regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
    
        # node_id can be passed as IP address or FQDN or
        # some random number or just sequence of chars

        # first seperate the string from dots.
        splitted_node_id = node_id.replace('.', '')

        # If string only contains numbers, means it can be just
        # random number or can be an IP address. So, IP address
        # validation can be done. else for random number, exception will be
        # raised
        if re.search('^[0-9]*$', splitted_node_id):
            if re.search(ip_validator_regex, node_id):
                return True
            raise HAClusterCLIError(f'{node_id} is not a valid node_id')
        # else it can be combination of chars and numbers means hostname or just a
        # random meaningless string
        else:
            try:
                socket.gethostbyname(node_id)
            except Exception as err:
                raise HAClusterCLIError(f'{node_id} not a valid node_id: {err}')
        return True