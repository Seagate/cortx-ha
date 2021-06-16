[ $1 -eq 1 ] && exit 0

RES_AGENT="/usr/lib/ocf/resource.d/seagate"
HA_INSTALL_DIR=/opt/seagate/cortx/ha
BIN_DIR=${HA_INSTALL_DIR}/bin

rm -f ${BIN_DIR}/ha_setup
rm -f /usr/bin/ha_setup
rm -f /usr/local/bin/ha_setup

rm -f ${BIN_DIR}/cortx
rm -f /usr/bin/cortx
rm -f /usr/bin/cortxha

rm -f ${BIN_DIR}/dynamic_fid_service_ra
rm -f /usr/bin/dynamic_fid_service_ra
rm -f $RES_AGENT/dynamic_fid_service_ra

rm -f ${BIN_DIR}/service_instances_counter
rm -f ${SRV_COUNTER_RA} /usr/bin/service_instances_counter
rm -f ${SRV_COUNTER_RA} $RES_AGENT/service_instances_counter

rm -f ${BIN_DIR}/event_analyzerd
rm -f /usr/local/bin/event_analyzerd
rm -f /usr/bin/event_analyzerd

rm -rf ${HA_INSTALL_DIR}

exit 0