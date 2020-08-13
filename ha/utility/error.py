#!/usr/bin/env python3

"""
 ****************************************************************************
 Filename:          exception.py
 _description:      Errors for various HA related scenarios.

 Creation Date:     2020/08/08
 Author:            Ajay Paratmandali

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2020 - $Date: 2020/08/08 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 ****************************************************************************
"""

from eos.utils.errors import BaseError
from eos.utils.log import Log

HA_BASIC_ERROR          = 0x0000
HA_UNIMPLEMENTED_ERROR  = 0x0001
HA_INVALID_NODE_ERROR   = 0x0002
HA_COMMAND_TERMINATION_ERROR   = 0x0003

class HAError(BaseError):
    def __init__(self, rc=1, desc=None, message_id=HA_BASIC_ERROR, message_args=None):
        """
        Parent class for the HA error classes
        """
        super(HAError, self).__init__(rc=rc, desc=desc, message_id=message_id,
                                       message_args=message_args)
        Log.error(f"error({self._message_id}):rc({self._rc}):{self._desc}:{self._message_args}")

class HAUnimplemented(HAError):
    def __init__(self, desc=None):
        """
        Handle unimplemented function error.
        """
        _desc = "This feature is not implemented." if desc is None else desc
        _message_id = HA_UNIMPLEMENTED_ERROR
        _rc = 1
        super(HAUnimplemented, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class HAInvalidNode(HAError):
    def __init__(self, desc=None):
        """
        Handle invalid node error.
        """
        _desc = "Invalid node. Not part of cluster." if desc is None else desc
        _message_id = HA_INVALID_NODE_ERROR
        _rc = 1
        super(HAInvalidNode, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class HACommandTerminated(HAError):
    def __init__(self, desc=None):
        """
        Handle command terminamation error.
        """
        _desc = "Failed to execute command" if desc is None else desc
        _message_id = HA_COMMAND_TERMINATION_ERROR
        _rc = 1
        super(HACommandTerminated, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)