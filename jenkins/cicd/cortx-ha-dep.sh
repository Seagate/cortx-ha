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

set -e -o pipefail

BASE_DIR=$(realpath "$(dirname $0)/../../")
HA1="1"
HA2="2"

usage() {
    echo """
For Developer to create venv
    $ ./cortx-ha-dep.sh [-v <cortx-ha major version>] [-e dev] [-t <github-token>]
For Production
    $ ./cortx-ha-dep.sh [-v <cortx-ha major version>]
"""
}

while getopts ":h:v:e:t:" o; do
    case "${o}" in
        h)
            usage ; exit 0
            ;;
        v)
            VERSION=${OPTARG}
            ;;
        e)
            DEV=${OPTARG}
            ;;
        t)
            TOKEN=${OPTARG}
            ;;
        *)
            usage ; exit 1
            ;;
    esac
done

# Check Dev
[ -z "$DEV" ] && DEV="false"
[ -z "$VERSION" ] && VERSION="${HA2}"

if [ "$DEV" == "false" ]; then
    set -x
    yum erase eos-py-utils -y && yum install cortx-py-utils -y
else
    mkdir -p "${BASE_DIR}"/dist

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
    python3 -m pip install --upgrade pip
    python3 -m pip install git+https://"${TOKEN}"@github.com/Seagate/cortx-utils.git#subdirectory=py-utils
    deactivate

    # TODO: add python path

    echo "Execute:"
    echo "**************************************"
    echo "source ${VENV}/bin/activate"
    echo "**************************************"
fi
