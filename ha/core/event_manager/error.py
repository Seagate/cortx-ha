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

from ha.core.error import HA_EVENT_MANAGER_ERROR
from ha.core.error import HAError

class EventManagerException(HAError):
    def __init__(self, desc=None):
        """
        Handle event manager function error.
        """
        _desc = "Failed event manager action"
        _message_id = HA_EVENT_MANAGER_ERROR
        _rc = 1
        super(EventManagerException, self).__init__(rc=_rc, desc=_desc, message_id=_message_id)

class InvalidComponent(EventManagerException):
    """
    Raise exception for invalid component
    """

class InvalidEvent(EventManagerException):
    """
    Raise exception for invalid event.
    """

class UnSubscribeException(EventManagerException):
    """
    Raise Exception
    """

class SubscribeException(EventManagerException):
    """
    Raise exception for errors during subscription
    """

class PublishException(EventManagerException):
    """
    Raise exception for errors when publishig the events
    """
