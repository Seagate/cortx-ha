#!/bin/bash

[ "$1" -eq 1 ] && exit 0

HA_INSTALL_DIR=/opt/seagate/cortx/ha
BIN_DIR=${HA_INSTALL_DIR}/bin

rm -f ${BIN_DIR}/ha_setup
rm -f /usr/bin/ha_setup
rm -f /usr/local/bin/ha_setup

rm -f ${BIN_DIR}/cortx
rm -f /usr/bin/cortx
rm -f /usr/bin/cortxha

rm -f ${BIN_DIR}/event_analyzerd
rm -f /usr/local/bin/event_analyzerd
rm -f /usr/bin/event_analyzerd

rm -rf ${HA_INSTALL_DIR}

exit 0
