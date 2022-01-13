#!/usr/bin/env bash

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

BASE_DIR=$(realpath "$(dirname $0)")

source ${BASE_DIR}/conf/read_conf.sh $1

# Config if needed
[ -z $2 ] && STATE="multinode" || STATE=$2
[ -z ${config[THIRD_PARTY]} ] && { echo "error: THIRD_PARTY is empty"; exit 1; }
[ -z ${config[CORTX_ISO]} ] && { echo "error: CORTX_ISO is empty"; exit 1; }
[ -z ${config[GPG_CHECK]} ] && { echo "error: GPG_CHECK is empty"; exit 1; }

THIRD_PARTY=${config[THIRD_PARTY]}
CORTX_ISO=${config[CORTX_ISO]}
GPG_CHECK=${config[GPG_CHECK]}

mkdir -p /var/lib/ha_env

ls /var/lib/ha_env/ | grep yum_init || {
    # Configure cortx-py-utils
    yum-config-manager --add-repo ${THIRD_PARTY}
    yum-config-manager --add-repo ${CORTX_ISO}
    yum clean all
    rpm --import ${GPG_CHECK}
}

yum install -y gcc rpm-build python36 python36-pip python36-devel python36-setuptools openssl-devel libffi-devel python36-dbus  --nogpgcheck
yum group -y install "Development Tools" --nogpgcheck

# python3 -m pip install -r https://raw.githubusercontent.com/Seagate/cortx-utils/main/py-utils/python_requirements.txt
# python3 -m pip install -r https://raw.githubusercontent.com/Seagate/cortx-utils/main/py-utils/python_requirements.ext.txt
yum remove -y cortx-py-utils; yum install -y cortx-py-utils --nogpgcheck;

# Update provision conf
[ $STATE == "singlenode" ] && {
    cp -rf ${BASE_DIR}/conf/example_config_singlenode.json /root/example_config.json
    [ -z ${config[LOCAL_NODE]} ] && { echo "error: LOCAL_NODE is empty"; exit 1; }
    LOCAL_NODE=${config[LOCAL_NODE]}
    sed -i -e "s|<NODE1>|${LOCAL_NODE}|g" /root/example_config.json
} || {
    cp -rf ${BASE_DIR}/conf/example_config_multinode.json /root/example_config.json
    [ -z ${config[NODE1]} ] && { echo "error: NODE1 is empty"; exit 1; }
    [ -z ${config[NODE2]} ] && { echo "error: NODE2 is empty"; exit 1; }
    [ -z ${config[NODE3]} ] && { echo "error: NODE3 is empty"; exit 1; }
    NODE1=${config[NODE1]}
    NODE2=${config[NODE2]}
    NODE3=${config[NODE3]}
    sed -i -e "s|<NODE1>|${NODE1}|g" /root/example_config.json
    sed -i -e "s|<NODE2>|${NODE2}|g" /root/example_config.json
    sed -i -e "s|<NODE3>|${NODE3}|g" /root/example_config.json
}

/opt/seagate/cortx/utils/bin/utils_setup post_install --config 'json:///root/example_config.json'
/opt/seagate/cortx/utils/bin/utils_setup config --config 'json:///root/example_config.json'
/opt/seagate/cortx/utils/bin/utils_setup init --config 'json:///root/example_config.json' 2> /dev/null
touch /var/lib/ha_env/yum_init
