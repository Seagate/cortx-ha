RES_AGENT="/usr/lib/ocf/resource.d/seagate"
HA_INSTALL_DIR=/opt/seagate/cortx/ha
BIN_DIR=${HA_INSTALL_DIR}/bin
mkdir -p ${BIN_DIR} ${RES_AGENT}

SITE_PACKAGES=`python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'`
HA_SETUP=${SITE_PACKAGES}/ha/setup/ha_setup.py
CLI_EXEC=${SITE_PACKAGES}/ha/cli/cortxha.py
DYNAMIC_RA=${SITE_PACKAGES}/ha/resource/dynamic_fid_service_ra.py
SRV_COUNTER_RA=${SITE_PACKAGES}/ha/resource/service_instances_counter.py
EVENT_ANALYZER=${SITE_PACKAGES}/ha/core/event_analyzer/event_analyzerd.py

chmod +x ${HA_SETUP}
ln -sf ${HA_SETUP} ${BIN_DIR}/ha_setup
ln -sf ${HA_SETUP} /usr/bin/ha_setup
ln -sf ${HA_SETUP} /usr/local/bin/ha_setup

chmod +x ${CLI_EXEC}
ln -sf ${CLI_EXEC} ${BIN_DIR}/cortx
ln -sf ${CLI_EXEC} /usr/bin/cortx
ln -sf ${CLI_EXEC} /usr/bin/cortxha

chmod +x ${DYNAMIC_RA}
ln -sf ${DYNAMIC_RA} ${BIN_DIR}/dynamic_fid_service_ra
ln -sf ${DYNAMIC_RA} /usr/bin/dynamic_fid_service_ra
ln -sf ${DYNAMIC_RA} $RES_AGENT/dynamic_fid_service_ra

chmod +x ${SRV_COUNTER_RA}
ln -sf ${SRV_COUNTER_RA} ${BIN_DIR}/service_instances_counter
ln -sf ${SRV_COUNTER_RA} /usr/bin/service_instances_counter
ln -sf ${SRV_COUNTER_RA} $RES_AGENT/service_instances_counter

chmod +x ${EVENT_ANALYZER}
ln -sf ${EVENT_ANALYZER} ${BIN_DIR}/event_analyzerd
ln -sf ${EVENT_ANALYZER} /usr/local/bin/event_analyzerd
ln -sf ${EVENT_ANALYZER} /usr/bin/event_analyzerd

chown -R root:root /opt/seagate/cortx/ha

exit 0