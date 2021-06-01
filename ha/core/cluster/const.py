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

from enum import Enum

# System health output versions
SYSTEM_HEALTH_OUTPUT_V1 = "1.0"

# Variable arguments supported by get_system_health() API
class GET_SYS_HEALTH_ARGS(Enum):
    ID = "id"

# System health output attributes
class SYS_HEALTH_OP_ATTRS(Enum):
    VERSION = "version"
    RESOURCE = "resource"
    ID = "id"
    STATUS = "status"
    UPDATE_TIMESTAMP = "update_timestamp"