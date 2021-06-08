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
from ha.core.config.config_manager import ConfigManager
from ha.core.controllers.pcs.pcs_controller import PcsController
from ha.core.error import ClusterManagerError
from ha.core.controllers.cluster_controller import ClusterController
from ha.core.controllers.controller_annotation import controller_error_handler
from ha import const
from ha.const import NODE_STATUSES
from ha.core.cluster.operation_result import OperationResult

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

    def _wait_for_node_online(self, nodeid: str) -> bool:
        """
        Wait till the node becomes online
        """
        for retry_index in range(0, const.CLUSTER_RETRY_COUNT):
            node_status = self.nodes_status([nodeid]).get(nodeid)
            if node_status == const.NODE_STATUSES.ONLINE.value:
                Log.info(f"Node {nodeid} is online.")
                return True
            # Sleep for some time and try again.
            Log.info(f"Node {nodeid} is not online, retry index #{retry_index}")
            time.sleep(const.BASE_WAIT_TIME)
        return False

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
            auth_cmd = const.PCS_CLUSTER_NODE_AUTH.replace("<node>", node_id
                ).replace("<username>", cluster_user).replace("<password>", cluster_password)
            self._execute.run_cmd(auth_cmd, secret=cluster_password)
            Log.info(f"Node {node_id} authenticated with {cluster_user} Successfully.")
        except Exception as e:
            Log.error(f"Failed to authenticate node : {node_id} with reason : {e}")
            raise ClusterManagerError(f"Failed to authenticate node : {node_id}, Please check username or password")

    def _get_node_group(self) -> list:
        """
        Get node_group
        """
        if self._is_pcs_cluster_running() is False:
            raise ClusterManagerError("Cluster is not running on current node.")
        res = json.loads(self.node_list())
        if res.get("status") != const.STATUSES.SUCCEEDED.value:
            raise ClusterManagerError("Failed to get node list.")
        else:
            node_list: list = res.get("msg")
            Log.info(f"Node List : {node_list}")
            if node_list is not None:
                node_group: list = [ node_list[i:i + const.PCS_NODE_GROUP_SIZE]
                        for i in range(0, len(node_list), const.PCS_NODE_GROUP_SIZE)]
        return node_group

    def _verify_expected_cluster_status(self, expected_status, timeout):
        """
        Verify the status of cluster is same as expected_status

        Args:
            expected_status (const.CLUSTER_STATUS): verify cluster is in this state.
            timeout (int): timeout(in seconds) wait for the status till the timeout

        Returns:
            boolean
        """
        if timeout < 0:
            timeout = const.BASE_WAIT_TIME*2

        check_interval = 2  # seconds
        loop_counter = 0
        while check_interval*loop_counter < timeout:
            result = self.status()
            result = OperationResult(result)
            if result.get_output() == expected_status.value:
                return True
            time.sleep(check_interval)
            loop_counter += 1

        return False

    @controller_error_handler
    def cluster_exists(self) -> dict:
        """
        Check if cluster exists.

        Returns:
            dict: Return dictionary. {"status": "", "msg":""}
                status: Succeeded
        """
        try:
            result: bool = True if self._is_pcs_cluster_running() else False
        except Exception as e:
            Log.error(f"Cluster status is failed. error {e}")
            result = False
        return {"status": const.STATUSES.SUCCEEDED.value, "msg": result}

    @controller_error_handler
    def start(self, sync=False, timeout=120) -> dict:
        """
        Start cluster and all service.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        # Current behavior of start, starts all the nodes and bring all the nodes out of standby.
        # This is deviation from cluster start as envisioned. So the documentation should change.

        if self._is_pcs_cluster_running() is False:
            res = self._pcs_cluster_start()
            time.sleep(const.BASE_WAIT_TIME)
            if res != const.STATUSES.SUCCEEDED.value:
                raise ClusterManagerError("Cluster start operation failed")
        status = ""
        failed_node_list: list = []
        try:
            node_group: list = self._get_node_group()
            for node_subgroup in node_group:
                for node_id in node_subgroup:
                    res = json.loads(self._controllers[const.NODE_CONTROLLER].start(node_id))
                    Log.info(f'res: {res}')
                    if res.get("status") == const.STATUSES.FAILED.value:
                        msg = res.get("msg")
                        Log.error(f"Node {node_id} : {msg}")
                        failed_node_list.append(node_id)
                # Wait till all the resources get started in the sub group
                time.sleep(const.BASE_WAIT_TIME * const.PCS_NODE_GROUP_SIZE)
        except Exception as e:
            raise ClusterManagerError(f"Failed to start Cluster. Error: {e}")
        status = "Cluster start is in process."
        if len(failed_node_list) != 0 and len(failed_node_list) != len(json.loads(self.node_list()).get("msg")):
            status += f"Warning, Some of nodes failed to start are {failed_node_list}"
        elif len(failed_node_list) != 0:
            raise ClusterManagerError(f"Failed to start all nodes {failed_node_list}")
        else:
            status += "All node started successfully, resource start in progress."

        if sync:
            timeout = timeout - const.BASE_WAIT_TIME*const.PCS_NODE_GROUP_SIZE*len(node_group)
            in_expected_state = self._verify_expected_cluster_status(const.CLUSTER_STATUS.ONLINE, timeout)
            if in_expected_state:
                return {"status": const.STATUSES.SUCCEEDED.value, "output": "Cluster is online.", "error": ""}
            else:
                return {"status": const.STATUSES.FAILED.value, "output": "Retry suggested.", "error": "Operation timed out."}

        return {"status": const.STATUSES.IN_PROGRESS.value, "output": "Cluster start operation performed", "error": ""}

    @controller_error_handler
    def stop(self) -> dict:
        """
        Stop cluster and all service. It is Blocking call.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        status: str = ""
        if not self._is_pcs_cluster_running():
            raise ClusterManagerError("Cluster not running on current node."
                        "To stop cluster, It should be running on current node.")
        node_group: list = self._get_node_group()
        local_node: str = ConfigManager.get_local_node()
        Log.info(f"Node group for cluster start {node_group}, local node {local_node}")
        self_group: list = list(filter(lambda group: (local_node in group), node_group))[0]
        node_group.remove(self_group)
        offline_nodes = self._get_filtered_nodes([NODE_STATUSES.POWEROFF.value])
        # Stop cluster for other group
        for node_subgroup in node_group:
            for nodeid in node_subgroup:
                # Offline node can not be started without stonith.
                if nodeid not in offline_nodes:
                    if self.heal_resource(nodeid):
                        time.sleep(const.BASE_WAIT_TIME)
                    res = json.loads(self._controllers[const.NODE_CONTROLLER].stop(nodeid))
                    Log.info(f"Stopping node {nodeid}, output {res}")
                    if NODE_STATUSES.POWEROFF.value in res.get("msg"):
                        offline_nodes.append(nodeid)
                        Log.warn(f"Node {nodeid}, is in offline or lost from network.")
                    elif res.get("status") == const.STATUSES.FAILED.value:
                        raise ClusterManagerError(f"Cluster Stop failed. Unable to stop {nodeid}")
                    else:
                        Log.info(f"Node {nodeid} stop is in progress.")
                else:
                    Log.info(f"Node {nodeid}, is in offline or lost from network.")
            # Wait till resource will get stop.
            Log.info(f"Waiting, for {node_subgroup} to stop is in progress.")
        # Stop self group of cluster
        try:
            Log.info(f"Please Wait, trying to stop self node group: {self_group}")
            timeout = const.NODE_STOP_TIMEOUT * len(self_group)
            self._execute.run_cmd(const.PCS_STOP_CLUSTER.replace("<seconds>", str(timeout)))
            Log.info("Cluster stop completed.")
        except Exception as e:
            raise ClusterManagerError(f"Cluster stop failed. Error: {e}")
        status = "Cluster stop is in progress."
        if len(offline_nodes) != 0:
            status += f" Warning, Found {offline_nodes}, may be poweroff or not in network"

        if sync:
            timeout = timeout - const.BASE_WAIT_TIME*const.PCS_NODE_GROUP_SIZE*len(node_group)
            in_expected_state = self._verify_expected_cluster_status(const.CLUSTER_STATUS.OFFLINE, timeout)
            if in_expected_state:
                return {"status": const.STATUSES.SUCCEEDED.value, "output": "Cluster is offline.", "error": ""}
            else:
                return {"status": const.STATUSES.FAILED.value, "output": "Retry suggested.", "error": "Operation timed out."}

        return {"status": const.STATUSES.IN_PROGRESS.value, "output": status, "error": ""}

    @controller_error_handler
    def status(self) -> dict:
        """
        Status cluster and all service. It gives status for all resources.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":{}}
                status: Succeeded, Failed, InProgress
                msg: dict of resource and status.
        """
        try:
            pcs_cluster_status = PcsClusterStatus()
            pcs_cluster_status.load()
            return pcs_cluster_status.get_cluster_health()
        except Exception as e:
            Log.error(f"Failed to get status of the cluster. Error: {e}")
            return {"status": const.STATUSES.FAILED.value, "output": "Retry Suggested.", "error" : str(e)}


    @controller_error_handler
    def standby(self) -> dict:
        """
        Put cluster in standby mode.

        Args:
            sync (bool, optional): if sync is True then stop will check the status for timeout seconds.
            timeout (int, optional): timeout(in seconds) can be specified for sync=True otherwise ignored.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        if not self._is_pcs_cluster_running():
            return {"status": const.STATUSES.FAILED.value, "output": "Node should be online.",
                    "error": "Cluster is not running on current node."}

        node_group: list = self._get_node_group()
        for node_subgroup in node_group:
            for node_id in node_subgroup:
                self._controllers[const.NODE_CONTROLLER].standby(node_id)

        if sync:
            timeout = timeout - const.BASE_WAIT_TIME*const.PCS_NODE_GROUP_SIZE*len(node_group)
            in_expected_state = self._verify_expected_cluster_status(const.CLUSTER_STATUS.STANDBY, timeout)
            if in_expected_state:
                return {"status": const.STATUSES.SUCCEEDED.value, "output": "Cluster is on standby.", "error": ""}
            else:
                return {"status": const.STATUSES.FAILED.value, "output": "Retry suggested.", "error": "Operation timed out."}

        return {"status": const.STATUSES.IN_PROGRESS.value, "output": "Operation is in progress.", "error": ""}

    @controller_error_handler
    def active(self, sync=False, timeout=90) -> dict:
        """
        Activate all node.

        Args:
            sync (bool, optional): if sync is True then stop will check the status for timeout seconds.
            timeout (int, optional): timeout(in seconds) can be specified for sync=True otherwise ignored.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        status_result = OperationResult(self.status())
        if status_result.get_output() != const.CLUSTER_STATUS.STANDBY.value:
            return {"status": const.STATUSES.FAILED.value, "output": "Operation aborted.",
                    "error": "Cluster is not in standby."}

        node_group: list = self._get_node_group()
        for node_subgroup in node_group:
            for node_id in node_subgroup:
                self._controllers[const.NODE_CONTROLLER].active(node_id)

        if sync:
            timeout = timeout - const.BASE_WAIT_TIME*const.PCS_NODE_GROUP_SIZE*len(node_group)
            in_expected_state = self._verify_expected_cluster_status(const.CLUSTER_STATUS.ONLINE, timeout)
            if in_expected_state:
                return {"status": const.STATUSES.SUCCEEDED.value, "output": "Cluster is online.", "error": ""}
            else:
                return {"status": const.STATUSES.FAILED.value, "output": "Retry suggested.",
                        "error": "Operation timed out."}

        return {"status": const.STATUSES.IN_PROGRESS.value, "output": "Operation is in progress.", "error": ""}

    @controller_error_handler
    def node_list(self) -> dict:
        """
        Provide node list.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":[]}
                status: Succeeded, Failed, InProgress
        """
        nodelist: list = self._get_node_list()
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
            if self._wait_for_node_online(nodeid):
                return {"status": const.STATUSES.SUCCEEDED.value, "output": f"Node {nodeid} added successfully in the cluster", "error": ""}
            else:
                return {"status": const.STATUSES.FAILED.value, "output": "", "error": f"Node {nodeid} add operation failed, node not online"}
        else:
            return {"status": const.STATUSES.FAILED.value, "output": "", "error": "Cluster size is already filled to 32, "
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
                                        .replace("<node>", nodeid))
                Log.info("Pacmaker cluster created, waiting to start node.")
                self._execute.run_cmd(const.PCS_CLUSTER_START_NODE)
                self._execute.run_cmd(const.PCS_CLUSTER_ENABLE)
                Log.info("Node started and enabled successfully.")
                time.sleep(const.BASE_WAIT_TIME * 2)
            if self._is_pcs_cluster_running():
                if self._wait_for_node_online(nodeid):
                    # TODO: Divide class into vm, hw when stonith is needed.
                    self._execute.run_cmd(const.PCS_STONITH_DISABLE)
                    return {"status": const.STATUSES.SUCCEEDED.value,
                            "output": "Cluster created successfully.", "error": ""}
                else:
                    raise ClusterManagerError("Node is not online.")
            else:
                raise ClusterManagerError("Cluster is not started.")
        except Exception as e:
            raise ClusterManagerError(f"Failed to create cluster. Error: {e}")
