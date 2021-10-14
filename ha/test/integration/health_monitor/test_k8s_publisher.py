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
import time

from ha.core.event_analyzer.filter_event import FiletrEvent
from ha.alert.K8s_alert import K8SAlert
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.event_manager.event_manager import EventManager
from ha.core.event_manager.subscribe_event import SubscribeEvent
from ha.util.message_bus import MessageBus, CONSUMER_STATUS
from ha.const import K8S_ALERT_RESOURCE_TYPE, K8S_ALERT_STATUS

sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))

MSG = False

def receive(message):
    print("MESSAGE: ",message)
    global MSG
    MSG = True
    return CONSUMER_STATUS.SUCCESS_STOP

if __name__ == '__main__':
    try:
        print("********Event Publisher********")
        event_manager = EventManager.get_instance()
        component = "csm"
        resource_type = K8S_ALERT_RESOURCE_TYPE.RESOURCE_TYPE_POD.value
        state = K8S_ALERT_STATUS.STATUS_FAILED.value
        message_type = event_manager.subscribe('csm', [SubscribeEvent(resource_type, [state])])
        print(f"Subscribed {component}, message type is {message_type}")
        k8s_event = K8SAlert("cortx", "node2", "cortx-data123", K8S_ALERT_STATUS.STATUS_FAILED.value, K8S_ALERT_RESOURCE_TYPE.RESOURCE_TYPE_POD.value, "16215909572")
        health_event = HealthEvent(k8s_event)
        filetr_event = FiletrEvent()
        recovery_action_event = filetr_event.process_event(health_event)
        if recovery_action_event is not None:
            event_manager.publish(recovery_action_event)
        else:
            sys.exit(0)
        print("Consuming the action event")
        message_consumer = MessageBus.get_consumer(consumer_id="1",
                            consumer_group='test_publisher',
                            message_type=message_type, callback=receive)
        message_consumer.start()
        while not MSG:
            time.sleep(2)
            print("waiting for msg")
        message_consumer.stop()
        unsubscribe = event_manager.unsubscribe(component, [SubscribeEvent(resource_type, [state])])
        print(f"Unsubscribed {component}")
        print("Event Publisher test completed successfully")
    except Exception as e:
        print(f"Failed to run event manager publiser test, Error: {e}")
