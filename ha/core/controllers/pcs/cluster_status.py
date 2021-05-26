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
from ha import const
from ha.core.config.config_manager import ConfigManager
from ha.execute import SimpleCommand
from ha.const import CLUSTER_STATUS

from cortx.utils.log import Log

from xml.etree import ElementTree

from ha.remote_execution.ssh_communicator import SSHRemoteExecutor


class PcsConstants:
    PCS_STATUS_XML = "pcs status --full xml"
    NAME = "name"
    ONLINE = "online"
    STANDBY = "standby"
    STANDBY_ON_FAIL = "standby_onfail"
    MAINTENANCE = "maintenance"
    PENDING = "pending"
    UNCLEAN = "unclean"
    SHUTDOWN = "shutdown"
    ROLE = "role"
    ACTIVE = "active"
    ORPHANED = "orphaned"
    BLOCKED = "blocked"
    FAILED = "failed"
    COUNT = "count"
    UNHEALTHY = "unhealthy"
    FALSE = "false"
    TRUE = "true"
    ID = "id"
    STARTED = "Started"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class PcsClusterStatus:
    """
        Status of the cluster
        This is temporary code. This information will finally come from system health.
    """

    def __init__(self):
        self._nodes_configured = []
        self._nodes = {}
        self._services = {}
        self._output = None

        # Read list of nodes from HA Conf store
        confstore = ConfigManager._get_confstore()
        nodelist = confstore.get(const.CLUSTER_CONFSTORE_NODES_KEY)

        if nodelist is not None:
            Log.info(f"Number of nodes configured = {len(nodelist)}")
            for a_node in nodelist:
                self._nodes_configured.append(a_node.split('/')[-1])

    def _get_pcs_status(self):
        """
            Get status of the cluster using "pcs status --full xml" command.
        """
        self._nodes[PcsConstants.OFFLINE] = []
        self._nodes[PcsConstants.COUNT] = 0

        error = None
        try:
            self._output, error, rc = SimpleCommand().run_cmd(PcsConstants.PCS_STATUS_XML)
        except Exception:
            Log.info("Failed to run pcs status on current node.")
            rc = 1
        Log.info(f"pcs status : rc = {rc}, error = {error}")

        if rc != 0:
            self._output = self._get_pcs_status_remote()

        if self._output is not None:
            self._output = ElementTree.fromstring(self._output)

    def _get_pcs_status_remote(self):
        """
            Get status of the cluster using "pcs status --full xml" command remotely.
        """
        for remote_node in self._nodes_configured:
            res = None
            remote_executor = SSHRemoteExecutor(remote_node)
            try:
                res = remote_executor.execute(PcsConstants.PCS_STATUS_XML)
                self._nodes[PcsConstants.OFFLINE] = []
            except Exception as e:
                Log.info(f"Failed to run pcs status on node: {remote_node}")
                self._nodes[PcsConstants.OFFLINE].append(remote_node)
            else:
                return res

    def _load_nodes_health(self):
        """
            Read xml output and load online, standby and unhealthy nodes.
        """
        self._nodes[PcsConstants.ONLINE] = []
        self._nodes[PcsConstants.STANDBY] = []
        self._nodes[PcsConstants.UNHEALTHY] = []

        if self._output is None:
            return

        node_path = "./nodes/node"
        nodes = self._output.findall(node_path)
        self._nodes[PcsConstants.COUNT] = len(nodes)

        for a_node in nodes:
            node_name = a_node.attrib[PcsConstants.NAME]
            if a_node.attrib[PcsConstants.ONLINE] == PcsConstants.FALSE:
                self._nodes[PcsConstants.OFFLINE].append(node_name)
            elif a_node.attrib[PcsConstants.STANDBY_ON_FAIL] == PcsConstants.TRUE or \
                    a_node.attrib[PcsConstants.MAINTENANCE] == PcsConstants.TRUE or \
                    a_node.attrib[PcsConstants.PENDING] == PcsConstants.TRUE or \
                    a_node.attrib[PcsConstants.SHUTDOWN] == PcsConstants.TRUE:
                self._nodes[PcsConstants.UNHEALTHY].append(node_name)
            elif a_node.attrib[PcsConstants.ONLINE] == PcsConstants.TRUE and \
                    a_node.attrib[PcsConstants.STANDBY] == PcsConstants.TRUE:
                self._nodes[PcsConstants.STANDBY].append(node_name)
            elif a_node.attrib[PcsConstants.ONLINE] == PcsConstants.TRUE:
                self._nodes[PcsConstants.ONLINE].append(node_name)
            else:
                self._nodes[PcsConstants.UNHEALTHY].append(node_name)

    def _load_services_health(self):
        """
            Read xml output and load online and unhealthy services.
        """
        resource_path = "./resources/resource"
        clone_group_resource_path = "./resources/clone/group/resource"
        group_resource_path = "./resources/clone/group/resource"

        self._services[PcsConstants.ONLINE] = []
        self._services[PcsConstants.UNHEALTHY] = []

        if self._output is None:
            return

        resources = self._output.findall(resource_path)
        resources.extend(self._output.findall(clone_group_resource_path))
        resources.extend(self._output.findall(group_resource_path))

        for a_resource in resources:
            resource_name = a_resource.attrib[PcsConstants.ID]
            if a_resource.attrib[PcsConstants.ACTIVE] == PcsConstants.FALSE or \
                    a_resource.attrib[PcsConstants.ORPHANED] == PcsConstants.TRUE or \
                    a_resource.attrib[PcsConstants.BLOCKED] == PcsConstants.TRUE or \
                    a_resource.attrib[PcsConstants.FAILED] == PcsConstants.TRUE:
                self._services[PcsConstants.UNHEALTHY].append(resource_name)
            elif a_resource.attrib[PcsConstants.ROLE] == PcsConstants.STARTED:
                self._services[PcsConstants.ONLINE].append(resource_name)
            else:
                self._services[PcsConstants.UNHEALTHY].append(resource_name)

    def load(self):
        """
            Loads pcs status and stores unhealthy elements internally.
        """
        self._get_pcs_status()
        self._load_nodes_health()
        self._load_services_health()

    def refresh(self):
        """
            Refreshes the internal data structures.
        """
        self._nodes_configured = 0
        self._nodes = {}
        self._services = {}
        self.load()

    def get_health_status(self):
        """
            Finds and returns the cluster health.
        """
        if len(self._nodes_configured)//2 + 1 <= len(self._nodes[PcsConstants.OFFLINE]):
            return {"status": const.STATUSES.SUCCEEDED.value, "output": CLUSTER_STATUS.OFFLINE.value, "error": ""}

        if len(self._nodes_configured) == len(self._nodes[PcsConstants.STANDBY]):
            return {"status": const.STATUSES.SUCCEEDED.value, "output": CLUSTER_STATUS.STANDBY.value, "error": ""}

        if len(self._nodes_configured) != self._nodes[PcsConstants.COUNT]:
            return {"status": const.STATUSES.SUCCEEDED.value, "output": CLUSTER_STATUS.UNHEALTHY.value,
                    "error": f"Some nodes are missing from cluster. Expected: {self._nodes_configured}"}
        if len(self._nodes_configured) > len(self._nodes[PcsConstants.ONLINE]):
            return {"status": const.STATUSES.SUCCEEDED.value, "output": CLUSTER_STATUS.DEGRADED.value,
                    "error": f"All nodes are not online. online: {self._nodes[PcsConstants.ONLINE]}"}

        if len(self._services[PcsConstants.UNHEALTHY]) > 0:
            return {"status": const.STATUSES.SUCCEEDED.value, "output": CLUSTER_STATUS.DEGRADED.value,
                    "error": f"All services are not started. Sample: {self._services[PcsConstants.UNHEALTHY][:2]}"}

        return {"status": const.STATUSES.SUCCEEDED.value, "output": CLUSTER_STATUS.ONLINE.value, "error" : ""}

