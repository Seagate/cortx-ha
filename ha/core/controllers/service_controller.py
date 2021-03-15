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

class ServiceController(ElementController):
    """ Controller to manage service. """

    def __init__(self):
        """
        Initalize ServiceController
        """
        super(ServiceController, self).__init__()

    def initialize(self, controllers):
        """
        Initialize the service controller
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def start(self, service: str, nodeids: list = None) -> dict:
        """
        Start service.

        Args:
            service (str): Service name.
            nodeids (list, optional): Node ids, if none then all node status.
                    Defaults to None.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def stop(self, service: str, nodeids: list = None) -> dict:
        """
        Stop service.

        Args:
            service (str): Service name.
            nodeids (list, optional): Node ids, if none then all node status.
                    Defaults to None.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def status(self, service: str, nodeids: list = None) -> dict:
        """
        Return status of service.

        Args:
            service (str): Service name.
            nodeids (list, optional): Node ids, if none then all node status.
                    Defaults to None.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")
