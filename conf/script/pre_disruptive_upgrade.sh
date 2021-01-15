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
consul=/usr/bin/consul
HARE_DIR=/var/lib/hare

backup_consul(){

    echo "Taking the backup of consul"
    consul_kv_dump=$HARE_DIR/consul-kv-dump.json
    if [[ -f $consul_kv_dump ]]; then
        cat $consul_kv_dump | xz > ${consul_kv_dump%.json}-$(date '+%Y%m%d%H%M%S').json.xz
    fi
    $consul kv export > $consul_kv_dump

}

backup_conf(){

    echo "Taking the backup of ha conf directory"

    [ -d $BACKUP_DEST_DIR ]  && {
        rm -rf $BACKUP_DEST_DIR
    }

    mkdir -p $BACKUP_DEST_DIR

    # Take the backup of configuration files
    cp -r $BACKUP_SOURCE_DIR $BACKUP_DEST_DIR
}

cluster_standby_mode(){

    echo "standby mode ON"

    standby_mode=$(crm_standby -G  | awk '{print $3}' | cut -d '=' -f 2)

    if [ "$standby_mode" == "on" ]
    then
        echo "cluster is already in a standby mode"
    else
        # Keep cluster (nodes and resources) on standby mode
        /usr/sbin/pcs node standby --all --wait=10
        [ $? == 0 ] || {

            echo "some problem occured to keep cluster in standby mode, Hence exiting"
            exit 1
        }
    fi
}

delete_resources(){

    echo "deleting the resources from the cluster"

    resources=$(/usr/sbin/pcs resource show)
    if [ "$resources" == "NO resources configured" ];
    then
        echo "No resources are configured. Hence, skipping this"
    else
        # Get only the name of the resource
        resource_list=$(/usr/sbin/crm_resource --list-raw)

        resource_list=( $resource_list )

        # Remove each one by one
        for resource in "${resource_list[@]}"
        do
            echo "Deleteing the resource: ${resource}"
            /usr/sbin/pcs resource delete "${resource}" --force
        done
    fi
}


while [ $# -gt 0 ]; do
    case $1 in
        -cb )
            backup_consul
            ;;
        * )
            ;;
    esac
    shift 1
done

backup_conf

cluster_standby_mode

delete_resources
