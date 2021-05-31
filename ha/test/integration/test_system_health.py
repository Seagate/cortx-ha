#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

import os
import sys
import pathlib
import json

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))
from ha import const
from ha.core.config.config_manager import ConfigManager
from ha.core.system_health.system_health import SystemHealth
from ha.core.system_health.model.health_event import HealthEvent

def main(argv: dict):
    # TODO: Add test cases.
    pass

if __name__ == '__main__':
    # TODO: Import and use config_manager.py
    Conf.init(delim='.')
    Conf.load(const.HA_GLOBAL_INDEX, f"yaml://{const.SOURCE_CONFIG_FILE}")
    log_path = Conf.get(const.HA_GLOBAL_INDEX, "LOG.path")
    log_level = Conf.get(const.HA_GLOBAL_INDEX, "LOG.level")
    Log.init(service_name='ha_system_health', log_path=log_path, level=log_level)

    try:
        store = ConfigManager.get_confstore()
        health = SystemHealth(store)
        """
        Test case 1
        """
        event = HealthEvent("event_id", "fault", "severity", "1", "1", "e766bd52-c19c-45b6-9c91-663fd8203c2e", "storage-set-1",
                            "2", "srvnode-1.mgmt.public", "node", "16215009572", "iem", "Description")
        health.process_event(event)
        node_info = health.get_node_status(node_id="2")
        node_info_dict = json.loads(node_info)
        node_status = node_info_dict['events'][0]['status']
        if node_status != const.NODE_STATUSES.CLUSTER_OFFLINE.value:
            Log.error("Test case 1 failed : node status must be 'offline' for event 'fault'")

        """
        Test case 2
        """
        event = HealthEvent("event_id", "fault_resolved", "severity", "1", "1", "e766bd52-c19c-45b6-9c91-663fd8203c2e", "storage-set-1",
                            "2", "srvnode-1.mgmt.public", "node", "16215009572", "iem", "Description")
        health.process_event(event)
        node_info = health.get_node_status(node_id="2")
        node_info_dict = json.loads(node_info)
        node_status = node_info_dict['events'][0]['status']
        if node_status != const.NODE_STATUSES.ONLINE.value:
            Log.error("Test case 2 failed : node status must be 'online' for event 'fault_resolved'")

    except Exception as e:
            Log.error(f"Process event test failed : {e}")
    sys.exit(main(sys.argv))