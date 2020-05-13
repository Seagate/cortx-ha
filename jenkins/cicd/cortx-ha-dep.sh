#!/bin/bash

BASE_DIR=$(realpath "$(dirname $0)/../../")

req_file=${BASE_DIR}/jenkins/pyinstaller/requirment.txt
python3 -m pip install --user -r $req_file > /dev/null || {
    echo "Unable to install package from $req_file"; exit 1;
};


