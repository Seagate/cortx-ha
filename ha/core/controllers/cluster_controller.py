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

from ha.core.error import HAUnimplemented
from ha.core.controllers.element_controller import ElementController
from ha.core.controllers.controller_annotation import controller_error_handler


class ClusterController(ElementController):
    """ Cluster controller to perform cluster level operation. """

    def __init__(self):
        """
        Initalize ClusterController
        """
        super(ClusterController, self).__init__()

    def initialize(self, controllers):
        """
        Initialize the cluster controller
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def start(self, sync=False, timeout=30) -> dict:
        """
        Start cluster and all service.

        Args:
            sync (bool, optional): if sync is True then start will check the status for timeout seconds.
            timeout (int, optional): timeout(in seconds) can be specified for sync=True otherwise ignored.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def stop(self, sync=True, timeout=30) -> dict:
        """
        Stop cluster and all service.

        Args:
            sync (bool, optional): if sync is True then stop will check the status for timeout seconds.
            timeout (int, optional): timeout(in seconds) can be specified for sync=True otherwise ignored.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def status(self) -> dict:
        """
        Status cluster and all service. It gives status for all resources.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error":""}
                status: Succeeded, Failed
                output: dict of resource and status.
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def standby(self, sync=True, timeout=30) -> dict:
        """
        Put cluster in standby mode.

        Args:
            sync (bool, optional): if sync is True then standby will check the status for timeout seconds.
            timeout (int, optional): timeout(in seconds) can be specified for sync=True otherwise ignored.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def active(self, sync=True, timeout=30) -> dict:
        """
        Activate all node.

        Args:
            sync (bool, optional): if sync is True then standby will check the status for timeout seconds.
            timeout (int, optional): timeout(in seconds) can be specified for sync=True otherwise ignored.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def node_list(self) -> dict:
        """
        Provide node list.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error":""}
                status: Succeeded, Failed
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def service_list(self) -> dict:
        """
        Provide service list.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error":""}
                status: Succeeded, Failed
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def storageset_list(self) -> dict:
        """
        Provide storageset list.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error":""}
                status: Succeeded, Failed
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def add_node(self, nodeid: str, cluster_user: str, cluster_password: str) -> dict:
        """
        Add new node to cluster.

        Args:
            nodeid (str, required): Provide nodeid.
            cluster_user (str, required): Provide cluster_user.
            cluster_password (str, required): Provide cluster_password.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def add_storageset(self, nodeid: str = None, descfile: str = None) -> dict:
        """
        Add new storageset to cluster.

        Args:
            nodeid (str, optional): Provide nodeid. Defaults to None.
            filename (str, optional): Provide descfile. Defaults to None.

        Returns:
            ([dict]): Return dictionary. {"status": "", "output":"", "error":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")