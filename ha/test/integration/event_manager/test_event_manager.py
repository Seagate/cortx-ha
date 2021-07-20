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
import unittest
sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))
from cortx.utils.log import Log
from ha.core.system_health.const import EVENTS
from ha.core.event_manager.error import InvalidEvent
from ha.core.event_manager.event_manager import EventManager

class TestEventManager(unittest.TestCase):
    """
    Unit test for event manager
    """

    def setUp(self):
        Log.init(service_name='event_manager', log_path="/tmp", level="DEBUG")
        self.event_manager = EventManager.get_instance()

    def tearDown(self):
        pass

    def test_validate_event(self):
        self.event_manager._validate_events(EVENTS)
        with self.assertRaises(InvalidEvent):
            self.event_manager._validate_events(["a", "b"])

if __name__ == "__main__":
    unittest.main()