#!/bin/bash

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


set -x

BASE_DIR=$(realpath "$(dirname $0)/../../")

# Copy Backend files
TMPHA="${BASE_DIR}"/dist/tmp/cortx/ha
rm -rf "${TMPHA}"
mkdir -p "${TMPHA}"
cp -rs "$BASE_DIR"/ha/* "${TMPHA}"

mkdir -p /etc/cortx/ha/ /var/log/seagate/cortx/ha
cp -rf "${BASE_DIR}"/jenkins/cicd/etc/* /etc/cortx/ha/

# Perform unit test
python3 "${TMPHA}"/test/main.py "${TMPHA}"/test/unit

/usr/lib/ocf/resource.d/seagate/hw_comp_ra meta-data
