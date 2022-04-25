#!/usr/bin/env python3

# CORTX Python common library.
# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

import time
from ha.fault_tolerance.view import CcView, CcResponse


@CcView._app_routes.view("/api/v1/system/health/{resource}/{id}")
class CcResource(CcView):

    """
    Resource class will fetch the status for all the resources,
    and return the response json.
    resources can be:- cluster, node, disk, cvgs etc
    """
    def __init__(self, request):
        """Init API request for resources."""
        super(CcResource, self).__init__(request)

    async def get(self):
        res_type = self.request.match_info.get("resource", "")
        res_id = self.request.match_info.get("id", "")
        # ToDo: get status of the resource from system health
        # currently keeping status = "online"
        status = "online"
        json_msg = {
            "id": f"{res_id}",
            "type": f"{res_type}",
            "last_updated_timestamp": time.time(),
            "resource_status": f"{status}"
        }
        return CcResponse(json_msg)
