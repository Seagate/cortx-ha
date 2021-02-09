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

from ha.core.error import ValidationFailedError
from ha.core.error import HAUnimplemented
from ha.core.controllers.pcs.pcs_controller import PcsController

class PcsNodeController(PcsController):
    """ Controller to manage node. """

    def __init__(self):
        """
        Initalize pcs cluster controller
        """
        super(PcsNodeController, self).__init__()
        self._element = "node"
        self._actions: list =  [method for method in dir(PcsNodeController)
            if method.startswith("_") is False]

    def _validate(self, args):
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

    def start(self, args: dict):
        """
        Start node.

        Args:
            args ([dict]): Args for commands. Example args: {node: <name>}.
        """
        raise HAUnimplemented("This operation is not implemented.")

    def stop(self, args: dict):
        """
        Stop node.

        Args:
            args ([dict]): Args for commands. Example args: {node: <name>}.
        """
        raise HAUnimplemented("This operation is not implemented.")

    def standby(self, args: dict):
        """
        Put node on standby.

        Args:
            args ([dict]): Args for commands. Example args: {node: <name>}.
        """
        raise HAUnimplemented("This operation is not implemented.")

    def active(self, args: dict):
        """
        Start resources on node.

        Args:
            args ([dict]): Args for commands. Example args: {node: <name>}.
        """
        raise HAUnimplemented("This operation is not implemented.")

    def status(self, args: dict):
        """
        Status node.

        Args:
            args ([dict]): Args for commands. Example args: {node: <name>}.
        """
        raise HAUnimplemented("This operation is not implemented.")

class PcsVMNodeController(PcsNodeController):
    def start(self, args: dict):
        raise HAUnimplemented("This operation is not implemented.")

    def stop(self, args: dict):
        raise HAUnimplemented("This operation is not implemented.")

class PcsHWNodeController(PcsNodeController):
    def start(self, args: dict):
        raise HAUnimplemented("This operation is not implemented.")

    def stop(self, args: dict):
        raise HAUnimplemented("This operation is not implemented.")
