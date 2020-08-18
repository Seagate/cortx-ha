#!/bin/bash

set -x

BASE_DIR=$(realpath "$(dirname $0)/../../")

# Copy Backend files
TMPHA="${BASE_DIR}"/dist/tmp/cortx/ha
rm -rf "${TMPHA}"
mkdir -p "${TMPHA}"
cp -rs "$BASE_DIR"/ha/* "${TMPHA}"

mkdir -p /etc/cortx/ha/
cp -rf "${BASE_DIR}"/jenkins/cicd/etc/* /etc/cortx/ha/

# Perform unit test
python3 "${TMPHA}"/test/main.py "${TMPHA}"/test/unit

cortxha cleanup db --node srvnode-1 || exit 1

/usr/lib/ocf/resource.d/seagate/hw_comp_ra meta-data
