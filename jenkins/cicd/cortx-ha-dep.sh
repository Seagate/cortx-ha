#!/bin/bash

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