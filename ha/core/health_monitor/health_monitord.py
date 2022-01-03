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
  Description:       Entry point for the health monitor daemon service
 ****************************************************************************
"""

import os
import time
import sys
import json
import traceback
import signal
import threading
from cortx.utils.log import Log
from cortx.utils.conf_store.conf_store import Conf
from ha.const import HA_GLOBAL_INDEX
from ha.const import _DELIM, CORTX_HA_WAIT_TIMEOUT
from ha.core.action_handler.action_factory import ActionFactory
from ha.core.health_monitor import const
from ha.core.system_health.model.health_event import HealthEvent
from ha.util.message_bus import MessageBus
from ha.util.message_bus import CONSUMER_STATUS
from ha.core.config.config_manager import ConfigManager
from ha.core.health_monitor.monitor_rules_manager import MonitorRulesManager

class HealthMonitorService:

    __instance = None

    @staticmethod
    def get_instance():
        """
        Static method to fetch the current instance.
        Performs initialization related to HealthMonitorService
        """
        if not HealthMonitorService.__instance:
            HealthMonitorService(singleton_check=True)
        return HealthMonitorService.__instance

    def __init__(self, singleton_check: bool = False):
        """
        Private Constructor. Make initialization work for HealthMonitorService

        Args:
            singleton_check (bool, optional): Create instance with get_instance. Defaults to False.
        """
        if singleton_check is False:
            raise Exception("Please use HealthMonitorService.get_instance() to fetch \
                             singleton instance of class")
        if HealthMonitorService.__instance is None:
            HealthMonitorService.__instance = self
        else:
            raise Exception("HealthMonitorService is singleton class, use HealthMonitorService.get_instance().")
        # initialize
        ConfigManager.init(const.HEALTH_MONITOR_LOG)
        # set sigterm handler
        signal.signal(signal.SIGTERM, self.set_sigterm)
        Log.info("Health Monitor daemon initializations...")
        self._stop = threading.Event()
        self._confstore = ConfigManager.get_confstore()
        self._rule_manager = MonitorRulesManager()
        self._event_consumer = self._get_consumer()

    def _get_consumer(self):
        """
        Return instace of message bus consumer.
        """
        consumer_id = Conf.get(HA_GLOBAL_INDEX, f"EVENT_MANAGER{_DELIM}consumer_id")
        consumer_group = Conf.get(HA_GLOBAL_INDEX, f"EVENT_MANAGER{_DELIM}consumer_group")
        message_type = Conf.get(HA_GLOBAL_INDEX, f"EVENT_MANAGER{_DELIM}message_type")
        MessageBus.init()
        return MessageBus.get_consumer(consumer_id=consumer_id, consumer_group=consumer_group,
                                        message_type=message_type, callback=self.process_event)

    def process_event(self, message: str) -> None:
        """
        Callback function to receive and process event.

        Args:
            message (str): event message.
        """
        try:
            event = json.loads(message.decode('utf-8'))
            health_event = HealthEvent.dict_to_object(event)
        except Exception as e:
            Log.error(f"Invalid format for event {message}, Error: {e}. Forcefully ack.")
            return CONSUMER_STATUS.SUCCESS
        Log.debug(f"Captured {message} for evaluating health monitor.")
        action_handler = None
        try:
            action_list = self._rule_manager.evaluate(health_event)
            if action_list:
                Log.info(f"Evaluated {health_event} with action {action_list}")
                action_handler = ActionFactory.get_action_handler(health_event, action_list)
                action_handler.act(health_event, action_list)
            return CONSUMER_STATUS.SUCCESS
        except Exception as e:
            Log.error(f"Failed to process {message} error: {e} {traceback.format_exc()}")
            return CONSUMER_STATUS.FAILED

    def set_sigterm(self, signum, frame):
        Log.info(f"Received SIGTERM: {signum}")
        Log.debug(f"Received signal: {signum} during execution of frame: {frame}")
        self.stop(flush=True)
        self._stop.set()

    def start(self):
        """
        Starts consumer daemon thread to receive the alters and perform action on it.
        """
        Log.info("Starting the daemon for Health Monitor...")
        self._event_consumer.start()
        Log.info(f"The daemon for Health Monitor with PID {os.getpid()} started successfully.")

    def stop(self, flush=False):
        """
        Stops consumer daemon thread.
        """
        self._event_consumer.stop(flush=flush)
        Log.info(f"The daemon for Health Monitor with PID {os.getpid()} stopped successfully.")

    def run(self):
        """
        Run health monitor server
        """
        Log.info("Running the Health Monitor server...")
        while not self._stop.is_set():
            self._stop.wait(timeout=CORTX_HA_WAIT_TIMEOUT)


def main(argv):
    """
    Entry point for Health Monitor daemon
    """
    # argv can be used later when config parameters are needed
    try:
        health_monitor = HealthMonitorService.get_instance()
        health_monitor.start()
        health_monitor.run()
    except Exception as e:
        Log.error(f"Health Monitor service failed. Error: {e} {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
