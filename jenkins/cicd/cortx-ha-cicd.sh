#!/bin/bash

set -x

BASE_DIR=$(realpath "$(dirname $0)/../../")

mkdir -p /etc/cortx/ha/
cp -rf ${BASE_DIR}/jenkins/cicd/etc/decision_monitor_conf.json /etc/cortx/ha/decision_monitor_conf.json
cp -rf ${BASE_DIR}/jenkins/cicd/etc/database.json /etc/cortx/ha/database.json

cortxha cleanup db --node srvnode-1 || exit 1

/usr/lib/ocf/resource.d/seagate/hw_comp_ra meta-data
