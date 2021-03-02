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


BASE_DIR=$(realpath "$(dirname $0)/../../")

usage() {
    echo """
For Developer to create venv
    $ ./cortx-ha-dep.sh dev <github-token>
For Production
    $ ./cortx-ha-dep.sh
"""
}

# Check Dev
DEV=$1
[ -z "$DEV" ] && DEV=false

if [ "$DEV" == false ]; then
    set -x
    yum erase eos-py-utils -y && yum install cortx-py-utils -y
    req_file=${BASE_DIR}/jenkins/pyinstaller/requirements.txt
    python3 -m pip install -r $req_file > /dev/null || {
        echo "Unable to install package from $req_file"; exit 1;
    };
else
    mkdir -p "${BASE_DIR}"/dist

    TOKEN=$2
    [ -z "$TOKEN" ] && {
        usage; exit 1
    }

    VENV="${BASE_DIR}/dist/venv"
    if [ -d "${VENV}/bin" ]; then
        echo "Using existing Python virtual environment..."
    else
        echo "Setting up Python 3.6 virtual environment..."
        python3.6 -m venv "${VENV}"
    fi
    source "${VENV}/bin/activate"

    echo "Installing python packages..."
    pip install --upgrade pip
    pip install git+https://"${TOKEN}"@github.com/Seagate/cortx-py-utils.git
    req_file=${BASE_DIR}/jenkins/pyinstaller/requirements.txt
    pip install -r "$req_file" || {
        echo "Unable to install package from $req_file"; exit 1;
    };
    deavtivate

    echo "Execute:"
    echo "**************************************"
    echo "source ${VENV}/bin/activate"
    echo "**************************************"
fi
