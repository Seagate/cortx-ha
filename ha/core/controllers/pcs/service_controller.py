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
from cortx.utils.log import Log
from ha import const
from ha.core.error import ClusterManagerError, HAUnimplemented
from ha.core.controllers.pcs.pcs_controller import PcsController
from ha.core.controllers.service_controller import ServiceController
from ha.core.controllers.controller_annotation import controller_error_handler


class PcsServiceController(ServiceController, PcsController):
    """ Controller to manage node. """

    def __init__(self):
        """
        Initalize pcs cluster controller
        """
        super(PcsServiceController, self).__init__()

    def initialize(self, controllers):
        """
        Initialize the service controller
        """
        self._controllers = controllers

    @controller_error_handler
    def start(self, service: str, nodeids: list = None) -> dict:
        """
        Start service.

        Args:
            service (str): Service name.
            nodeids (list, optional): Node ids, if none then all node status.
                    Defaults to None.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error"}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def stop(self, node_id: str, excludeResourceList: list = None) -> dict:
        """
        Stop service.

        Args:
            node_id (str): Private fqdn define in conf store.
            excludeResourceList (list): Service list which are not stopped.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error"}
                status: Succeeded, Failed, InProgress
        """
        try:
            resources: list = []
            output, _, _ = self._execute.run_cmd(const.LIST_PCS_RESOURCES, check_error=False)
            if "NO resources".lower() not in output.lower():
                for resource in output.split("\n"):
                    res = resource.split(":")[0]
                    if res != "" and res not in resources and res not in excludeResourceList:
                        resources.append(res)
            for resource in resources:
                self._execute.run_cmd(f"pcs resource ban {resource} {node_id}")
            Log.info(f"Waiting to stop resource on node {node_id}")
            time.sleep(const.BASE_WAIT_TIME)
            # TODO: Check if the resources are stopped EOS-23386
            return {"status": const.STATUSES.IN_PROGRESS.value, "msg": f"Resources stopped on node {node_id}"}
        except Exception as e:
            raise ClusterManagerError(f"Failed to stop resources on {node_id}, Error: {e}")

    @controller_error_handler
    def status(self, service: str, nodeids: list = None) -> dict:
        """
        Return status of service.

        Args:
            service (str): Service name.
            nodeids (list, optional): Node ids, if none then all node status.
                    Defaults to None.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error"}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    def clear_resources(self, node_id: str):
        """
        Clear resources on node.

        Args:
            nodeid (str): Private fqdn define in conf store.
        """
        try:
            resources: list = []
            output, _, _ = self._execute.run_cmd(const.LIST_PCS_RESOURCES, check_error=False)
            if "NO resources".lower() not in output.lower():
                for resource in output.split("\n"):
                    res = resource.split(":")[0]
                    if res != "" and res not in resources:
                        resources.append(res)
            for resource in resources:
                self._execute.run_cmd(f"pcs resource clear {resource} {node_id}")
            Log.info(f"Cleared resource on node {node_id}")
        except Exception as e:
            raise ClusterManagerError(f"Failed to clear resources on {node_id}, Error: {e}")
