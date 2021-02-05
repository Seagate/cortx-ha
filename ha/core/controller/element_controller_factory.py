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

from importlib import import_module

from cortx.utils.log import Log
from cortx.utils.conf_store.conf_store import Conf
from ha import const
from ha.core.controller.element_controller import ElementController

class ElementControllerFactory:

    # Example:
    # {'instances':
    #   {'ha.core.controller.pcs.cluster_controller.PcsClusterController':
    #       <ha.core.controller.pcs.cluster_controller.PcsClusterController object at 0x7f056c12ac18>},
    # 'elements':
    #   {'cluster':
    #       'ha.core.controller.pcs.cluster_controller.PcsClusterController'}}
    _controllers: dict = {
        "instances": {},
        "elements": {}
    }

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
        element_dict = ElementControllerFactory._controllers
        if element in element_dict["elements"]:
            return element_dict["instances"][element_dict["elements"]]
        controllers: dict = Conf.get(const.CM_CONTROLLER_INDEX,
                        f"{env}.{cluster_type}")
        for controller in controllers:
            if element in controller["elements"]:
                Log.info(f"Initalizing controller api {controller['interface']}")
                class_path_list: list = controller["interface"].split('.')[:-1]
                module = import_module(f"{'.'.join(class_path_list)}")
                element_instace = getattr(module, controller["interface"].split('.')[-1])()
                # Adding instance to element dict.
                element_dict["elements"][element] = controller["interface"]
                element_dict["instances"][controller["interface"]] = element_instace
                Log.info(f"Registered {element_instace} with cluster manager.")
                return element_instace