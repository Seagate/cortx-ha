#!/bin/bash

HA_INSTALL_DIR=/opt/seagate/cortx/ha
BIN_DIR=${HA_INSTALL_DIR}/bin
mkdir -p ${BIN_DIR} ${RES_AGENT}

SITE_PACKAGES=$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
HA_SETUP=${SITE_PACKAGES}/ha/k8s_setup/ha_setup.py
HA_ENTRYPOINT=${SITE_PACKAGES}/ha/k8s_setup/ha_start.py
CLI_EXEC=${SITE_PACKAGES}/ha/cli/cortxha.py
EVENT_ANALYZER=${SITE_PACKAGES}/ha/core/event_analyzer/event_analyzerd.py

chmod +x "${HA_SETUP}"
chmod +x "${HA_ENTRYPOINT}"
ln -sf "${HA_SETUP}" ${BIN_DIR}/ha_setup
ln -sf "${HA_ENTRYPOINT}" ${BIN_DIR}/ha_start
ln -sf "${HA_SETUP}" /usr/bin/ha_setup
ln -sf "${HA_SETUP}" /usr/local/bin/ha_setup

chmod +x "${CLI_EXEC}"
ln -sf "${CLI_EXEC}" ${BIN_DIR}/cortx
ln -sf "${CLI_EXEC}" /usr/bin/cortx
ln -sf "${CLI_EXEC}" /usr/bin/cortxha


chmod +x "${EVENT_ANALYZER}"
ln -sf "${EVENT_ANALYZER}" ${BIN_DIR}/event_analyzerd
ln -sf "${EVENT_ANALYZER}" /usr/local/bin/event_analyzerd
ln -sf "${EVENT_ANALYZER}" /usr/bin/event_analyzerd

chown -R root:root /opt/seagate/cortx/ha
exit 0
