#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
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

from cortx.utils.errors import BaseError
from cortx.utils.log import Log
from ha.fault_tolerance.const import ERROR_CODES

CC_OPERATION_SUCESSFUL     = 0x0000
CC_ERR_INVALID_VALUE       = 0x1001
CC_ERR_INTERRUPTED         = 0x1002
CC_INVALID_REQUEST         = 0x1003
CC_PROVIDER_NOT_AVAILABLE  = 0x1004
CC_INTERNAL_ERROR          = 0x1005
CC_SETUP_ERROR             = 0x1006
CC_RESOURCE_EXIST          = 0x1007
CC_OPERATION_NOT_PERMITTED = 0x1008
CC_FAILURE                 = 0x1009
CC_SERVICE_NOT_AVAILABLE   = 0x100A
CC_REQUEST_CANCELLED       = 0x100B
CC_NOT_IMPLEMENTED         = 0x100C
CC_SERVICE_CONFLICT        = 0x100D
CC_GATEWAY_TIMEOUT         = 0x100E
CC_UNAUTHORIZED_ERROR      = 0x100F
CC_UNKNOWN_ERROR           = 0x1010
CC_HTTP_ERROR              = 0x1011
CC_REQUEST_TIMEOUT         = 0x1012
CC_UN_SUPPORTED_CONTENT_TYPE = 0x1013
CC_TOO_MANY_REQUESTS       = 0x1014


class CcError(BaseError):
    """
    Parent class for the REST API error classes
    """

    def __init__(self, rc=0, desc=None, message_id=None, message_args=None):
        """ Instantiation Method for CcError class. """
        super(CcError, self).__init__(rc=rc, desc=desc, message_id=message_id,
                                       message_args=message_args)

        # Common error logging for all kind of CcError
        Log.error(f"{self._rc}:{self._desc}:{self._message_id}:{self._message_args}")


class InvalidRequest(CcError):
    """
    This error will be raised when an invalid response
    message is received for any of the cli commands.
    """

    _err = CC_INVALID_REQUEST
    _desc = "Invalid request."

    def __init__(self, _desc=None, message_id=ERROR_CODES.INVALID_REQUEST.value, message_args=None):
        """
        Instantiation Method for InvalidRequest class
        """
        super(InvalidRequest, self).__init__(
            CC_INVALID_REQUEST, _desc, message_id, message_args)

class CcNotFoundError(CcError):
    """
    This error is raised for all cases when an resource was not found
    """

    _desc = "An resource was not found."

    def __init__(self, _desc=None, message_id=ERROR_CODES.NOT_FOUND_ERROR.value, message_args=None):
        """
        Instantiation Method for CcNotFoundError class
        """
        super(CcNotFoundError, self).__init__(
            CC_INTERNAL_ERROR, _desc,
            message_id, message_args)

class CcPermissionDenied(CcError):
    """
    This error is raised for all cases when we don't have permissions
    """

    _desc = "Access to the requested resource is forbidden."

    def __init__(self, _desc=None, message_id=ERROR_CODES.PERMISSION_DENIED_ERROR.value, message_args=None):
        """
        Instantiation Method for CcPermissionDenied class
        """
        super(CcPermissionDenied, self).__init__(
            CC_OPERATION_NOT_PERMITTED, _desc,
            message_id, message_args)

class CcRequestTimeout(CcError):
    """
    This error indicates that the server did not receive a complete request message
    within the time that it was prepared to wait
    """

    _desc = "Failed to receive the request in time."

    def __init__(self, _desc=None, message_id=ERROR_CODES.REQUEST_TIMEOUT.value, message_args=None):
        """
        Instantiation Method for CcRequestTimeout class
        """
        super(CcRequestTimeout, self).__init__(
            CC_REQUEST_TIMEOUT, _desc,
            message_id, message_args)

class CcUnsupportedContentTypeError(CcError):
    """
    Server refuses to accept the request because the payload format is in an unsupported format.
    """

    _desc = "The Requested content type is not supported."

    def __init__(self, _desc=None, message_id=ERROR_CODES.UN_SUPPORTED_CONTENT_TYPE.value, message_args=None):
        """
        Instantiation Method for CcUnsupportedContentTypeError class
        """
        super(CcUnsupportedContentTypeError, self).__init__(
            CC_UN_SUPPORTED_CONTENT_TYPE, 'Unsupported Content Type: %s' % _desc,
            message_id, message_args)

class CcTooManyRequestsError(CcError):
    """
    This error represents the user has sent too many requests in a given
    amount of time (“rate limiting”).
    """

    _desc = "Too many requests."

    def __init__(self, _desc=None, message_id=ERROR_CODES.TOO_MANY_REQUESTS.value, message_args=None):
        """
        Instantiation Method for CcNotImplemented class
        """
        super(CcTooManyRequestsError, self).__init__(
            CC_TOO_MANY_REQUESTS, _desc,
            message_id, message_args)

class CcInternalError(CcError):
    """
    This error is raised by CLI for all unknown internal errors
    """

    _desc = "Internal Error."

    def __init__(self, _desc=None, message_id=ERROR_CODES.INTERNAL_ERROR.value, message_args=None):
        """
        Instantiation Method for CcInternalError class
        """
        super(CcInternalError, self).__init__(
            CC_INTERNAL_ERROR, 'Internal error: %s' % _desc,
            message_id, message_args)

class CcNotImplemented(CcError):
    """
    This error represents HTTP 501 Not Implemented Error
    """

    _desc = "Not Implemented."

    def __init__(self, _desc=None, message_id=ERROR_CODES.NOT_IMPLEMENTED.value, message_args=None):
        """
        Instantiation Method for CcNotImplemented class
        """
        super(CcNotImplemented, self).__init__(
            CC_NOT_IMPLEMENTED, _desc,
            message_id, message_args)

class CcServiceNotAvailable(CcError):
    """
    This  error represents Cc service is Not Available.
    """

    _desc = "The service is not available at the moment."

    def __init__(self, _desc=None, message_id=ERROR_CODES.SERVICE_NOT_AVAILABLE.value, message_args=None):
        """
        Instantiation Method for CcServiceNotAvailable class
        """
        super(CcServiceNotAvailable, self).__init__(
            CC_SERVICE_NOT_AVAILABLE, _desc,
            message_id, message_args)

class CcGatewayTimeout(CcError):

    """
    This error represents a scenario where Cc was acting as a gateway or proxy and did not receive
    a timely response from the upstream server.
    """

    _desc = "Unable to get timely response."

    def __init__(self, _desc=None, message_id=ERROR_CODES.GATEWAY_TIMEOUT.value, message_args=None):
        """
        Instantiation Method for CcGatewayTimeout class
        """
        super(CcGatewayTimeout, self).__init__(
            CC_GATEWAY_TIMEOUT, _desc,
            message_id, message_args)
