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

import os
import sys
import pathlib
from cortx.utils.conf_store.conf_store import Conf

sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))

from ha.core.config.config_manager import ConfigManager
from ha.core.event_analyzer.watcher.watcher import Watcher
from ha.core.event_analyzer.subscriber import Subscriber
from ha import const

class TestSubscriber(Subscriber):
    """
    Subscriber for testing.
    """
    def process_event(self, event: HealthEvent) -> None:
        """
        Test event.

        Args:
            event (HealthEvent): Event.
        """
        print(event)

def get_watcher():
    id = Conf.get(const.HA_GLOBAL_INDEX, "EVENT_ANALYZER.watcher.alert.consumer_id")
    message_type = Conf.get(const.HA_GLOBAL_INDEX, "EVENT_ANALYZER.watcher.alert.message_type")
    group = Conf.get(const.HA_GLOBAL_INDEX, "EVENT_ANALYZER.watcher.alert.consumer_group")
    event_filter = Conf.get(const.HA_GLOBAL_INDEX, "EVENT_ANALYZER.watcher.alert.filter")()
    parser = Conf.get(const.HA_GLOBAL_INDEX, "EVENT_ANALYZER.watcher.alert.parser")()
    subscriber = TestSubscriber()
    return Watcher(id, message_type, group, event_filter, parser, subscriber)

if __name__ == "__main__":
        ConfigManager.init("event_analyzer")
        watcher = get_watcher()
        watcher.start()
