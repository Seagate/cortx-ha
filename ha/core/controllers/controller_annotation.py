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
import traceback
from ha import const
from cortx.utils.log import Log

def controller_error_handler(func):
    def inner_function(*args, **kwargs) -> str:
        try:
            result: dict = func(*args, **kwargs)
            return json.dumps(result)
        except Exception as e:
            Log.error(f"ClusterManagerException. {func.__name__} failed. {traceback.format_exc()}, {e}")
            result: dict = {"status": const.STATUSES.FAILED.value, "output": "",
                "error": f"ClusterManagerException. {func.__name__} failed. Error: {e}"}
            return json.dumps(result)
    return inner_function