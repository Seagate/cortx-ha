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

from ha.core.error import SetupError

# TODO: Move all error.py setup related error to setup_error.py

class AlertConfigError(SetupError):
    """Failed to configure alert"""

class ConfigureStonithResourceError(SetupError):
    '''
    Exception to indicate any failure happened during stonith resource creation.
    '''

    def __init__(self, desc=None):
        """
        Handle Configure Stonith Resource Error.
        """
        _desc = "Stonith configuration failed." if desc is None else desc
        super(ConfigureStonithResourceError, self).__init__(desc=_desc)