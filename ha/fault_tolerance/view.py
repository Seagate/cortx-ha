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

import json
from aiohttp import web


class CcResponse(web.Response):
    def __init__(self, res=None, status=200, headers=None,
                 content_type='application/json',
                 **kwargs):
        """Returns json response to web."""
        if not res:
            res= {}
        body = json.dumps(res)
        super().__init__(body=body, status=status, headers=headers,
                         content_type=content_type, **kwargs)


class CcHttpException(web.HTTPException):
    def __init__(self, status, error_id, message_id, error_message, args=None):
        self.status_code = status
        body = {
            "error_id": error_id,
            "error_message":  error_message,
        }
        if args is not None:
            body["error_format_args"] = args
        json_body = json.dumps(body)
        super().__init__(body=json_body, content_type='application/json')


class CcView(web.View):

    _resource_mapping = {}

    # common routes to used by subclass
    _app_routes = web.RouteTableDef()

    def __init__(self, request):
        """Init for view class."""
        super(CcView, self).__init__(request)

    async def get(self):
        """Generic get call implementation."""
        if self.request.match_info:
            response_obj = {}
            response_obj.update(self.request.match_info)
        return response_obj
