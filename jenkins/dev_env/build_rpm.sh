#!/usr/bin/env bash

BASE_DIR=$(realpath "$(dirname $0)")

source ${BASE_DIR}/conf/read_conf.sh $1

# Config if needed
[ -z ${config[THIRD_PARTY]} ] && { echo "error: THIRD_PARTY is empty"; exit 1; }
[ -z ${config[CORTX_ISO]} ] && { echo "error: CORTX_ISO is empty"; exit 1; }
[ -z ${config[GPG_CHECK]} ] && { echo "error: GPG_CHECK is empty"; exit 1; }
[ -z ${config[REPO_PATH]} ] && { echo "error: REPO_PATH is empty"; exit 1; }
[ -z ${config[USER]} ] && { echo "error: GID is empty"; exit 1; }

THIRD_PARTY=${config[THIRD_PARTY]}
CORTX_ISO=${config[CORTX_ISO]}
GPG_CHECK=${config[GPG_CHECK]}
REPO_PATH=${config[REPO_PATH]}
USER=${config[USER]}

echo "PATH: ${REPO_PATH}, USER: ${USER}"

mkdir -p /var/lib/ha_env

ls /var/lib/ha_env/ | grep yum_init || {
    # Configure cortx-py-utils
    yum-config-manager --add-repo ${THIRD_PARTY}
    yum-config-manager --add-repo ${CORTX_ISO}
    yum clean all
    rpm --import ${GPG_CHECK}
}

yum install -y gcc rpm-build python36 python36-pip python36-devel python36-setuptools openssl-devel libffi-devel  --nogpgcheck
yum group -y install "Development Tools" --nogpgcheck

python3 -m pip install -r https://raw.githubusercontent.com/Seagate/cortx-utils/main/py-utils/python_requirements.txt
python3 -m pip install -r https://raw.githubusercontent.com/Seagate/cortx-utils/main/py-utils/python_requirements.ext.txt
yum remove -y cortx-py-utils; yum install -y cortx-py-utils --nogpgcheck;

req_file=${REPO_PATH}/jenkins/pyinstaller/v2/requirements.txt
python3 -m pip install -r $req_file

[ ${USER} != "root" ] && {
    su - -c "/${REPO_PATH}/jenkins/build.sh -v 2" ${USER}
} || {
    su -c "/${REPO_PATH}/jenkins/build.sh -v 2"
}

echo "${REPO_PATH}/dist/rpmbuild/RPMS/x86_64/cortx-ha-2.0.0-*.x86_64.rpm"

yum remove -y cortx-ha
yum install -y ${REPO_PATH}/dist/rpmbuild/RPMS/x86_64/cortx-ha-2.0.0-*.x86_64.rpm

touch /var/lib/ha_env/yum_init