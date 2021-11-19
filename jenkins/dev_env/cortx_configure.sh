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

[ -z $1 ] && {
    echo "Config file is missing"
    exit 1
}

[ -z $2 ] && {
    echo """
/usr/bin/env bash -x cortx_configure.sh /root/dev.conf singlenode
or
/usr/bin/env bash -x cortx_configure.sh /root/dev.conf multinode
"""
exit 0
}

BASE_DIR=$(realpath "$(dirname $0)")

source ${BASE_DIR}/conf/read_conf.sh $1

[ -z $2 ] && STATE="multinode" || STATE=$2

# Config if needed
[ -z ${config[THIRD_PARTY]} ] && { echo "error: THIRD_PARTY is empty"; exit 1; }
[ -z ${config[CORTX_ISO]} ] && { echo "error: CORTX_ISO is empty"; exit 1; }
[ -z ${config[GPG_CHECK]} ] && { echo "error: GPG_CHECK is empty"; exit 1; }
[ -z ${config[LOCAL_NODE]} ] && { echo "error: LOCAL_NODE is empty"; exit 1; }

THIRD_PARTY=${config[THIRD_PARTY]}
CORTX_ISO=${config[CORTX_ISO]}
GPG_CHECK=${config[GPG_CHECK]}
LOCAL_NODE=${config[LOCAL_NODE]}

[ $STATE == "singlenode" ] && {
    [ -z ${config[MACHINE_ID1]} ] && { echo "error: MACHINE_ID1 is empty"; exit 1; }
    [ -z ${config[NODE1]} ] && { echo "error: NODE1 is empty"; exit 1; }
    MACHINE_ID1=${config[MACHINE_ID1]}
    NODE1=${config[NODE1]}
    ENV_TYPE=${config[ENV_TYPE]}
    BMC_IP_1=${config[BMC_IP_1]}
    BMC_USER_1=${config[BMC_USER_1]}
    BMC_SECRET_1=${config[BMC_SECRET_1]}
} || {
    [ -z ${config[MACHINE_ID1]} ] && { echo "error: MACHINE_ID1 is empty"; exit 1; }
    [ -z ${config[MACHINE_ID2]} ] && { echo "error: MACHINE_ID2 is empty"; exit 1; }
    [ -z ${config[MACHINE_ID3]} ] && { echo "error: MACHINE_ID3 is empty"; exit 1; }
    [ -z ${config[NODE1]} ] && { echo "error: NODE1 is empty"; exit 1; }
    [ -z ${config[NODE2]} ] && { echo "error: NODE2 is empty"; exit 1; }
    [ -z ${config[NODE3]} ] && { echo "error: NODE3 is empty"; exit 1; }
    MACHINE_ID1=${config[MACHINE_ID1]}
    MACHINE_ID2=${config[MACHINE_ID2]}
    MACHINE_ID3=${config[MACHINE_ID3]}
    NODE1=${config[NODE1]}
    NODE2=${config[NODE2]}
    NODE3=${config[NODE3]}
    ENV_TYPE=${config[ENV_TYPE]}
    BMC_IP_1=${config[BMC_IP_1]}
    BMC_USER_1=${config[BMC_USER_1]}
    BMC_SECRET_1=${config[BMC_SECRET_1]}
    BMC_IP_2=${config[BMC_IP_2]}
    BMC_USER_2=${config[BMC_USER_2]}
    BMC_SECRET_2=${config[BMC_SECRET_2]}
    BMC_IP_3=${config[BMC_IP_3]}
    BMC_USER_3=${config[BMC_USER_3]}
    BMC_SECRET_3=${config[BMC_SECRET_3]}
}

cd ${BASE_DIR}
#############################################

DIR=/root/service
mkdir -p ${DIR}

ls /var/lib/ha_env/ | grep yum_init || {
    echo "Please complete preqs."
}

########### Configure other component #########

