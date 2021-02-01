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

    def _validate(self, args) -> None:
        """
        Validate args.

        Args:
            args ([dict]): cluster args

        {element: cluster, action: <start|stop|standby|active>,
        args: {process_type: <sync|async>}}
        """
        pass

    def start(self) -> None:
        raise HAUnimplemented("This feature is not implemented")

    def stop(self) -> None:
        raise HAUnimplemented("This feature is not implemented")

    def standby(self) -> None:
        raise HAUnimplemented("This feature is not implemented")

    def active(self) -> None:
        raise HAUnimplemented("This feature is not implemented")