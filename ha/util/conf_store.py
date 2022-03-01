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
from ha.k8s_setup.const import _DELIM, GconfKeys
from cortx.utils.log import Log
from ha.core.error import ClusterCardinalityError


class ConftStoreSearch:
    """
    Wrapper class for using the confstore search APIs
    """

    def __init__(self, conf_store_req: bool = True):
        """Init method"""
        if conf_store_req:
            self._confstore = ConfigManager.get_confstore()

    def get_data_pods(self, index):
        """
        Get machine ids for data pods: returns list of machine ids.
        """
        machine_ids = []
        # Sample output of the serach API
        # ex: Conf.search("cortx", "node", "services", Const.SERVICE_MOTR_IO.value)
        # ['node>5f3dc3a153454a918277ee4a2c57f36b>components[1]>services[0]',
        # 'node>6203a14bde204e8ea798ad9d42583fb5>components[1]>services[0]', 'node>8cc8b13101e34b3ca1e51ed6e3228d5b>components[1]>services[0]']

        data_pod_keys = Conf.search(index, GconfKeys.NODE_CONST.value, GconfKeys.SERVICE_CONST.value, Const.SERVICE_MOTR_IO.value)
        for key in data_pod_keys:
            machine_id = key.split('>')[1]
            # Add machine id to list
            machine_ids.append(machine_id)
        return machine_ids

    def get_server_pods(self, index):
        """
        Get machine ids for server pods: returns list of machine ids.
        """
        machine_ids = []
        server_pod_keys = Conf.search(index, GconfKeys.NODE_CONST.value, GconfKeys.SERVICE_CONST.value, Const.SERVICE_S3_HAPROXY.value)
        for key in server_pod_keys:
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

        data_pods = self.get_data_pods(index)
        server_pods = self.get_server_pods(index)

        # Combine the lists data_pods, server_pod and find unique machine ids
        watch_pods = data_pods + server_pods
        watch_pods = list(set(watch_pods))
        num_pods = len(watch_pods)

        Log.info(f"Cluster cardinality: number of nodes {num_pods}, machine ids for nodes {watch_pods} ")

        if num_pods == 0:
            Log.warn(f"Possible cluster cardinality issue; number of pods to be watched {num_pods}")

        # Update the same to consul; if KV already present, it will be modified.
        cluster_cardinality_key = CLUSTER_CARDINALITY_KEY
        cluster_cardinality_value = {CLUSTER_CARDINALITY_NUM_NODES: num_pods, CLUSTER_CARDINALITY_LIST_NODES : watch_pods }
        self._confstore.update(cluster_cardinality_key, json.dumps(cluster_cardinality_value))

    @staticmethod
    def _get_cvg_count(index, node_id):
        cvg_count = Conf.get(index, GconfKeys.CVG_COUNT.value.format(_DELIM=_DELIM, node_id=node_id))
        if not cvg_count:
            Log.warn(f"CVGs are not available for this node {node_id}")
        return cvg_count

    @staticmethod
    def get_cvg_list(index, node_id):
        """
        Return list of CVG's for any given node.
        Args:
            index(str): index of conf file
            node_id (str): node id
        Returns:
            list: list of CVG's

        >>> ConftStoreSearch.get_cvg_list("cortx", '21d6291109304485b3daff43a06cff77')
        ['cvg-01', 'cvg-02']
        """
        cvg_list = []
        try:
            cvg_count = ConftStoreSearch._get_cvg_count(index, node_id)
            if cvg_count:
                cvg_list = [Conf.get(index, GconfKeys.CVG_NAME.value.format
                                     (_DELIM=_DELIM, node_id=node_id, cvg_index=cvg_index)) for cvg_index in range(cvg_count)]
            return cvg_list
        except Exception as e:
            Log.error(f"Unable to fetch CVG list from GConf. Error {e}")
            raise Exception(f"Unable to fetch CVG list. Error {e}")

    @staticmethod
    def _get_data_disks(index, node_id, cvg_index):
        disk_list = []
        num_of_data_disks = Conf.get(index, GconfKeys.DATA_COUNT.value.format
                                     (_DELIM=_DELIM, node_id=node_id, cvg_index=cvg_index))
        if num_of_data_disks:
            for d_index in range(num_of_data_disks):
                disk_list.append(Conf.get(index, GconfKeys.DATA_DISK.value.format
                                          (_DELIM=_DELIM, node_id=node_id, cvg_index=cvg_index, d_index=d_index)))
        return disk_list

    @staticmethod
    def _get_metadata_disks(index, node_id, cvg_index):
        mdisk_list = []
        num_of_metadata_disks = Conf.get(index, GconfKeys.METADATA_COUNT.value.format
                                         (_DELIM=_DELIM, node_id=node_id, cvg_index=cvg_index))
        if num_of_metadata_disks:
            for m_index in range(num_of_metadata_disks):
                mdisk_list.append(Conf.get(index, GconfKeys.METADATA_DISK.value.format
                                           (_DELIM=_DELIM, node_id=node_id, cvg_index=cvg_index, m_index=m_index)))
        return mdisk_list

    @staticmethod
    def get_disk_list(index, node_id):
        """
        Return list of disks for any given node
        Args:
            index(str): index of conf file
            node_id (str): node id
        Returns:
            list: list of disks id's

        >>> ConftStoreSearch.get_disk_list("cortx", '21d6291109304485b3daff43a06cff77')
        ['/dev/sdd', '/dev/sde', '/dev/sdc', '/dev/sdg', '/dev/sdh', '/dev/sdf']
        """
        disk_list = []
        try:
            cvg_count = ConftStoreSearch._get_cvg_count(index, node_id)
            if cvg_count:
                for cvg_index in range(cvg_count):
                    for disk in ConftStoreSearch._get_data_disks(index, node_id, cvg_index):
                        disk_list.append(disk)
                    for mdisk in ConftStoreSearch._get_metadata_disks(index, node_id, cvg_index):
                        disk_list.append(mdisk)
            return disk_list
        except Exception as e:
            Log.error(f"Unable to fetch Disk list from GConf. Error {e}")
            raise Exception(f"Unable to fetch Disk list. Error {e}")

    @staticmethod
    def get_disk_list_for_cvg(index, node_id, cvg_id):
        """
        Return list of disks for any given node and CVG.
        Args:
            index(str): index of conf file
            node_id (str): node id
            cvg_id (str): cvg id
        Returns:
            list: list of disks id's

        >>> ConftStoreSearch.get_disk_list_for_cvg("cortx", '21d6291109304485b3daff43a06cff77', 'cvg-01')
        ['/dev/sdd', '/dev/sde', '/dev/sdc']
        """
        disk_list = []
        try:
            cvg_list = ConftStoreSearch.get_cvg_list(index, node_id)
            if cvg_id in cvg_list:
                cvg_index = cvg_list.index(cvg_id)
                for disk in ConftStoreSearch._get_data_disks(index, node_id, cvg_index):
                    disk_list.append(disk)
                for mdisk in ConftStoreSearch._get_metadata_disks(index, node_id, cvg_index):
                    disk_list.append(mdisk)
            return disk_list
        except Exception as e:
            Log.error(f"Unable to fetch Disk list from GConf. Error {e}")
            raise Exception(f"Unable to fetch Disk list. Error {e}")