DUMMY_SERVICE=${BASE_DIR}/cortx_component/dummy_service.service
DUMMY_SCRIPT=${BASE_DIR}/cortx_component/dummy_script.sh

# s3backgroundproducer
SERVICE="s3backgroundproducer"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# sspl
SERVICE="sspl"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# kibana
SERVICE="kibana"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# csm_agent
SERVICE="csm_agent"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# csm_web
SERVICE="csm_web"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# hare-consul-agent
SERVICE="hare-consul-agent"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# hare-hax
SERVICE="hare-hax"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# haproxy
SERVICE="haproxy"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# s3backgroundconsumer
SERVICE="s3backgroundconsumer"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# s3authserver
SERVICE="s3authserver"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# motr-free-space-monitor
SERVICE="motr-free-space-monitor"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# s3server
SERVICE="s3server"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}@.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}@.service

# m0d
SERVICE="m0d"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}@.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}@.service

systemctl daemon-reload

# Update provision conf
[ $STATE == "singlenode" ] && {
    cp -rf ${BASE_DIR}/conf/example_config_singlenode.json /root/example_config.json
    sed -i -e "s|<MACHINE_ID1>|${MACHINE_ID1}|g" /root/example_config.json
    sed -i -e "s|<NODE1>|${NODE1}|g" /root/example_config.json
    sed -i -e "s|<ENV_TYPE>|${ENV_TYPE}|g" /root/example_config.json
    sed -i -e "s|<BMC_IP_1>|${BMC_IP_1}|g" /root/example_config.json
    sed -i -e "s|<BMC_USER_1>|${BMC_USER_1}|g" /root/example_config.json
    sed -i -e "s|<BMC_SECRET_1>|${BMC_SECRET_1}|g" /root/example_config.json
} || {
    cp -rf ${BASE_DIR}/conf/example_config_multinode.json /root/example_config.json
    sed -i -e "s|<MACHINE_ID1>|${MACHINE_ID1}|g" /root/example_config.json
    sed -i -e "s|<MACHINE_ID2>|${MACHINE_ID2}|g" /root/example_config.json
    sed -i -e "s|<MACHINE_ID3>|${MACHINE_ID3}|g" /root/example_config.json
    sed -i -e "s|<NODE1>|${NODE1}|g" /root/example_config.json
    sed -i -e "s|<NODE2>|${NODE2}|g" /root/example_config.json
    sed -i -e "s|<NODE3>|${NODE3}|g" /root/example_config.json
    sed -i -e "s|<ENV_TYPE>|${ENV_TYPE}|g" /root/example_config.json
    sed -i -e "s|<BMC_IP_1>|${BMC_IP_1}|g" /root/example_config.json
    sed -i -e "s|<BMC_USER_1>|${BMC_USER_1}|g" /root/example_config.json
    sed -i -e "s|<BMC_SECRET_1>|${BMC_SECRET_1}|g" /root/example_config.json
    sed -i -e "s|<BMC_IP_2>|${BMC_IP_2}|g" /root/example_config.json
    sed -i -e "s|<BMC_USER_2>|${BMC_USER_2}|g" /root/example_config.json
    sed -i -e "s|<BMC_SECRET_2>|${BMC_SECRET_2}|g" /root/example_config.json
    sed -i -e "s|<BMC_IP_3>|${BMC_IP_3}|g" /root/example_config.json
    sed -i -e "s|<BMC_USER_3>|${BMC_USER_3}|g" /root/example_config.json
    sed -i -e "s|<BMC_SECRET_3>|${BMC_SECRET_3}|g" /root/example_config.json
}

# Update hctl interface
cp -rf ${BASE_DIR}/cortx_component/hctl_cli /usr/bin/hctl
chmod +x /usr/bin/hctl

# Pacemaker basic
yum -y install corosync pacemaker pcs  --nogpgcheck
systemctl enable pcsd
systemctl enable corosync
systemctl enable pacemaker
echo "Seagate" | passwd --stdin hacluster
systemctl start pcsd
