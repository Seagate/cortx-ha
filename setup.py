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


import os
import sys
from setuptools import setup

# Get the installation dir and version from command line
install_dir = "/opt/seagate/cortx/ha/"    #default value
version = "2.0.0"
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
    long_description = rf.read()


def get_data_files() -> list:
    data_files = [(install_dir + '/meta-info', ['LICENSE', 'README.md'])]
    ignore_dirs = ['v1', 'iostack-ha']
    replace_dirs_in_dest = ('v2', 'common', 'mini_provisioner')
    conf_dir = 'conf'
    for root, _, file_names in os.walk(conf_dir):
        dest_root = root
        last_dir = root.split("/")[-1]
        if last_dir in ignore_dirs:
            continue
        if dest_root.endswith(replace_dirs_in_dest):
            dest_root = "/".join(dest_root.split("/")[:-1])
        # Repeat the check for double such sufixes
        if dest_root.endswith(replace_dirs_in_dest):
            dest_root = "/".join(dest_root.split("/")[:-1])
        dest_root = install_dir + '/' + dest_root
        dest_root = dest_root.replace('/common/', '/')
        dest_root = dest_root.replace('/v2/', '/')
        dest_root = dest_root.replace('/mini_provisioner/', '/')
        src_files = []
        for a_file in file_names:
            src_files.append(root+"/"+a_file)
        if len(src_files) != 0:
            data_files.append((dest_root, src_files))
    # See if same dest_root multiple times create a problem
    return data_files


def get_packages() -> list:
    ignore_list = ['pcswrap', 'test', '__pycache__']
    packages = ['ha']
    package_root = 'ha'
    for root, directories, _ in os.walk(package_root):
        for a_dir in directories:
            package = root + '/' + a_dir
            package = package.replace('/', '.')
            if len(set(package.split('.')).intersection(set(ignore_list))) == 0:
                packages.append(package)
    return packages


setup(name='cortx-ha',
      version=version,
      url='https://github.com/Seagate/cortx-ha',
      license='Seagate',
      author='Ajay Srivastava',
      author_email='ajay.srivastava@seagate.com',
      description='High availability for CORTX',
      package_dir={'ha': 'ha'},
      packages=get_packages(),
      package_data={
        'ha': ['py.typed'],
      },
      data_files = get_data_files(),
      long_description=long_description,
      zip_safe=False,
      python_requires='>=3.6')