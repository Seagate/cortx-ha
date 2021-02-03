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

from cortx.utils.log import Log

from ha import const
from ha.core.error import ValidationFailedError
from ha.core.controller.element_controller import ElementController
from ha.core.error import HAUnimplemented

class PcsClusterController(ElementController):
    """
    Pcs cluster controller to perform pcs cluster level operation.
    """
    def __init__(self):
        """
        Initalize pcs cluster controller
        """
        super(PcsClusterController, self).__init__()
        self._actions: list =  [method for method in dir(PcsClusterController)
            if method.startswith("_") is False]

    def _validate(self, args: dict) -> None:
        """
        Validate args.

        Args:
            args ([dict]): cluster args

        raise:
            ValidationFailedError

        {element: cluster, action: <start|stop|standby|active>,
        args: {process_type: <sync|async>}}
        """
        action: str = args["action"] if "action" in args else None
        if action not in self._actions:
            raise ValidationFailedError(f"Invalid action {action} for cluster controller.")

    def start(self, args: dict) -> None:
        """
        Start cluster and all service.

        Args:
            args ([dict]): Args for commands. Example args: {}.
                            No extra argument needed for cluster start.
        """
        raise HAUnimplemented("This operation is not supported.")

    def stop(self, args: dict) -> None:
        """
        Stop cluster and all service.

        Args:
            args ([dict]): Args for commands. Example args: {}.
                            No extra argument needed for cluster stop.
        """
        raise HAUnimplemented("This operation is not supported.")

    def status(self, args: dict) -> None:
        """
        Status cluster and all service. It gives status for all resources.

        Args:
            args ([dict]): Args for commands. Example args: {}.
                            No extra argument needed for cluster status.
        """
        raise HAUnimplemented("This operation is not supported.")

    def standby(self, args: dict) -> None:
        """
        Put cluster in standby mode.

        Args:
            args ([dict]): Args for commands. Example args: {}.
                            No extra argument needed for cluster standby.
        """
        raise HAUnimplemented("This operation is not supported.")

    def active(self, args: dict) -> None:
        """
        Start cluster services.

        Args:
            args ([dict]): Args for commands. Example args: {}.
                            No extra argument needed for cluster active.
        """
        raise HAUnimplemented("This operation is not supported.")
