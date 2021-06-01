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
        self.system_status = []

    def add_system_status(self, system_status: dict) -> None:
        self.system_status.append(system_status)

    def to_json(self):
        return json.dumps(self, default=lambda a: a.__dict__)

class ElementStatus:
    def __init__(self, resource: str, id: str, status: str, update_timestamp: str):
        self.resource = resource
        self.id = id
        self.status = status
        self.update_timestamp = update_timestamp
        self.sub_resource = None

    def add_resource(self, resource: dict) -> None:
        if self.sub_resource is None:
            self.sub_resource = []
        self.sub_resource.append(resource)