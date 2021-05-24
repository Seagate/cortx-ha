#!/usr/bin/python3.6

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

import time
import sys

from cortx.utils.log import Log
from cortx.utils.conf_store.conf_store import Conf

from ha import const
from ha.core.config.config_manager import ConfigManager
from ha.core.system_health.system_health import SystemHealth
from ha.core.event_analyzer.watcher.watcher import Watcher

# TODO: convert event_analyser.service to event_analyser@consumer_id.service for scaling
class EventAnalyserService:

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
            self._watcher_list[watcher] = Watcher(
                consumer_id = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER.watcher.{watcher}.consumer_id"),
                message_type = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER.watcher.{watcher}.message_type"),
                consumer_group = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER.watcher.{watcher}.consumer_group"),
                event_filter = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER.watcher.{watcher}.event_filter"),
                event_parser = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_ANALYZER.watcher.{watcher}.event_parser"),
                subscriber = system_health
            )

    def run(self):
        """
        Run server
        """
        for watcher in self._watcher_list.keys():
            Log.info(f"Starting watcher {watcher} service for event analyser.")
            self._watcher_list[watcher].start()
        Log.info("Running the daemon for HA event analyzer...")
        while True:
            #TODO remove this message and sleep once appropriate code is added here
            Log.info("Running the daemon for HA event analyzer")
            time.sleep(600)

def main(argv):
    """
    Entry point for event analyzer daemon
    """
    # argv can be used later when config parameters are needed
    event_analyser_service = EventAnalyserService()
    event_analyser_service.init()
    event_analyser_service.run()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
