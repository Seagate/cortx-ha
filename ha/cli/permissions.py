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


"""
user validation, permissions validation module
"""

import grp
import getpass
import os
import errno

from ha import const
from cortx.utils.log import Log
from ha.cli.error import Error

class Permissions:

    def __init__(self):
        self._is_hauser = False

    """
    Routine used by executors to confirm acess permissions.
    Used to differentiate between external and internal CLIs
    """
    def is_ha_user(self):
        return self._is_hauser

    def validate_permissions(self):

        # confirm that user is root or part of haclient group"

        user = getpass.getuser()
        group_id = os.getgid()
                
        try:
            # find group id for root and haclient
            id_ha = grp.getgrnam(const.USER_GROUP_HACLIENT)
            id_root = grp.getgrnam(const.USER_GROUP_ROOT)

            # if group not root or haclient return error
            if group_id != id_ha.gr_gid and group_id != id_root.gr_gid:
                Log.error(f"User {user} does not have necessary permissions to execute this CLI")
                raise Error(errno.EACCES,
                            f"User {user} does not have necessary permissions to execute this CLI")

            # The user name "hauser"; which is part of the "haclient" group;
            # is used by HA.
            # internal commands are allowed only if the user is "hauser"
            if user == const.USER_HA_INTERNAL:
                self._is_hauser = True


        # TBD : If required raise seperate exception  for root and haclient
        except KeyError:
            Log.error("Group root / haclient is not defined")
            raise Error(errno.EINVAL,
                "Group root / haclient is not defined ")
            


