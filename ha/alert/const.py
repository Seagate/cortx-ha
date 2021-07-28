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


from ha.const import _DELIM

# pacemaker alerts constants
class ALERTS:
    REQUIRED_COMPONENT = "ha"
    REQUIRED_EVENTS = ["node" , "resource"]
    ALERT_FILTER_TYPE = f"alert{_DELIM}filter_type"
    PK_ALERT_EVENT_COMPONENTS = f"alert{_DELIM}components"
    PK_ALERT_EVENT_COMPONENT_MODULES = f"alert{_DELIM}modules"
    PK_ALERT_EVENT_OPERATIONS = f"alert{_DELIM}operations"
    logger_utility_iec_cmd="logger -i -p local3.err"


