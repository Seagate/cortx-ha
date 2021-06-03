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
from ha import const
from cortx.utils.log import Log

class HealthHierarchy:

    SCHEMA = None

    @staticmethod
    def get_schema():
        """
        Schema initialization
        """
        if HealthHierarchy.SCHEMA is None:
            with open(const.HEALTH_HIERARCHY_FILE, "r") as fi:
                HealthHierarchy.SCHEMA = json.load(fi)
        return HealthHierarchy.SCHEMA

    @staticmethod
    def get_element_level(element: str) -> int:
        element_level = 0
        try:
            schema = HealthHierarchy.get_schema()
            elements = schema["elements"]
            for count, value in enumerate(elements):
                if value == element:
                    element_level = count + 1
        except Exception as e:
            Log.error(f"Failed to fetch element level. Error: {e}")

        if element_level != 0:
            return element_level
        else:
            raise Exception("Failed to fetch element level.")

    @staticmethod
    def get_total_depth() -> int:
        total_depth = 0
        try:
            schema = HealthHierarchy.get_schema()
            elements = schema["elements"]
            total_depth = len(elements)
        except Exception as e:
            Log.error(f"Failed to fetch total depth. Error: {e}")

        if total_depth != 0:
            return total_depth
        else:
            raise Exception("Failed to fetch total depth.")

    @staticmethod
    def get_next_elements(element: str) -> list:
        next_elements = []
        try:
            schema = HealthHierarchy.get_schema()
            elements = schema["elements"]
            for number in range(len(elements)):
                if elements[number] == element:
                    if number < (len(elements) -1 ):
                        next_elements.append(elements[number + 1])
        except Exception as e:
            Log.error(f"Failed fetching next element. Error: {e}")
        return next_elements