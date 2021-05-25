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

class EventAnalyserService:

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
        Initalize EventAnalyserService
        """
        ConfigManager.init("event_analyzerd")
        Log.info("Event analyzer daemon initializations...")
        # Initialize system health
        confstore = ConfigManager.get_confstore()
        system_health = SystemHealth(confstore)
        # Initalize watcher
        watchers = Conf.get(const.HA_GLOBAL_INDEX, "EVENT_ANALYZER.watcher")
        self._watcher_list: dict = {}
        for watcher in watchers:
            Log.info(f"Initializing watcher {watcher}....")
            event_filter_class = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER.watcher.{watcher}.event_filter")
            event_filter_instance = EventAnalyserService.get_class(event_filter_class)()
            event_parser_class = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER.watcher.{watcher}.event_parser")
            event_parser_instance = EventAnalyserService.get_class(event_parser_class)()
            self._watcher_list[watcher] = Watcher(
                consumer_id = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER.watcher.{watcher}.consumer_id"),
                message_type = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER.watcher.{watcher}.message_type"),
                consumer_group = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER.watcher.{watcher}.consumer_group"),
                event_filter = event_filter_instance,
                event_parser = event_parser_instance,
                subscriber = system_health
            )

    def run(self):
        """
        Run server
        """
        for watcher in self._watcher_list.keys():
            Log.info(f"Starting watcher {watcher} service for event analyser.")
            self._watcher_list[watcher].start()
        Log.info(f"Running the daemon for HA event analyzer with PID {os.getpid()}...")
        # Check if need to handle signal
        while True:
            Log.info("Running the daemon for HA event analyzer")
            time.sleep(600)

def main(argv):
    """
    Entry point for event analyzer daemon
    """
    # argv can be used later when config parameters are needed
    try:
        event_analyser_service = EventAnalyserService()
        event_analyser_service.init()
        event_analyser_service.run()
    except Exception as e:
        Log.error(f"Event analyser service failed. Error: {e} {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
