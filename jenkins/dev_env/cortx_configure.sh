#!/usr/bin/env bash

BASE_DIR=$(realpath "$(dirname $0)")

source ${BASE_DIR}/conf/read_conf.sh $1

# Config if needed
[ -z ${config[THIRD_PARTY]} ] && { echo "error: THIRD_PARTY is empty"; exit 1; }
[ -z ${config[CORTX_ISO]} ] && { echo "error: CORTX_ISO is empty"; exit 1; }
[ -z ${config[GPG_CHECK]} ] && { echo "error: GPG_CHECK is empty"; exit 1; }
[ -z ${config[LOCAL_NODE]} ] && { echo "error: LOCAL_NODE is empty"; exit 1; }
[ -z ${config[MACHINE_ID1]} ] && { echo "error: MACHINE_ID1 is empty"; exit 1; }
[ -z ${config[MACHINE_ID2]} ] && { echo "error: MACHINE_ID2 is empty"; exit 1; }
[ -z ${config[MACHINE_ID3]} ] && { echo "error: MACHINE_ID3 is empty"; exit 1; }
[ -z ${config[NODE1]} ] && { echo "error: NODE1 is empty"; exit 1; }
[ -z ${config[NODE2]} ] && { echo "error: NODE2 is empty"; exit 1; }
[ -z ${config[NODE3]} ] && { echo "error: NODE3 is empty"; exit 1; }

THIRD_PARTY=${config[THIRD_PARTY]}
CORTX_ISO=${config[CORTX_ISO]}
GPG_CHECK=${config[GPG_CHECK]}
LOCAL_NODE=${config[LOCAL_NODE]}
MACHINE_ID1=${config[MACHINE_ID1]}
MACHINE_ID2=${config[MACHINE_ID2]}
MACHINE_ID3=${config[MACHINE_ID3]}
NODE1=${config[NODE1]}
NODE2=${config[NODE2]}
NODE3=${config[NODE3]}

cd ${BASE_DIR}
#############################################

[ $LOCAL_NODE == "--clean" ] && {
    echo "Cleaning Yum"
    rm -rf /etc/yum.repos.d/cortx-*
    yum clean all
    exit 0
}

DIR=/root/service
mkdir -p ${DIR}

########### Configure cortx-py-utils #########

yum-config-manager --add-repo ${THIRD_PARTY}
yum-config-manager --add-repo ${CORTX_ISO}
yum clean all
rpm --import ${GPG_CHECK}

yum install -y gcc rpm-build python36 python36-pip python36-devel python36-setuptools openssl-devel libffi-devel
python3 -m pip install -r https://raw.githubusercontent.com/Seagate/cortx-utils/main/py-utils/python_requirements.txt
python3 -m pip install -r https://raw.githubusercontent.com/Seagate/cortx-utils/main/py-utils/python_requirements.ext.txt
yum remove -y cortx-py-utils; yum install -y cortx-py-utils --nogpgcheck;

########### Configure other component #########

DUMMY_SERVICE=${BASE_DIR}/cortx_component/dummy_service.service
DUMMY_SCRIPT=${BASE_DIR}/cortx_component/dummy_script.sh

# s3backgroundproducer
SERVICE="s3backgroundproducer"
cp -rf ${DUMMY_SCRIPT} ${DIR}/${SERVICE}
chmod +x  ${DIR}/${SERVICE}
cp -rf ${DUMMY_SERVICE} /usr/lib/systemd/system/${SERVICE}.service
sed -i -e "s|<service>|${SERVICE}|g" /usr/lib/systemd/system/${SERVICE}.service

# sspl-ll
SERVICE="sspl-ll"
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
cp -rf ${BASE_DIR}/conf/example_config.json /root/
sed -i -e "s|<MACHINE_ID1>|${MACHINE_ID1}|g" /root/example_config.json
sed -i -e "s|<MACHINE_ID2>|${MACHINE_ID2}|g" /root/example_config.json
sed -i -e "s|<MACHINE_ID3>|${MACHINE_ID3}|g" /root/example_config.json
sed -i -e "s|<NODE1>|${NODE1}|g" /root/example_config.json
sed -i -e "s|<NODE2>|${NODE2}|g" /root/example_config.json
sed -i -e "s|<NODE3>|${NODE3}|g" /root/example_config.json

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
