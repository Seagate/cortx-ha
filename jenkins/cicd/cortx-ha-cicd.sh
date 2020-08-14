#!/bin/bash

set -x

BASE_DIR=$(realpath "$(dirname $0)/../../")

# Copy Backend files
TMPHA="${BASE_DIR}"/dist/tmp/cortx/ha
rm -rf "${TMPHA}"
mkdir -p "${TMPHA}"
cp -rs "$BASE_DIR"/ha/* "${TMPHA}"

mkdir -p /etc/cortx/ha/
cp -rf "${BASE_DIR}"/jenkins/cicd/etc/decision_monitor_conf.json /etc/cortx/ha/decision_monitor_conf.json
cp -rf "${BASE_DIR}"/jenkins/cicd/etc/database.json /etc/cortx/ha/database.json

# Perform unit test
python3 "${TMPHA}"/test/main.py "${TMPHA}"/test/unit

cortxha cleanup db --node srvnode-1 || exit 1

/usr/lib/ocf/resource.d/seagate/hw_comp_ra meta-data
