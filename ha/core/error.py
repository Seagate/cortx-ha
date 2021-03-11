#!/usr/bin/env python3

# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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

import inspect

from cortx.utils.errors import BaseError
from cortx.utils.log import Log

HA_BASIC_ERROR                  = 0x0000
HA_UNIMPLEMENTED_ERROR          = 0x0001
HA_INVALID_NODE_ERROR           = 0x0002
HA_COMMAND_TERMINATION_ERROR    = 0x0003
HA_TEST_FAILED                  = 0x0004
HA_SUPPORT_BUNDLE_FAILED        = 0x0005
HA_CLUSTER_MANAGER_FAILED       = 0x0006
HA_PRE_UPGRADE_FAILED           = 0x0007
HA_SETUP_FAILED                 = 0x0008
HA_REMOTE_EXECUTOR_FAILED       = 0x0009

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
        _desc = f"Unimplemented Feature. stack: {inspect.stack()[1]}" if desc is None else desc
        _message_id = HA_UNIMPLEMENTED_ERROR
        _rc = 1
        super(HAUnimplemented, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class HAInvalidNode(HAError):
    def __init__(self, desc=None):
        """
        Handle invalid node error.
        """
        _desc = '[%s] %s' %(inspect.stack()[1][3], desc)
        _message_id = HA_INVALID_NODE_ERROR
        _rc = 1
        super(HAInvalidNode, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class HACommandTerminated(HAError):
    def __init__(self, desc=None):
        """
        Handle command terminamation error.
        """
        _desc = '[%s] %s' %(inspect.stack()[1][3], desc)
        _message_id = HA_COMMAND_TERMINATION_ERROR
        _rc = 1
        super(HACommandTerminated, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class HAInvalidCommand(HAError):
    def __init__(self, desc=None):
        """
        Handle command terminamation error.
        """
        _desc = '[%s] %s' %(inspect.stack()[1][3], desc)
        _message_id = HA_COMMAND_TERMINATION_ERROR
        _rc = 1
        super(HAInvalidCommand, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class HATestFailedError(HAError):
    def __init__(self, desc=None):
        """
        Handle Test Failed Error.
        """
        _desc = '[%s] %s' %(inspect.stack()[1][3], desc)
        _message_id = HA_TEST_FAILED
        _rc = 1
        super(HATestFailedError, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class RemoteExecutorError(HAError):
    '''
    Remote Node Execution Exception handling
    '''
    def __init__(self, desc=None):
        """
        Init method.
        """
        _desc = f'{"Failed to execute opeartion on a remote node"}' if desc is None else desc
        _message_id = HA_REMOTE_EXECUTOR_FAILED
        _rc = 1
        super(RemoteExecutorError, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class SupportBundleError(HAError):
    def __init__(self, desc=None):
        """
        Handle Support Bundle error.
        """
        _desc = f"Failed to create Support Bundle. stack: {inspect.stack()[1]}" if desc is None else desc
        _message_id = HA_SUPPORT_BUNDLE_FAILED
        _rc = 1
        super(SupportBundleError, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class ClusterManagerError(HAError):
    def __init__(self, desc=None):
        """
        Handle Support Bundle error.
        """
        _desc = "Failed to perform Cluster Manager Operation" if desc is None else desc
        _message_id = HA_CLUSTER_MANAGER_FAILED
        _rc = 1
        super(ClusterManagerError, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)


class PreRequisiteUpgradeError(HAError):
    """
    Disruptive upgrade prerequisites exceptions
    """
    def __init__(self, desc=None):
        _desc = "Failed to prepare to disruptive upgrade" if desc is None else desc
        _message_id = HA_PRE_UPGRADE_FAILED
        _rc = 1
        super(PreRequisiteUpgradeError, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class SetupError(HAError):
    def __init__(self, desc=None):
        """
        Handle HA .
        """
        _desc = "HA miniprovision failure." if desc is None else desc
        _message_id = HA_SETUP_FAILED
        _rc = 1
        super(SetupError, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class CreateResourceError(SetupError):
    """Exception to indicate any failure happened during resource creation."""


class CreateResourceConfigError(CreateResourceError):
    """Exception to indicate that given resource configuration is incorrect or incomplete."""

class HaPrerequisiteException(SetupError):
    """
    Exception to indicate that some error happened during HA prerequisite checks.
    """
    pass

class HaConfigException(SetupError):
    """
    Exception to indicate that config command failed during cluster config.
    """
    pass

class HaInitException(SetupError):
    """
    Exception to indicate that cleanup command failed due to some error.
    """
    pass

class HaCleanupException(SetupError):
    """
    Exception to indicate that cleanup command failed due to some error.
    """
    pass
