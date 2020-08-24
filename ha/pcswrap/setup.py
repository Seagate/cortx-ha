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

import os
from setuptools import setup, find_packages


def get_version():
    ver = os.environ.get('PCS_CLIENT_VERSION')
    if ver:
        return ver
    with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
        return f.read().rstrip('\n')


setup(
    name='pcswrap',
    version=get_version(),
    packages=find_packages(),
    setup_requires=['flake8', 'mypy', 'pkgconfig'],
    entry_points={'console_scripts': ['pcswrap=pcswrap.client:main']},
)
