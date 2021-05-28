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

    # To test update health API
    store = ConfigManager._get_confstore()
    health = SystemHealth(store)
    event = HealthEvent("event_id", "fault", "severity", "site_id", "rack_id", "cluster_id", "storageset_id",
                        "node_5", "srvnode-1.mgmt.public", "node", "16215009572", "iem", "Description")
    health.process_event(event)

    # To test querying the node health API
    node_status = health.get_node_status(node_id="node_5")
    sys.exit(main(sys.argv))