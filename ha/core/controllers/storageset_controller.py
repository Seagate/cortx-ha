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

class StorageSetController(ElementController):
    """ Perform storage set level operation. """

    def __init__(self):
        """
        Initalize StorageSetController controller
        """
        super(StorageSetController, self).__init__()

    @controller_error_handler
    def start(self, storagesetid) -> dict:
        """
        Start storagesetid and all service.

        Args:
            storagesetid (str): Storageset ID from cluster nodes.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def stop(self, storagesetid) -> dict:
        """
        Stop storagesetid and all service.

        Args:
            storagesetid (str): Storageset ID from cluster nodes.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def status(self, storagesetid) -> dict:
        """
        Status storagesetid and all service. It gives status for all resources.

        Args:
            storagesetid (str): Storageset ID from cluster nodes.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def active(self, storagesetid) -> dict:
        """
        active storagesetid and all service. It gives status for all resources.

        Args:
            storagesetid (str): Storageset ID from cluster nodes.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")

    @controller_error_handler
    def standby(self, storagesetid) -> dict:
        """
        standby storagesetid and all service.

        Args:
            storagesetid (str): Storageset ID from cluster nodes.

        Returns:
            ([dict]): Return dictionary. {"status": "", "msg":""}
                status: Succeeded, Failed, InProgress
        """
        raise HAUnimplemented("This operation is not implemented.")
