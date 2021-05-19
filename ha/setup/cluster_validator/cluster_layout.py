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

"""
Module provides an interface for component files which describe HA cluster.
"""

import json
from typing import Dict, List
from abc import ABC
from ha.core.error import SetupError, HA_CLUSTER_CONFIG_ERROR


class ValidationConfigError(SetupError):
    """
    Error during cluster configuration import or validation.
    """
    def __init__(self, desc=None):
        _desc = "HA cluster configuration error" if desc is None else desc
        _message_id = HA_CLUSTER_CONFIG_ERROR
        _rc = 1
        super().__init__(rc=_rc, desc=_desc, message_id=_message_id)


class ClusterLayout(ABC):
    """Abstract class for Cluster Layout implementations."""
    resources: dict
    nodes: list

    def __repr__(self):
        return f"nodes: {self.nodes}, resources: {self.resources}"


class ClusterLayoutJson(ClusterLayout):
    """
    Presumably this class is supposed to store cluster layout

    Layout is imported from component files.
    """

    @classmethod
    def from_json_file(cls, file_list: List[str], node_list: List[str]) -> "ClusterLayoutJson":
        """
        Read a bunch of component JSON files and create ClusterLayout object.

        Node list is passed manually since they can vary between configuratons.
        The resource layout itself is saved as a simple dictionary since
        component file format is currently unstable.
        """
        layout = {}
        resource_counter = 0
        for filename in file_list:
            with open(filename, "r") as f:
                component = json.load(f)
                for resource, definition in component.items():
                    if resource in layout:
                        raise ValidationConfigError(
                            f"Resource {resource} already exists in layout (processing {filename})")
                    try:
                        if definition['ha']['mode'] == "active_passive":
                            resource_counter += 1
                        else:
                            total_clones = definition['ha']['clones']['active'][1]
                            total_clones = len(node_list) if total_clones == "INFINITY" else int(total_clones)
                            resource_counter += total_clones
                    except Exception as err:
                        raise ValidationConfigError(
                            f"Required keys for resource {resource} are missing") from err
                    layout[resource] = definition
        return ClusterLayoutJson(nodes=node_list, resources=layout,
                                 total_num_resources=resource_counter)

    def __init__(self, nodes: List[str], resources: Dict, total_num_resources: int):
        self.resources = resources
        self.nodes = nodes
        self.total_number_of_resources = total_num_resources

    def get_num_nodes(self) -> int:
        """Return number of available nodes."""
        return len(self.nodes)
