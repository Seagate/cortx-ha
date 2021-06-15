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

import json

from ha.core.system_health.system_health import SystemHealth
from ha.core.system_health.const import CLUSTER_ELEMENTS
from ha import const
from ha.core.cluster.const import SYSTEM_HEALTH_OUTPUT_V1, GET_SYS_HEALTH_ARGS

class SystemHealthController(SystemHealth):
    """ System health controller to perform system health operations. """

    def __init__(self, store):
        """
        Initalize SystemHealthController
        """
        super().__init__(store)

    def get_status(self, component: CLUSTER_ELEMENTS = CLUSTER_ELEMENTS.CLUSTER.value, depth: int = 1, version: str = SYSTEM_HEALTH_OUTPUT_V1, **kwargs) -> json:
        """
        Return health status for the requested components.
        Args:
            component ([CLUSTER_ELEMENTS]): The component whose health status is to be returned.
            depth ([int]): A depth of elements starting from the input "component" that the health status
                is to be returned.
            version ([str]): The health status json output version
            **kwargs([dict]): Variable number of arguments that are used as filters,
                e.g. "id" of the input "component".
        Returns:
            ([dict]): Returns dictionary. {"status": "Succeeded"/"Failed"/"Partial", "output": "", "error": ""}
                status: Succeeded, Failed, Partial
                output: Dictionary with element health status
                error: Error information if the request "Failed"
        """
        # Check if unsupported element status requested.
        unsupported_element = True
        for supported_element in CLUSTER_ELEMENTS:
            if component == supported_element.value:
                unsupported_element = False
                break
        if unsupported_element:
            return json.dumps({"status": const.STATUSES.FAILED.value, "output": "", "error": "Invalid element"})

        # Currently only "id" is supported as a filter
        if kwargs and GET_SYS_HEALTH_ARGS.ID.value not in kwargs:
            return json.dumps({"status": const.STATUSES.FAILED.value, "output": "", "error": "Invalid filter argument(s)"})

        return super().get_status(component, depth, version, **kwargs)