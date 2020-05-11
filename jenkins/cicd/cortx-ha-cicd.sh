#!/bin/bash

BASE_DIR=$(realpath "$(dirname $0)/../../")

# Copy Backend files
TMPHA=${BASE_DIR}/dist/tmp/cortx/ha

# Perform unit test
python3 ${TMPHA}/test/main.py ${TMPHA}/test/unit

mkdir -p /etc/cortx/ha/
cp -rf ${BASE_DIR}/jenkins/cicd/decision_monitor_conf.json /etc/cortx/ha/decision_monitor_conf.json

/usr/lib/ocf/resource.d/seagate/hw_comp_ra meta-data
