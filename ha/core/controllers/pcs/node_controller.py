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
from ha.core.error import HAUnimplemented, ClusterManagerError
from ha.core.controllers.pcs.pcs_controller import PcsController
from ha.core.controllers.node_controller import NodeController
from ha.core.controllers.controller_annotation import controller_error_handler
from ha import const
from ha.const import NODE_STATUSES
from ha.core.system_health.const import HEALTH_EVENTS, HEALTH_STATUSES
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.system_health import SystemHealth
from ha.core.config.config_manager import ConfigManager
from ha.util.ipmi_fencing_agent import IpmiFencingAgent
from ha.setup.const import RESOURCE

class PcsNodeController(NodeController, PcsController):
    """ Controller to manage node. """

    def __init__(self):
        """
        Initalize PcsNodeController
        """
        super(PcsNodeController, self).__init__()
        self._confstore = ConfigManager.get_confstore()
        self._system_health = SystemHealth(self._confstore)

    def initialize(self, controllers):
        """
        Initialize the node controller
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def start(self, node_id: str, **op_kwargs) -> dict:
        """
        Start node with the node_id.
        Args:
            node_id (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "output": "", "error": ""}
                status: Succeeded, Failed, InProgress
        """
        try:
            # Get the node_name (pvtfqdn) from node_id
            node_name = self._get_node_name(node_id=node_id)
            self._is_node_in_cluster(node_id=node_name)
            # TODO: Check status from system health instead of pcs below.
            node_status = self.nodes_status([node_name])[node_name]
            Log.debug(f"Node {node_name} status is {node_status}")
            if node_status == NODE_STATUSES.ONLINE.value:
                Log.debug(f"Node {node_name} is already online")
                return {"status": const.STATUSES.SUCCEEDED.value, "output": NODE_STATUSES.ONLINE.value, "error": ""}
            elif node_status == NODE_STATUSES.STANDBY.value or node_status == NODE_STATUSES.STANDBY_WITH_RESOURCES_RUNNING.value:
                # Unstandby the node
                if self.heal_resource(node_name):
                    _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_UNSTANDBY.replace("<node>", node_name), check_error=False)
                    if _rc != 0:
                        Log.error(f"Failed to start node {node_name}, Error: {_err}")
                        return {"status": const.STATUSES.FAILED.value, "output": "", "error": f"Failed to start node {node_id}, Error: {_err}"}
                    Log.debug(f"Node {node_name} was in standby mode, unstandby operation started successfully")
                else:
                    Log.error(f"Node {node_name} is in standby mode : Resource failcount found on the node, cleanup did not work")
                    return {"status": const.STATUSES.FAILED.value, "output": "", "error": f"Node {node_id} is in standby mode, resource failcount found on the node, cleanup did not work"}
            elif node_status == NODE_STATUSES.CLUSTER_OFFLINE.value:
                _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_START.replace("<node>", node_name), check_error=False)
                if _rc != 0:
                    Log.error(f"Failed to start node {node_name}, Error: {_err}")
                    return {"status": const.STATUSES.FAILED.value, "output": "", "error": f"Failed to start node {node_id}, Error: {_err}"}
                Log.debug(f"Node {node_name} started successfully. Waiting for cluster to stabalize and then get the node status")
                time.sleep(const.BASE_WAIT_TIME * 2)
                # Get the status of the node again
                node_status = self.nodes_status([node_name])[node_name]
                # If the node is in standby mode, unstandby here
                if node_status == NODE_STATUSES.STANDBY.value:
                    Log.warn(f'Node {node_name} is still in standby mode')
                    _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_UNSTANDBY.replace("<node>", node_name), check_error=False)
                    if _rc != 0:
                        Log.error(f"Failed to start node {node_name}, Error: {_err}")
                        return {"status": const.STATUSES.FAILED.value, "output": "", "error": f"Failed to start node {node_id}, Error: {_err}"}
            else:
                Log.error(f"{node_name} status is {node_status}, node cannot be started.")
                return {"status": const.STATUSES.FAILED.value, "output": "", "error": f"Node {node_id} status is {node_status}, node cannot be started."}

            # Update the node status in system health
            event_template = self._system_health.get_health_event_template(nodeid=node_id, event_type=HEALTH_EVENTS.FAULT_RESOLVED.value)
            health_event = HealthEvent.dict_to_object(event_template)
            self._system_health.process_event(health_event)
            Log.debug(f"Node health: {event_template} updated for node {node_id}")
            return {"status": const.STATUSES.SUCCEEDED.value, "output": NODE_STATUSES.ONLINE.value, "error": ""}
        except Exception as e:
            Log.error(f"Failed to start node {node_id}")
            raise ClusterManagerError(f"Failed to start node {node_id}, Error {e}")

    @controller_error_handler
    def stop(self, node_id: str, timeout: int, **op_kwargs) -> dict:
        """
        Stop Node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "output": "", "error": ""}
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
            ([dict]): Return dictionary. {"status": "", "output": "", "error": ""}
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
            ([dict]): Return dictionary. {"status": "", "output": "", "error": ""}
                status: Succeeded, Failed, InProgress
        """
        status: str = ""
        # Check node status
        node_status = self.nodes_status([nodeid]).get(nodeid)
        Log.info(f"Current {nodeid} status is {node_status}")
        if node_status == NODE_STATUSES.STANDBY.value:
            return {"status": const.STATUSES.SUCCEEDED.value, "output":
                f"Node {nodeid} is already running in standby mode.", "error": ""}
        elif node_status == NODE_STATUSES.STANDBY_WITH_RESOURCES_RUNNING.value:
            return {"status": const.STATUSES.IN_PROGRESS.value, "output":
                f"Node {nodeid} is in standby with resource running mode.", "error": ""}
        elif node_status != NODE_STATUSES.ONLINE.value:
            return {"status": const.STATUSES.FAILED.value, "output": "",
                    "error": f"Failed to put node in standby as node is in {node_status}"}
        else:
            if self.heal_resource(nodeid):
                time.sleep(const.BASE_WAIT_TIME)
            self._execute.run_cmd(const.PCS_NODE_STANDBY.replace("<node>", nodeid))
            Log.info(f"Waiting to standby {nodeid} node.")
            time.sleep(const.BASE_WAIT_TIME * 2)
            node_status = self.nodes_status([nodeid]).get(nodeid)
            Log.info(f"After standby, current {nodeid} status is {node_status}")

        status = f"Waiting for resource to stop, {nodeid} standby is in progress"
        return {"status": const.STATUSES.IN_PROGRESS.value, "output": status, "error": ""}

    @controller_error_handler
    def active(self, nodeid: str) -> dict:
        """
        Activate node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "output": "", "error": ""}
                status: Succeeded, Failed, InProgress
        """
        # TODO: Future: Check if cluster is online on the current node. Current code will work for cluster active operation.
        self._is_node_in_cluster(node_id=nodeid)
        node_status = self.nodes_status([nodeid]).get(nodeid)
        Log.info(f"Current {nodeid} status is {node_status}")
        if node_status != NODE_STATUSES.STANDBY.value:
            return {"status": const.STATUSES.FAILED.value, "output": "Node is not in standby.",
                    "error": f"Current state = {node_status}"}

        self._execute.run_cmd(const.PCS_NODE_UNSTANDBY.replace("<node>", nodeid))
        Log.info(f"Waiting  for node to become active. Node = {nodeid}.")
        time.sleep(const.BASE_WAIT_TIME)

        node_status = self.nodes_status([nodeid]).get(nodeid)
        Log.info(f"Current {nodeid} status is {node_status}")
        if node_status == NODE_STATUSES.STANDBY.value:
            status = const.STATUSES.SUCCEEDED.value
        else:
            status = const.STATUSES.FAILED.value
        return {"status": status, "output": node_status, "error": ""}

    @controller_error_handler
    def status(self, nodeids: list = None) -> dict:
        """
        Get status of nodes.
        Args:
            nodeids (list): List of Node IDs from cluster nodes.
                Default provide list of all node status.
                if 'local' then provide local node status.
        Returns:
            ([dict]): Return dictionary. {"status": "", "output": "", "error": ""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def check_cluster_feasibility(self, node_id: str) -> dict:
        """
            Check whether the cluster is going to be offline after node with node_id is stopped.
        Args:
            node_id (str): Node ID from cluster nodes.
        Returns:
            Dictionary : {"status": "", "msg":""}
        """
        # Get the node_name (pvtfqdn) fron nodeid
        node_name = self._get_node_name(node_id=node_id)
        # Raise exception if node_name is not valid
        self._is_node_in_cluster(node_id=node_name)
        node_list = self._get_node_list()
        offline_nodes = self._get_offline_nodes()
        Log.debug(f"nodelist : {node_list} offlinenodes : {offline_nodes}")
        num_nodes = len(node_list)
        max_nodes_offline = num_nodes // 2 if num_nodes % 2 == 1 else (num_nodes // 2) - 1
        if (len(offline_nodes) + 1) > max_nodes_offline:
            Log.debug("Stopping the node will cause a loss of the quorum")
            return {"status": const.STATUSES.FAILED.value, "output": "", "error": "Stopping the node will cause a loss of the quorum"}
        else:
            Log.debug("Stopping the node will not cause a loss of the quorum")
            return {"status": const.STATUSES.SUCCEEDED.value, "output": "", "error": ""}

    def _get_offline_nodes(self):
        """
        Get the list offline, standby, failed nodes
        Returns:
            [list]: list of offline & failed nodes
        """
        nodes_status = self.nodes_status()
        offline_nodes = []
        for node_name in self._get_node_list():
            if nodes_status[node_name] != HEALTH_STATUSES.ONLINE.value:
                offline_nodes.append(node_name)
        return offline_nodes


class PcsVMNodeController(PcsNodeController):
    def initialize(self, controllers):
        """
        Initialize the node controller
        """
        self._controllers = controllers

    @controller_error_handler
    def start(self, node_id: str, **op_kwargs) -> dict:
        """
        Start node with the node_id.
        Args:
            node_id (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "output": "", "error": ""}
                status: Succeeded, Failed, InProgress
        """
        return super().start(node_id, **op_kwargs)

    @controller_error_handler
    def stop(self, node_id: str, timeout: int= -1, **op_kwargs) -> dict:
        """
        Stop Node with nodeid.
        Args:
            node_id (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "output": "", "error": ""}
                status: Succeeded, Failed, InProgress
        """
        # Get the node_name (pvtfqdn) fron nodeid
        node_name = self._get_node_name(node_id=node_id)
        # TODO: check_cluster - boolean.It checks whether cluster is going to be offline if node with node_id is stopped.
        timeout = const.NODE_STOP_TIMEOUT if timeout < 0 else timeout
        # TODO: Get the node_status from system health status
        node_status = self.nodes_status([node_name]).get(node_name)
        if node_status == NODE_STATUSES.CLUSTER_OFFLINE.value:
            Log.info(f"For stop {node_name}, Node already in offline state.")
            status = f"Node {node_name} is already in offline state."
        elif node_status == NODE_STATUSES.POWEROFF.value:
            raise ClusterManagerError(f"Failed to stop {node_name}. Node is in {node_status}.")
        else:
            if self.heal_resource(node_name):
                time.sleep(const.BASE_WAIT_TIME)
            try:
                Log.info(f"Please Wait, trying to stop node: {node_name}")
                # TODO: Use PCS_STOP_NODE from const.py with timeout value
                self._execute.run_cmd(f"pcs cluster stop {node_name}")
                Log.info(f"Executed node stop for {node_name}, Waiting to stop resource")
                time.sleep(const.BASE_WAIT_TIME)
                status = f"Stop for {node_name} is in progress, waiting to stop resource"
                # TODO: Update node_status in system_health
            except Exception as e:
                raise ClusterManagerError(f"Failed to stop {node_name}, Error: {e}")
        return {"status": const.STATUSES.SUCCEEDED.value, "output": status, "error": ""}

class PcsHWNodeController(PcsNodeController):
    def initialize(self, controllers):
        """
        Initialize the storageset controller
        """
        self._controllers = controllers
        self.fencing_agent = IpmiFencingAgent()

    def start(self, node_id: str, **op_kwargs) -> dict:
        """
        Start node with the node_id.
        Args:
            node_id (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "output": "", "error": ""}
                status: Succeeded, Failed, InProgress
        """
        try:
            poweron = op_kwargs.get("poweron") if op_kwargs.get("poweron") is not None else False
            node_name = self._get_node_name(node_id=node_id)
            self._is_node_in_cluster(node_id=node_name)
            power_status = self.fencing_agent.power_status(node_id=node_name)
            if power_status == const.BMC_POWER_STATUS.OFF.value and poweron is False:
                Log.debug(f"Node {node_name} is powered-off and poweron was not set")
                return {"status": const.STATUSES.FAILED.value, "output": "", "error": f"Node {node_id} is powered-off, use poweron option"}
            elif power_status == const.BMC_POWER_STATUS.OFF.value and poweron is True:
                self.fencing_agent.power_on(node_id=node_name)
                Log.debug(f"Node {node_name} is powered-on, waiting for node boot")
                time.sleep(const.NODE_POWERON_DELAY)
            start_status =  super().start(node_id, **op_kwargs)
            # TODO: Move this to base class after during stop stonith is disabled for VM as well.
            start_status = json.loads(start_status)
            if start_status["status"] == const.STATUSES.SUCCEEDED.value:
                self._execute.run_cmd(const.ENABLE_STONITH.replace("<node>", node_name))
            return start_status
        except Exception as e:
            raise ClusterManagerError(f"Failed to start {node_id}, Error: {e}")

    @controller_error_handler
    def shutdown(self, nodeid: str) -> dict:
        """
        Shutdown node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "output": "", "error": ""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def stop(self, node_id: str, timeout: int = -1, **op_kwargs) -> dict:
        """
        Stop (poweroff) node with node_id.
        Args:
            node_id (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        check_cluster = op_kwargs.get("check_cluster") if op_kwargs.get("check_cluster") is not None else True
        poweroff = op_kwargs.get("poweroff") if op_kwargs.get("poweroff") is not None else False
        storageoff = op_kwargs.get("storageoff") if op_kwargs.get("storageoff") is not None else False
        try:

            # Get the node_name (pvtfqdn) fron nodeid
            node_name = self._get_node_name(node_id=node_id)
            # Raise exception if node_id is not valid
            self._is_node_in_cluster(node_id=node_name)

            # stop all services running on node with node_id
            node_status = self._system_health.get_node_status(node_id=node_id).get("status")
            if node_status == HEALTH_STATUSES.OFFLINE.value:
                Log.info(f"For stop {node_name}, Node already in offline state.")
                status = f"Node {node_name} is already in offline state."
                return {"status": const.STATUSES.SUCCEEDED.value, "output": status, "error": ""}
            elif node_status == HEALTH_STATUSES.FAILED.value:
                raise ClusterManagerError(f"Failed to stop {node_name}. node is in {node_status} state.")
            else:
                if check_cluster:
                    # Checks whether cluster is going to be offline if node with node_name is stopped.
                    res = json.loads(self.check_cluster_feasibility(node_id=node_id))
                    if res.get("status") == const.STATUSES.FAILED.value:
                        return res
                if self.heal_resource(node_name):
                    time.sleep(const.BASE_WAIT_TIME)

            if storageoff:
                # Stop services on node except sspl-ll
                self._controllers[const.SERVICE_CONTROLLER].stop(node_id=node_name, excludeResourceList=[RESOURCE.SSPL_LL.value])

                # TODO: storage enclosure is stopped on the node

                # Put node in standby mode
                self._execute.run_cmd(const.PCS_NODE_STANDBY.replace("<node>", node_name), f" --wait={const.CLUSTER_STANDBY_UNSTANDBY_TIMEOUT}")
                Log.info(f"Executed node standby for {node_name}")
                self._controllers[const.SERVICE_CONTROLLER].clear_resources(node_id=node_name)
            else:
                self._execute.run_cmd(const.PCS_NODE_STANDBY.replace("<node>", node_name), f" --wait={const.CLUSTER_STANDBY_UNSTANDBY_TIMEOUT}")
                Log.info(f"Executed node standby for {node_name}")
            status = f"{node_name} Node Standby is in progress"

            # Update node health
            # TODO : Health event update to be removed once fault_tolerance branch is merged
            initial_event = self._system_health.get_health_event_template(nodeid=node_id, event_type=HEALTH_EVENTS.FAULT.value)
            Log.debug(f"Node health : {initial_event} updated for node {node_name}")
            health_event = HealthEvent.dict_to_object(initial_event)
            self._system_health.process_event(health_event)

            # Node power off
            if poweroff:
                self._execute.run_cmd(const.DISABLE_STONITH.replace("<node>", node_name))
                self.fencing_agent.power_off(node_id=node_name)
                status = f"Power off for {node_name} is in progress"
            Log.info(f"Node power off successfull. status : {status}")
            # TODO : return status should be changed according to passed parameters
            return {"status": const.STATUSES.SUCCEEDED.value, "error": "", "output": status}
        except Exception as e:
            raise ClusterManagerError(f"Failed to stop {node_name}, Error: {e}")