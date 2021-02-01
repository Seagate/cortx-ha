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

class ElementController:
    """
    Generic element controller class
    """
    def __init__(self):
        """
        Initialize element controller.
        """
        self._responce = None

    def _validate(self, args) -> None:
        """
        Abstract validation function.

        Args:
            args (dict): args for validation.
        """
        pass

    def process_request(self, args: dict, responce: object) -> None:
        """
        Args related to conroller and action.

        Args:
            args (dict): args for action and controller.
            responce (object): responce object for output and rc.

        { action: [start|stop|status],
            and other args depend on action
        }
        """
        # set responce.output and responce.rc
        self._responce = responce
        self._validate(args)
        getattr(self, args.action)()