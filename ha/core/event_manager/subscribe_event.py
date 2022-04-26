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

from typing import List
from ha.k8s_setup import const
from ha.core.event_manager.resources import RESOURCE_STATUS
from ha.core.event_manager.resources import RESOURCE_TYPES, FUNCTIONAL_TYPES

class SubscribeEvent:
    def __init__(self, resource_type : RESOURCE_TYPES, states : List[RESOURCE_STATUS],
                 functional_types: List[FUNCTIONAL_TYPES] = ["ALL"]):
        """
        Subscribe event object.
        For HA state will be dict of {state: actions}
        For Other Component states will be list.

        Args:
            resource_type (str): Type of resource.
            states (list): States
            functional_types(list): Functional types of resource (Default value is ALL)
        """
        self.states = []
        self.functional_types = []
        self.resource_type = resource_type.value \
            if isinstance(resource_type, RESOURCE_TYPES) \
                else resource_type
        for state in states:
            st = state.value if isinstance(state, RESOURCE_STATUS) else state
            self.states.append(st)

        # Functional type specific to the resource will be added to event.
        # If component subscribe request won't have any functional type specified,
        # all FUNCTIONAL_TYPES will be considered.
        try:
            resource_func_types = FUNCTIONAL_TYPES[self.resource_type.upper()]
        except KeyError as err:
            raise Exception(f"Unsupported resource type '{err}'")

        for func_type in functional_types:
            if func_type.upper() == "ALL":
                self.functional_types = [fn_type.value for fn_type in resource_func_types.value]
            else:
                func_type = func_type.lower()
                func_type = resource_func_types.value(func_type).value
                self.functional_types.append(func_type)
