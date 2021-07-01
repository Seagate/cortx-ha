#!/bin/bash

BASE_DIR=$(realpath "$(dirname $0)")
DEV_CONF=$1

typeset -A config # init array
config=( # set default values in config array
    [NODE1]="srvnode-1"
    [NODE2]="srvnode-2"
    [NODE3]="srvnode-3"
)

while read line
do
    if echo $line | grep -F = &>/dev/null
    then
        line=$(echo "$line" | cut -d '#' -f 1)
        varname=$(echo "$line" | cut -d '=' -f 1)
        config[$varname]=$(echo "$line" | cut -d '=' -f 2-)
    fi
done < ${DEV_CONF}

#echo ${config[THIRD_PARTY]}
#echo ${config[CORTX_ISO]}
#echo ${config[GPG_CHECK]}
#echo ${config[NODE1]}
#echo ${config[NODE2]}
#echo ${config[NODE3]}
