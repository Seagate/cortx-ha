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
import pathlib
import sys
import time

sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))

from ha.core.event_manager.event_manager import EventManager
from ha.core.event_manager.subscribe_event import SubscribeEvent
from ha.core.system_health.model.health_event import HealthEvent
from ha.util.message_bus import MessageBus
from ha.core.action_handler.action_factory import ActionFactory
from ha.core.event_manager.resources import SUBSCRIPTION_LIST
from ha.core.event_manager.resources import RESOURCE_TYPES, RESOURCE_STATUS

MSG = False

def receive(message):
    print(message)
    global MSG
    MSG = True

if __name__ == '__main__':
    try:
        print("********Event Action Handler********")
        event_manager = EventManager.get_instance()
        component = SUBSCRIPTION_LIST.CSM
        resource_type = RESOURCE_TYPES.NODE
        state = RESOURCE_STATUS.FAILED

        actions = ["publish"]
        message_type = event_manager.subscribe(component, [SubscribeEvent(resource_type, [state])])
        print(f"Subscribed {component}, message type is {message_type}")
        health_event = HealthEvent("csm", "1", "offline", "fault", "1", "1", "1", "1", "1", "q", "node", "16215009572", "1", None)
        action_handler_obj = ActionFactory.get_action_handler(actions=actions, event=health_event)
        action_handler_obj.act(event=health_event, action=actions)
        print("Consuming the action event")
        message_consumer = MessageBus.get_consumer(consumer_id="1",
                                                   consumer_group='test_publisher',
                                                   callback=receive, message_type=message_type)
        message_consumer.start()
        while not MSG:
            time.sleep(2)
            print("waiting for msg")
        message_consumer.stop()
        unsubscribe = event_manager.unsubscribe(component, [SubscribeEvent(resource_type, [state])])
        print(f"Unsubscribed {component}")
        print("Event action handler test completed successfully")
    except Exception as e:
        print(f"Failed to run event action handler test, Error: {e}")
