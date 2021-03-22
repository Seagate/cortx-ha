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

from ha.core.error import HAUnimplemented
from ha.core.controllers.pcs.pcs_controller import PcsController
from ha.core.controllers.cluster_controller import ClusterController
from ha.core.controllers.controller_annotation import controller_error_handler
from ha import const
from cortx.utils.log import Log


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
        if not nodeid:
            return {"status": "Failed", "msg": "Node_id is missing or empty to add node"}

        if not cluster_user:
            return {"status": "Failed", "msg": "Cluster username is missing or empty to add node"}

        if not cluster_password:
            return {"status": "Failed", "msg": "Cluster password is missing or empty to add node"}

        self._auth_node(nodeid, cluster_user, cluster_password)
        cluster_node_count = self._get_cluster_size()
        if cluster_node_count < 32:
            _output, _err, _rc = self._execute.run_cmd(const.PCS_CLUSTER_NODE_ADD.replace("<node>", nodeid))
            return {"status": "InProgress", "msg": f"Node {nodeid} add operation started successfully in the cluster"}
        else:
            return {"status": "Failed", "msg": "Cluster size is already filled to 32, "
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