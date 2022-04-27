#!/usr/bin/env python3

# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
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

import enum
from ha.util.enum_list import EnumListMeta

class HEALTH_EVENT_SOURCES(enum.Enum, metaclass=EnumListMeta):
    CSM = 'csm'
    HA = 'ha'
    HARE = 'hare'
    MONITOR = 'monitor'

# Message types of components
class FAULT_TOLERANCE_KEYS(enum.Enum, metaclass=EnumListMeta):
    HARE_HA_MESSAGE_TYPE = 'cortx_health_events'
    MONITOR_HA_MESSAGE_TYPE = 'cortx_health_events'
    CSM_HA_MESSAGE_TYPE = 'cortx_health_events'


class ERROR_CODES(enum.Enum, metaclass=EnumListMeta):
    INVALID_REQUEST         = 'MalformedRequest'
    UNKNOWN_ERROR           = 'UnknownError'
    RESOURCE_EXISTS         = 'ResourceExist'
    INTERNAL_ERROR          = 'InternalError'
    NOT_FOUND_ERROR         = 'NotFoundError'
    PERMISSION_DENIED_ERROR = 'PermissionDenied'
    UNAUTHORISED            = 'Unauthorized'
    RESOURCE_NOT_AVAILABLE  = 'ResourceNotAvailable'
    TYPE_ERROR              = 'TypeError'
    NOT_IMPLEMENTED         = 'NotImplemented'
    SERVICE_CONFLICT        = 'ServiceConflict'
    GATEWAY_TIMEOUT         = 'GatewayTimeout'
    REQUEST_TIMEOUT         = 'RequestTimeout'
    UNAUTHORIZED_ERROR      = 'UnauthorizedError'
    SERVICE_NOT_AVAILABLE   = 'ServiceNotAvailable'
    REQUEST_CANCELLED       = 'RequestCancelled'
    SETUP_ERROR             = 'SetupError'
    HTTP_ERROR              = 'HttpError'
    UN_SUPPORTED_CONTENT_TYPE  = 'UnsupportedContenttType'
    TOO_MANY_REQUESTS       = 'TooManyRequests'

# Success status response code
SUCCESS_CODE = 200

# Used to set default value in const.HA_CONFIG_FILE
# TODO : To be replaced by actual values when they are available in config
NOT_DEFINED = 'NOT_DEFINED'
