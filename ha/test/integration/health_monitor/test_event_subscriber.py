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
sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))
import unittest
from ha.core.event_manager.event_manager import EventManager
from ha.core.event_manager.subscribe_event import SubscribeEvent
from ha.core.event_manager.resources import SUBSCRIPTION_LIST
from ha.core.event_manager.resources import RESOURCE_STATUS
from ha.core.event_manager.resources import RESOURCE_TYPES

class TestEventManager(unittest.TestCase):
    """
    Unit test for event manager
    """

    def setUp(self):
        self.event_manager = EventManager.get_instance()
        self.component = SUBSCRIPTION_LIST.TEST
        self.event = SubscribeEvent(RESOURCE_TYPES.NODE,
            [RESOURCE_STATUS.FAILED, RESOURCE_STATUS.ONLINE, RESOURCE_STATUS.DEGRADED, RESOURCE_STATUS.OFFLINE])

    def tearDown(self):
        pass

    def test_subscriber(self):
        self.event_manager.subscribe(self.component, [self.event])
        self.event_manager.unsubscribe(self.component, [self.event])

if __name__ == "__main__":
    unittest.main()