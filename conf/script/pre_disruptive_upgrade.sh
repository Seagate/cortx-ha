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

set -eu -o pipefail

BACKUP_SOURCE_DIR=/etc/cortx/ha
BACKUP_DEST_DIR=/opt/seagate/cortx/ha_conf_backup

# Take the backup of configuration files
cp -r $BACKUP_SOURCE_DIR $BACKUP_DEST_DIR

# Keep cluster in maintainence mode
pcs property set maintenance-mode=true

# Remove all the resources from the cluster

# Get only the name of the resource
resource_list=( `crm_resource --list-raw` )

# Remove each one by one
for resource in "${resource_list[@]}"
do
    echo Deleteing the resource: "${resource}"
    pcs resource delete "${resource}" --force
done


