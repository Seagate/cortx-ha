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


"""
 ****************************************************************************
 Description:       Validation test for user and permissions.
 ****************************************************************************
"""

import os
import pathlib
import sys
import traceback


def test_validate_user_permissions():
    """
    R/W for log for root and other user
    R/W for conf for root
    R for conf for other user
    """
    from ha.setup.ha_setup import PostInstallCmd
    try:
        print("********Validate user and permissions.********")
        PostInstallCmd.validate_user_permissions()
        print("Validate user and permission test success.")
    except Exception as e:
        print("Validate user and permission test failed.")
        print(f"{traceback.format_exc()}, {e}")


if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))
    test_validate_user_permissions()
