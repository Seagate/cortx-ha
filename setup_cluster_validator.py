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


import sys
from setuptools import setup

for argument in sys.argv:
    if argument.startswith("--install-dir"):
        install_dir = argument.split("=")[1]
        # remove it. setup doesn't need it.
        sys.argv.remove(argument)
for argument in sys.argv:
    if argument.startswith("--version"):
        version = argument.split("=")[1]
        # remove it. setup doesn't need it.
        sys.argv.remove(argument)

with open('README.md', 'r') as rf:
    long_description = '''
Validation library for HA integration tests. Supposed to be used by HA mini-provisioner during Test phase.
'''

def get_data_files() -> list:
    return []


def get_packages() -> list:
    return [ "ha.setup.cluster_validator" ]


def get_install_requirements() -> list:
    return []


setup(name='cortx-validator',
      version='2.0.0',
      url='https://github.com/Seagate/cortx-ha',
      license='Seagate',
      author='Ajay Srivastava',
      author_email='ajay.srivastava@seagate.com',
      description='High availability for CORTX',
      package_dir={'ha': 'ha'},
      packages=get_packages(),
      package_data={
        'ha.setup.cluster_validator': ['py.typed'],
      },
      data_files = get_data_files(),
      long_description=long_description,
      zip_safe=False,
      python_requires='>=3.6',
      install_requires=get_install_requirements())
