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

import json
import time
from cortx.utils.log import Log

from ha.core.error import HAUnimplemented
from ha.core.controllers.pcs.pcs_controller import PcsController
from ha.core.error import ClusterManagerError
from ha.core.controllers.cluster_controller import ClusterController
from ha.core.controllers.controller_annotation import controller_error_handler
from ha import const

class PcsClusterController(ClusterController, PcsController):
    """ Pcs cluster controller to perform pcs cluster level operation. """

    def __init__(self):
        """
        Initalize pcs cluster controller
        """
        super(PcsClusterController, self).__init__()

    def initialize(self, controllers):
        """
        Initialize the cluster controller
        """
        self._controllers = controllers

    def _is_pcs_cluster_running(self):
        """
        Check pcs cluster status
        """
        _, _, _rc = self._execute.run_cmd(const.PCS_CLUSTER_STATUS, check_error=False)
        if _rc != 0:
            return False
        return True

    def _pcs_cluster_start(self):
        """
        Start pcs cluster
        """
        _status = const.STATUSES.FAILED.value
        self._execute.run_cmd(const.PCS_CLUSTER_START_NODE, check_error=False)
        for retry_index in range(0, const.CLUSTER_RETRY_COUNT):
            time.sleep(const.BASE_WAIT_TIME)
            _status = self._is_pcs_cluster_running()
            if _status is True:
                _status = const.STATUSES.SUCCEEDED.value
                break
            Log.info(f"Pcs cluster start retry index : {retry_index}")
        return _status

    def _auth_node(self, node_id, cluster_user, cluster_password):
        """
        Auth node to add
        """
        try:
            self._execute.run_cmd(const.PCS_CLUSTER_NODE_AUTH.replace("<node>", node_id)
                    .replace("<username>", cluster_user).replace("<password>", cluster_password),
                    is_secret=True, error=f"Auth to {node_id} failed.")
            Log.info(f"Node {node_id} authenticated with {cluster_user} Successfully.")
        except Exception as e:
            Log.error(f"Failed to authenticate node : {node_id} with reason : {e}")
            raise ClusterManagerError(f"Failed to authenticate node : {node_id}, Please check username or password")

    @controller_error_handler
    def start(self) -> dict:
        """
        Start cluster and all service.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        if self._is_pcs_cluster_running() is False:
            _res = self._pcs_cluster_start()
            if _res != const.STATUSES.SUCCEEDED.value:
                return {"status": const.STATUSES.FAILED.value, "msg": "Cluster start operation failed"}

        _res = self.node_list()
        _res = json.loads(_res)

        if _res.get("status") == const.STATUSES.SUCCEEDED.value:
            _node_list = _res.get("msg")
            Log.info(f"Node List : {_node_list}")
            if _node_list is not None:
                _node_group = [ _node_list[i:i + const.PCS_NODE_START_GROUP_SIZE] for i in range(0, len(_node_list), const.PCS_NODE_START_GROUP_SIZE)]

                for _node_subgroup in _node_group:
                    for _node_id in _node_subgroup:
                        _res = self._controllers[const.NODE_CONTROLLER].start(_node_id)
                        _res = json.loads(_res)
                        if _res.get("status") == const.STATUSES.FAILED.value:
                            msg = _res.get("msg")
                            Log.error(f"Node {_node_id} : {msg}")
                    # Wait till all the resources get started in the sub group
                    time.sleep(const.BASE_WAIT_TIME * const.PCS_NODE_START_GROUP_SIZE)

                return {"status": const.STATUSES.IN_PROGRESS.value, "msg": "Cluster start operation performed"}
            else:
                return {"status": const.STATUSES.FAILED.value, "msg": "Cluster start failed. Not able to verify node list."}
        else:
            msg = _res.get("msg")
            return {"status": _res.get("status"), "msg": f"Cluster start operation failed, {msg}"}

    @controller_error_handler
    def stop(self) -> dict:
        """
        Stop cluster and all service.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def status(self) -> dict:
        """
        Status cluster and all service. It gives status for all resources.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":{}}
                status: Succeeded, Failed, InProgress
                msg: dict of resource and status.
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def standby(self) -> dict:
        """
        Put cluster in standby mode.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def active(self) -> dict:
        """
        Activate all node.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def node_list(self) -> dict:
        """
        Provide node list.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":[]}
                status: Succeeded, Failed, InProgress
        """
        #TODO: This is temporary implementation and It should be removed once nodelist is available in the system health.
        nodelist = []
        _output, _err, _rc = self._execute.run_cmd(const.PCS_STATUS_NODES, check_error=False)

        if _rc != 0:
            return {"status": const.STATUSES.FAILED.value, "msg": "Failed to get nodes status"}
        else:
            for status in _output.split("\n"):
                nodes = status.split(":")
                if len(nodes) > 1:
                    nodelist.extend(nodes[1].split())
            return {"status": const.STATUSES.SUCCEEDED.value, "msg": nodelist}

    @controller_error_handler
    def service_list(self) -> dict:
        """
        Provide service list.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":[]}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def storageset_list(self) -> dict:
        """
        Provide storageset list.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":[]}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def add_node(self, nodeid: str, cluster_user: str, cluster_password: str) -> dict:
        """
        Add new node to cluster.
        :param cluster_user:
        :param cluster_password:
        :param nodeid:
        Args:
            nodeid (str, required): Provide node_id.
            cluster_user (str, required): Provide cluster_user.
            cluster_password (str, required): Provide cluster_password.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        self._check_non_empty(nodeid=nodeid, cluster_user=cluster_user, cluster_password=cluster_password)
        self._auth_node(nodeid, cluster_user, cluster_password)
        cluster_node_count = self._get_cluster_size()
        if cluster_node_count < 32:
            _output, _err, _rc = self._execute.run_cmd(const.PCS_CLUSTER_NODE_ADD.replace("<node>", nodeid))
            return {"status": const.IN_PROGRESS.FAILED.value, "msg": f"Node {nodeid} add operation started successfully in the cluster"}
        else:
            return {"status": const.STATUSES.FAILED.value, "msg": "Cluster size is already filled to 32, "
                                               "Please use add-remote node mechanism"}

    @controller_error_handler
    def add_storageset(self, nodeid: str = None, descfile: str = None) -> dict:
        """
        Add new storageset to cluster.

        Args:
            nodeid (str, optional): Provide nodeid. Defaults to None.
            filename (str, optional): Provide descfile. Defaults to None.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def create_cluster(self, name: str, user: str, secret: str, nodeid: str) -> dict:
        """
        Create cluster if not created.

        Args:
            name (str): Cluster name.
            user (str): Cluster User.
            secret (str): Cluster passward.
            nodeid (str): Node name, nodeid of current node.

        Returns:
            dict: Return dictionary. {"status": "", "msg":""}
        """
        try:
            self._check_non_empty(name=name, user=user, secret=secret, nodeid=nodeid)
            if not self._is_pcs_cluster_running():
                self._auth_node(nodeid, user, secret)
                self._execute.run_cmd(const.PCS_SETUP_CLUSTER.replace("<cluster_name>", name)
                                        .replace("<node>", nodeid), is_secret=True,
                                        error="Cluster setup failed.")
                Log.info("Pacmaker cluster created, waiting to start node.")
                self._execute.run_cmd(const.PCS_CLUSTER_START_NODE)
                self._execute.run_cmd(const.PCS_CLUSTER_ENABLE.replace("<node>", nodeid))
                Log.info("Node started and enabled successfully.")
                # TODO: Divide class into vm, hw when stonith is needed.
                self._execute.run_cmd(const.PCS_STONITH_DISABLE)
                time.sleep(const.BASE_WAIT_TIME * 2)
            if self._is_pcs_cluster_running():
                return {"status": const.STATUSES.SUCCEEDED.value,
                        "msg": "Cluster created successfully."}
            else:
                raise ClusterManagerError("Cluster is not started.")
        except Exception as e:
            raise ClusterManagerError(f"Failed to create cluster. Error: {e}")
