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

import grp
import os
import time
import ast
import uuid
import getpass
import xml.etree.ElementTree as ET

from cortx.utils.log import Log
from ha.core.error import HAInvalidPermission, HAUnimplemented, ClusterManagerError
from ha.core.controllers.pcs.pcs_controller import PcsController
from ha.core.controllers.node_controller import NodeController
from ha.core.controllers.controller_annotation import controller_error_handler
from ha import const
from ha.const import NODE_STATUSES
from ha.core.system_health.const import NODE_MAP_ATTRIBUTES, CLUSTER_ELEMENTS, HEALTH_EVENTS, EVENT_SEVERITIES, HEALTH_STATUSES
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.system_health import SystemHealth, SystemHealthManager
from ha.core.config.config_manager import ConfigManager
from ha.util.ipmi_fencing_agent import IpmiFencingAgent
from ha.core.controllers.pcs.service_controller import PcsServiceController

class PcsNodeController(NodeController, PcsController):
    """ Controller to manage node. """

    def __init__(self):
        """
        Initalize PcsNodeController
        """
        super(PcsNodeController, self).__init__()
        self._confstore = ConfigManager.get_confstore()
        self._system_health = SystemHealth(self._confstore)
        self._health_manager = SystemHealthManager(self._confstore)
        self._service_controller = PcsServiceController()

    def initialize(self, controllers):
        """
        Initialize the node controller
        """
        raise HAUnimplemented("This operation is not implemented.")

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
    def stop(self, node_id: str, timeout: int, **op_kwargs) -> dict:
        """
        Stop Cluster on node with nodeid.
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
        status: str = ""
        # Check node status
        node_status = self.nodes_status([nodeid]).get(nodeid)
        Log.info(f"Current {nodeid} status is {node_status}")
        if node_status == NODE_STATUSES.STANDBY.value:
            status = f"Node {nodeid} is already running in standby mode."
        elif node_status != NODE_STATUSES.ONLINE.value:
            return {"status": const.STATUSES.FAILED.value,
                    "msg": f"Failed to put node in standby as node is in {node_status}"}
        else:
            if self.heal_resource(nodeid):
                time.sleep(const.BASE_WAIT_TIME)
            self._execute.run_cmd(const.PCS_NODE_STANDBY.replace("<node>", nodeid))
            Log.info(f"Waiting to standby {nodeid} node.")
            time.sleep(const.BASE_WAIT_TIME * 2)
            node_status = self.nodes_status([nodeid]).get(nodeid)
            Log.info(f"After standby, current {nodeid} status is {node_status}")
            status = f"Waiting for resource to stop, {nodeid} standby is in progress"
        return {"status": const.STATUSES.IN_PROGRESS.value, "msg": status}

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
        raise HAUnimplemented("This operation is not implemented.")

    def _validate_permissions(self) -> None:

        # confirm that user is root or part of haclient group"
        user = getpass.getuser()
        group_id = os.getgid()

        try:
            # find group id for root and haclient
            id_ha = grp.getgrnam(const.USER_GROUP_HACLIENT)
            id_root = grp.getgrnam(const.USER_GROUP_ROOT)

            # if group not root or haclient return error
            if group_id != id_ha.gr_gid and group_id != id_root.gr_gid:
                Log.error(f"User {user} does not have necessary permissions to execute this CLI")
                raise HAInvalidPermission(
                            f"User {user} does not have necessary permissions to execute this CLI")

            # The user name "hauser"; which is part of the "haclient" group;
            # is used by HA.
            # internal commands are allowed only if the user is "hauser"
            # As of now, every HA CLI will be internal command. So, we
            # do not need this change. We can revisit this if needed in future
            #if user == const.USER_HA_INTERNAL:
            #    self._is_hauser = True


        # TBD : If required raise seperate exception  for root and haclient
        except KeyError:
            Log.error("Group root / haclient is not defined")
            raise HAInvalidPermission("Group root / haclient is not defined ")

    def check_cluster_feasibility(self, nodeid: str) -> dict:
        """
            Check whether the cluster is going to be offline after node with nodeid is stopped.
        Args:
            nodeid (str): Private fqdn define in conf store.
        Returns:
            Dictionary : {"status": "", "msg":""}
        """
        self.validate_node(node_id=nodeid)
        offline_nodes, node_list = self._get_offline_nodes()
        if (len(offline_nodes) + 1) >= ((len(node_list)//2) + 1):
            return {"status": const.STATUSES.FAILED.value, "error": "Stopping the node will cause a loss of the quorum"}
        else:
            return {"status": const.STATUSES.SUCCEEDED.value, "error": ""}

    def validate_node(self, node_id: str) -> bool:
        """
        Check node is a part of cluster
        Args:
            node_id ([str]): Private fqdn define in conf store.
        Raises: ClusterManagerError
        Returns: bool
        """
        _, node_list = self._get_offline_nodes()
        if node_id in node_list:
            return True
        raise ClusterManagerError(f"nodeid = {node_id} is not a valid node id")

    def _get_offline_nodes(self):
        """
        Get list of offline nodes ids.
        """
        cluster_status_xml = self._execute.run_cmd(const.GET_CLUSTER_STATUS)
        # create element tree object
        root = ET.fromstring(cluster_status_xml[0])
        node_list = []
        nodes_ids = []
        # iterate news items
        for item in root.findall('nodes'):
            # iterate child elements of item
            for child in item:
                if child.attrib['online'] == 'false':
                    nodes_ids.append(child.attrib['id'])
                node_list.append(child.attrib['name'])
        Log.info(f"List of offline node ids in cluster in sorted ascending order: {sorted(nodes_ids)}")
        return sorted(nodes_ids), node_list

    def create_health_event(self, nodeid: str, event_type: str) -> dict:
        """
        Create health event
        Args:
            nodeid (str): nodeid
            event_type (str): event type will be offline, online, failed

        Returns:
            dict: Return dictionary of health event
        """
        key = self._system_health._prepare_key(const.COMPONENTS.NODE_MAP.value, node_id=nodeid)
        node_map_val = self._health_manager.get_key(key)
        if node_map_val is None:
            raise ClusterManagerError("Failed to fetch node_map value")
        node_map_dict = ast.literal_eval(node_map_val)

        timestamp = str(int(time.time()))
        event_id = timestamp + str(uuid.uuid4().hex)
        initial_event = {
            const.EVENT_ATTRIBUTES.EVENT_ID : event_id,
            const.EVENT_ATTRIBUTES.EVENT_TYPE : event_type,
            const.EVENT_ATTRIBUTES.SEVERITY : EVENT_SEVERITIES.WARNING.value,
            const.EVENT_ATTRIBUTES.SITE_ID : node_map_dict[NODE_MAP_ATTRIBUTES.SITE_ID.value],
            const.EVENT_ATTRIBUTES.RACK_ID : node_map_dict[NODE_MAP_ATTRIBUTES.RACK_ID.value],
            const.EVENT_ATTRIBUTES.CLUSTER_ID : node_map_dict[NODE_MAP_ATTRIBUTES.CLUSTER_ID.value],
            const.EVENT_ATTRIBUTES.STORAGESET_ID : node_map_dict[NODE_MAP_ATTRIBUTES.STORAGESET_ID.value],
            const.EVENT_ATTRIBUTES.NODE_ID : nodeid,
            const.EVENT_ATTRIBUTES.HOST_ID : node_map_dict[NODE_MAP_ATTRIBUTES.HOST_ID.value],
            const.EVENT_ATTRIBUTES.RESOURCE_TYPE : CLUSTER_ELEMENTS.NODE.value,
            const.EVENT_ATTRIBUTES.TIMESTAMP : timestamp,
            const.EVENT_ATTRIBUTES.RESOURCE_ID : nodeid,
            const.EVENT_ATTRIBUTES.SPECIFIC_INFO : None
        }
        return initial_event

class PcsVMNodeController(PcsNodeController):
    def initialize(self, controllers):
        """
        Initialize the node controller
        """
        self._controllers = controllers

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
        _node_status = self.nodes_status([nodeid])[nodeid]
        if _node_status == NODE_STATUSES.ONLINE.value:
            return {"status": const.STATUSES.SUCCEEDED.value, "msg": f"Node {nodeid}, is already in Online status"}
        elif _node_status == NODE_STATUSES.STANDBY.value or _node_status == NODE_STATUSES.STANDBY_WITH_RESOURCES_RUNNING.value:
            # make node unstandby
            if self.heal_resource(nodeid):
                _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_UNSTANDBY.replace("<node>", nodeid),
                                                           check_error=False)
                return {"status": const.STATUSES.IN_PROGRESS.value, "msg": f"Node {nodeid} : Node was in standby mode, "
                                                       f"Unstandby operation started successfully"}
            else:
                Log.error(f"Node {nodeid} is in standby mode : Resource failcount found on the node, "
                          f"cleanup not worked after 2 retries")
                return {"status": const.STATUSES.FAILED.value, "msg": f"Node {nodeid} is in standby mode: Resource "
                                                   f"failcount found on the node cleanup not worked after 2 retries"}
        elif _node_status == NODE_STATUSES.CLUSTER_OFFLINE.value:
            _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_START.replace("<node>", nodeid), check_error=False)
            if _rc != 0:
                raise ClusterManagerError(f"Failed to start node {nodeid}")

            Log.info(f'Node: {nodeid} started successfully. Now, waiting for \
                       cluster to stabalize and then get the node status')

            time.sleep(const.BASE_WAIT_TIME * 2)

            # Get the status of the node again
            _node_status = self.nodes_status([nodeid])[nodeid]

            # If the node is in standby mode, unstandby here
            if _node_status == NODE_STATUSES.STANDBY.value:
                Log.warn(f'Node: {nodeid} is still in standby mode')
                _output, _err, _rc = self._execute.run_cmd(const.PCS_NODE_UNSTANDBY.replace("<node>", nodeid),
                                                           check_error=False)
                if _rc != 0:
                    raise ClusterManagerError(f"Failed to unstandby the node: {nodeid}")
                return {"status": const.STATUSES.IN_PROGRESS.value, "msg": f"Node {nodeid}: Node was in offline and then switched to standby mode, " f"Cluster started on node successfully"}

            return {"status": const.STATUSES.IN_PROGRESS.value, "msg": f"Node {nodeid} : Node was in cluster_offline mode, "
                                                       f"Cluster started on node successfully"}

        elif _node_status == NODE_STATUSES.POWEROFF.value:
            # start node not in scope of VM
            Log.error("Operation not available for node type VM")
            raise ClusterManagerError(f"Node {nodeid} : Node was in poweroff mode, "
                                      "Node start : Operation not available for VM")
        else:
            Log.error(f"{nodeid} status is {_node_status}, node may not be started.")
            raise ClusterManagerError(f"Failed to start {nodeid} as found unhandled status {_node_status}")

    @controller_error_handler
    def stop(self, node_id: str, timeout: int= -1, **op_kwargs) -> dict:
        timeout = const.NODE_STOP_TIMEOUT if timeout < 0 else timeout
        node_status = self.nodes_status([node_id]).get(node_id)
        if node_status == NODE_STATUSES.CLUSTER_OFFLINE.value:
            Log.info(f"For stop {node_id}, Node already in offline state.")
            status = f"Node {node_id} is already in offline state."
        elif node_status == NODE_STATUSES.POWEROFF.value:
            raise ClusterManagerError(f"Failed to stop {node_id}."
                f"node is in {node_status}.")
        else:
            if self.heal_resource(node_id):
                time.sleep(const.BASE_WAIT_TIME)
            try:
                Log.info(f"Please Wait, trying to stop node: {node_id}")
                self._execute.run_cmd(const.PCS_STOP_NODE.replace("<node>", node_id)
                        .replace("<seconds>", str(timeout)))
                Log.info(f"Executed node stop for {node_id}, Waiting to stop resource")
                time.sleep(const.BASE_WAIT_TIME)
                status = f"Stop for {node_id} is in progress, waiting to stop resource"
            except Exception as e:
                raise ClusterManagerError(f"Failed to stop {node_id}, Error: {e}")
        return {"status": const.STATUSES.IN_PROGRESS.value, "output": status, "error": ""}

class PcsHWNodeController(PcsNodeController):
    def initialize(self, controllers):
        """
        Initialize the storageset controller
        """
        self._controllers = controllers
        self.ipmifenceagent = IpmiFencingAgent()

    @controller_error_handler
    def shutdown(self, nodeid: str) -> dict:
        """
        Shutdown node with nodeid.
        Args:
            nodeid (str): Node ID from cluster nodes.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def stop(self, node_id: str, timeout: int = -1, **op_kwargs) -> dict:
        """
        Stop Cluster on node with node_id.
        Args:
            node_id (str): Private fqdn define in conf store.
        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        check_cluster = op_kwargs.get("check_cluster") if op_kwargs.get("check_cluster") is not None else True
        poweroff = op_kwargs.get("poweroff") if op_kwargs.get("poweroff") is not None else False
        storageoff = op_kwargs.get("storageoff") if op_kwargs.get("storageoff") is not None else False
        try:
            # Raise exception if user does not have proper permissions
            self._validate_permissions()
            # Raise exception if node_id is not valid
            self.validate_node(node_id=node_id)

            # Get the nodeid from pvtfqdn
            nodeid = self._health_manager.get_key(f"{const.PVTFQDN_TO_NODEID_KEY}/{node_id}")

            # stop all services running on node with node_id
            node_status = self._system_health.get_node_status(node_id=nodeid).get("status")
            if node_status == HEALTH_STATUSES.OFFLINE.value:
                Log.info(f"For stop {node_id}, Node already in offline state.")
                status = f"Node {node_id} is already in offline state."
                return {"status": const.STATUSES.SUCCEEDED.value, "output": node_status, "error": "", "msg": status}
            elif node_status == HEALTH_STATUSES.FAILED.value:
                raise ClusterManagerError(f"Failed to stop {node_id}."
                                          f"node is in {node_status} state.")
            else:
                if check_cluster:
                    # Checks whether cluster is going to be offline if node with node_id is stopped.
                    res = self.check_cluster_feasibility(nodeid=node_id)
                    if res.get("status") == const.STATUSES.FAILED.value:
                        return res
                if self.heal_resource(node_id):
                    time.sleep(const.BASE_WAIT_TIME)

            if storageoff:
                # Stop services on node except sspl-ll
                self._service_controller.stop(nodeid=node_id, excludeResourceList=["sspl-ll"])

                # TODO: storage enclosure is stopped on the node

                # Put node in standby mode
                self._execute.run_cmd(const.PCS_NODE_STANDBY.replace("<node>", node_id), f" --wait={const.CLUSTER_STANDBY_UNSTANDBY_TIMEOUT}")
                Log.info(f"Executed node standby for {node_id}")
                self._service_controller.clear_resources(node_id=node_id)
            else:
                self._execute.run_cmd(const.PCS_NODE_STANDBY.replace("<node>", node_id), f" --wait={const.CLUSTER_STANDBY_UNSTANDBY_TIMEOUT}")
                Log.info(f"Executed node standby for {node_id}")
            status = f"{node_id} Node Standby is in progress"

            # Update node health
            initial_event = self.create_health_event(nodeid=nodeid, event_type=HEALTH_EVENTS.FAULT.value)
            Log.debug(f"Node health : {initial_event} updated for node {nodeid}")
            health_event = HealthEvent.dict_to_object(initial_event)
            self._system_health.process_event(health_event)

            # Node power off
            if poweroff:
                self.ipmifenceagent.power_off(nodeid=node_id)
                status = f"Power off for {node_id} is in progress"
            Log.info("Node power off successfull")
            return {"status": const.STATUSES.IN_PROGRESS.value, "error": "", "output": HEALTH_STATUSES.OFFLINE.value, "msg": status}
        except Exception as e:
            raise ClusterManagerError(f"Failed to stop {node_id}, Error: {e}")
