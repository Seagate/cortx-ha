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
    def get_component_level(component: str) -> int:
        component_level = 0
        try:
            schema = HealthHierarchy.get_schema()
            components = schema["components"]
            for count, value in enumerate(components):
                if value == component:
                    component_level = count + 1
        except Exception as e:
            Log.error(f"Failed to fetch component level. Error: {e}")

        if component_level != 0:
            return component_level
        else:
            raise Exception("Failed to fetch component level.")

    @staticmethod
    def get_total_depth() -> int:
        total_depth = 0
        try:
            schema = HealthHierarchy.get_schema()
            components = schema["components"]
            total_depth = len(components)
        except Exception as e:
            Log.error(f"Failed to fetch total depth. Error: {e}")

        if total_depth != 0:
            return total_depth
        else:
            raise Exception("Failed to fetch total depth.")

    @staticmethod
    def get_next_components(component: str) -> list:
        next_components = []
        try:
            schema = HealthHierarchy.get_schema()
            components = schema["components"]
            for count, value in enumerate(components):
                if value == component:
                    if count < (len(components) -1 ):
                        next_components.append(components[count + 1])
        except Exception as e:
            Log.error(f"Failed fetching next component. Error: {e}")
        return next_components