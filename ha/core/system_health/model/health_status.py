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

class StatusOutput:
    def __init__(self, version: str):
        self.version = version
        self.health = []

    def add_health(self, health: dict) -> None:
        self.health.append(health)

    def to_json(self):
        return json.dumps(self, default=lambda a: a.__dict__)

class ComponentStatus:
    def __init__(self, resource: str, component_id: str, status: str, update_timestamp: str):
        self.resource = resource
        self.id = component_id
        self.status = status
        self.last_updated_time = update_timestamp
        self.sub_resources = None

    def add_resource(self, resource: dict) -> None:
        if self.sub_resources is None:
            self.sub_resources = []
        self.sub_resources.append(resource)

    def to_json(self):
        return json.dumps(self, default=lambda a: a.__dict__)