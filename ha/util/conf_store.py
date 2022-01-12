#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.


"""
Wrappeprs for using the search APIs from conf store
"""

import json

from cortx.utils.conf_store import Conf
from cortx.utils.cortx.const import Const
from ha.core.config.config_manager import ConfigManager
from ha.k8s_setup.const import CLUSTER_CARDINALITY_KEY, CLUSTER_CARDINALITY_NUM_NODES, CLUSTER_CARDINALITY_LIST_NODES
from ha.k8s_setup.const import NODE_CONST, SERVICE_CONST, _DELIM
from cortx.utils.log import Log
from ha.core.error import ClusterCardinalityError

class ConftStoreSearch:
    """
    Wrapper class for using the confstore search APIs
    """

    def __init__(self):
        """Init method"""
        self._confstore = ConfigManager.get_confstore()


    def _get_data_pods(self, index):
        """
        Get machine ids for data pods: returns list of machine ids.
        """
        machine_ids = []
        keys = Conf.search(index, NODE_CONST, SERVICE_CONST, Const.SERVICE_MOTR_IO.value)
        for key in keys:
            machine_id = key.split('>')[1]
            # Add machine id to list
            machine_ids.append(machine_id)
        return machine_ids

    def _get_server_pods(self, index):
        """
        Get machine ids for server pods: returns list of machine ids.
        """
        machine_ids = []
        keys = Conf.search(index, NODE_CONST, SERVICE_CONST, Const.SERVICE_S3_HAPROXY.value)
        for key in keys:
            machine_id = key.split('>')[1]
            # Add machine id to list
            machine_ids.append(machine_id)
        return machine_ids

    def get_cluster_cardinality(self):
        """
        Get number of nodes(pods) and their machine ids from confstore
        """

        cluster_cardinality_key = CLUSTER_CARDINALITY_KEY
        if self._confstore.key_exists(cluster_cardinality_key):
            cluster_cardinality = self._confstore.get(cluster_cardinality_key)
            _, nodes_list = cluster_cardinality.popitem()
            nodes_dict = json.loads(nodes_list)

            #Get  number of nodes and the node list
            num_nodes = nodes_dict[CLUSTER_CARDINALITY_NUM_NODES]
            nodes_list = nodes_dict[CLUSTER_CARDINALITY_LIST_NODES]
            return num_nodes, nodes_list

        else:
            Log.error(f"Unable to get cluster cardinality. Key {CLUSTER_CARDINALITY_KEY} does not exist")
            raise ClusterCardinalityError("Unable to get cluster cardinality")

    def set_cluster_cardinality(self, index):
        """
        Set number of nodes(pods) and their machine ids in confstore used by HA
        """

        data_pods = self._get_data_pods(index)
        server_pods = self._get_server_pods(index)

        # Combine the lists data_pods, server_pod and find unique machine ids
        watch_pods = data_pods + server_pods
        watch_pods = list(set(watch_pods))
        num_pods = len(watch_pods)

        Log.info(f"Cluster cardinality: number of nodes {num_pods}, machine ids for nodes {watch_pods} ")

        if num_pods is 0:
            Log.warn(f"Possible cluster cardinality issue; number of pods to be watched {num_pods}")

        # Update the same to consul; if KV already present, it will be modified.
        cluster_cardinality_key = CLUSTER_CARDINALITY_KEY
        cluster_cardinality_value = {CLUSTER_CARDINALITY_NUM_NODES: num_pods, CLUSTER_CARDINALITY_LIST_NODES : watch_pods }
        self._confstore.update(cluster_cardinality_key, json.dumps(cluster_cardinality_value))
