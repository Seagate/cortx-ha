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
 ****************************************************************************
 Description:       resource_agent resource agent
 ****************************************************************************
"""

import os
import pathlib
import sys
import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..'))
    path = sys.argv[1] if len(sys.argv) == 2 else os.path.join(os.path.dirname(pathlib.Path(__file__)), '.')
    test_suite = loader.discover(path)
    runner = unittest.TextTestRunner()
    runner.run(test_suite)
