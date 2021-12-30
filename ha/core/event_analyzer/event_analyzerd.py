#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>. For any questions
# about this software or licensing, please email opensource@seagate.com or
# cortx-questions@seagate.com.



"""
 ****************************************************************************
  Description:       Entry point for the event analyzer daemon service
 ****************************************************************************
"""

import os
import time
import sys
import traceback

from cortx.utils.log import Log
from cortx.utils.conf_store.conf_store import Conf

from ha import const
from ha.core.config.config_manager import ConfigManager
from ha.core.system_health.system_health import SystemHealth
from ha.core.event_analyzer.watcher.watcher import Watcher
from ha.core.event_analyzer.filter.filter import ClusterResourceFilter
from ha.core.event_analyzer.parser.parser import ClusterResourceParser
from ha.core.event_analyzer.event_analyzer_exceptions import SubscriberException
from ha.const import _DELIM

class EventAnalyzerService:

    @staticmethod
    def get_class(class_path: str):
        """ get class object for the appropriate executor """
        module_path = ".".join(class_path.split('.')[:-1])
        class_name = class_path.split('.')[-1]
        __import__(module_path)
        module = sys.modules[module_path]
        return getattr(module, class_name)

    def init(self):
        """
        Initalize EventAnalyzerService
        """
        ConfigManager.init("event_analyzerd")
        Log.info("Event analyzer daemon initializations...")
        # Initialize system health
        confstore = ConfigManager.get_confstore()
        system_health = SystemHealth(confstore)
        # Initalize watcher
        self._watcher_list: dict = self._initalize_watcher(system_health)

    def _initalize_watcher(self, system_health: SystemHealth) -> dict:
        """
        Initalize watcher.

        Args:
            system_health (SystemHealth): Instance of systemhealth.

        Returns:
            dict: mapping of wather_type -> watcher_instance
        """
        watchers = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER{_DELIM}watcher")
        watcher_list: dict = {}
        for watcher in watchers:
            Log.info(f"Initializing watcher {watcher}....")
            event_filter_class = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER{_DELIM}watcher{_DELIM}{watcher}{_DELIM}event_filter")
            event_filter_instance = EventAnalyzerService.get_class(event_filter_class)()
            event_parser_class = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER{_DELIM}watcher{_DELIM}{watcher}{_DELIM}event_parser")
            event_parser_instance = EventAnalyzerService.get_class(event_parser_class)()
            watcher_list[watcher] = Watcher(
                consumer_id = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER{_DELIM}watcher{_DELIM}{watcher}{_DELIM}consumer_id"),
                message_type = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER{_DELIM}watcher{_DELIM}{watcher}{_DELIM}message_type"),
                consumer_group = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER{_DELIM}watcher{_DELIM}{watcher}{_DELIM}consumer_group"),
                event_filter = event_filter_instance,
                event_parser = event_parser_instance,
                subscriber = system_health
            )
        return watcher_list

    def run(self):
        """
        Run server
        """
        for watcher in self._watcher_list.keys():
            Log.info(f"Starting watcher {watcher} service for event analyzer.")
            self._watcher_list[watcher].start()
        Log.info(f"Running the daemon for HA event analyzer with PID {os.getpid()}...")
        while True:
            time.sleep(600)

# This will be instantiated from the fault_tolerance
class EventAnalyzer:
    """
    Analyzes an event, filter gets applied. Further it parses
    an alert to create health event object required for system
    health processing
    """
    def __init__(self, msg=None):
        '''init method'''
        ConfigManager.init('event_analyzer')
        self._confstore = ConfigManager.get_confstore()
        system_health = SystemHealth(self._confstore)
        self._cluster_resource_filter = ClusterResourceFilter()
        self._cluster_resource_parser = ClusterResourceParser(self._confstore)
        if self._cluster_resource_filter.filter_event(msg):
            try:
                health_event_list = self._cluster_resource_parser.parse_event(msg)
                if health_event_list is not None and isinstance(health_event_list, list):
                    for health_event in health_event_list:
                        Log.error(f'#################################################')
                        Log.error(f'Analyzer processing health event: {health_event}')
                        Log.error(f'#################################################')
                        system_health.process_event(health_event)
                Log.debug(f"health event can not be processed further")
            except Exception as e:
                Log.error(f"Failed to process event. Error: {e}")
                raise SubscriberException(f"Failed to process event {str(health_event)}. Error: {e}")

def main(argv):
    """
    Entry point for event analyzer daemon
    """
    # argv can be used later when config parameters are needed
    try:
        event_analyzer_service = EventAnalyzerService()
        event_analyzer_service.init()
        event_analyzer_service.run()
    except Exception as e:
        Log.error(f"Event analyzer service failed. Error: {e} {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
