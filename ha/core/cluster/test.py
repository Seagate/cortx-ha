import os
import sys
import pathlib
import re

sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from ha import const
from ha.core.cluster.cluster_manager import CortxClusterManager
from ha.core.system_health.const import CLUSTER_ELEMENTS
from ha.core.system_health.system_health import SystemHealth
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.config.config_manager import ConfigManager

if __name__ == '__main__':
    #Conf.init(delim='.')
    #Conf.load(const.HA_GLOBAL_INDEX, f"yaml://{const.SOURCE_CONFIG_FILE}")
    #log_path = Conf.get(const.HA_GLOBAL_INDEX, "LOG.path")
    #log_level = Conf.get(const.HA_GLOBAL_INDEX, "LOG.level")
    #Log.init(service_name='test', log_path=log_path, level=log_level)

    #store = ConfigManager.get_confstore()
    #sh = SystemHealth(store)
    #he = HealthEvent("12345", "fault", "severity", "rack_1", "site_1", "cluster_1", "storageset_1",
    #                        "rack_1", "abcd.com", "rack", "16215009572", "rack_1", "fun")
    #sh.process_event(he)
    manager = CortxClusterManager()
    health = manager.get_system_health(element = CLUSTER_ELEMENTS.NODE.value, depth = 1)#, id = 'node_5')
    print(health)