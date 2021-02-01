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
from cortx.utils.conf_store.conf_store import Conf
from ha.core.controller.element_controller import ElementController

class ElementControllerFactory:

    _controllers: dict = {}

    @staticmethod
    def get_controller(env: str, cluster_type: str, element: str) -> ElementController:
        """
        Get specific controller instance to perform operation.

        Args:
            env (str): Detect controller as per env.
            cluster_type (str): Cluster type depend on cluster running on system.
            element (str): element of cluster.

        Returns:
            ElementController: It is instance of controller need to return.
        """
        for key in _controllers.keys():
            if element in list(key):
                return _controllers[key]
        controllers = Conf.get(const.CLUSTER_MANAGER_CONTROLLER_INDEX,
                        f"{env}.{cluster_type}")
        for controller in controllers:
            if element in controller["elements"]:
                element_li: list = controller["elements"]
                _controllers[str(element_li)] = controller["interface"]()
                return _controllers[str(element_li)]