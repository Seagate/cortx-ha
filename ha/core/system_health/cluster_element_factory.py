#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

from importlib import import_module

from cortx.utils.log import Log

from ha.core.system_health.cluster_elements.element import Element
from ha.core.system_health.const import CLUSTER_ELEMENT_CLASSES

class ClusterElementFactory:
    """
    Cluster Element factory to keep track of elements.
    """
    _element_instances : dict = {}

    @staticmethod
    def build_elements() -> None:
        """
        Build all elements.
        """
        Log.info("Build all the element inside the cluster")
        elements = CLUSTER_ELEMENT_CLASSES.CLASS_TO_ELEMENT_MAP
        for element in elements.keys():
            class_path_list: list = elements[element].split('.')[:-1]
            module = import_module(f"{'.'.join(class_path_list)}")
            element_instance = getattr(module, elements[element].split('.')[-1])()
            ClusterElementFactory._element_instances[element] = element_instance
            Log.info(f"Element {elements[element]} is initalized...")

    @staticmethod
    def get_element(element: str) -> Element:
        """
        Get instance of element

        Args:
            element (str): cluster element.

        Returns:
            Element: Generic element.
        """
        return ClusterElementFactory._element_instances[element]
