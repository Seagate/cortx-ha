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

'''Module which provides interfaces to subscribe or unsubscribe for HA
   events to cortx components'''

import json

from cortx.utils.log import Log
from cortx.utils.message_bus import MessageBusAdmin, MessageProducer
from ha.core.config.config_manager import ConfigManager
from ha.core.event_manager import const
from ha.core.event_manager.error import SubscriptionException, UnsubscriptionException, PublishException
from ha.core.event_manager.model.action_event import ActionEvent

class EventManager:
    '''Module responsible for publishing the HA event to a cortx component
       who has subscribed for the specific HA event through message bus'''

    def __init__(self):
        '''Make initialization work for Event Manager'''
        self._confstore = ConfigManager.get_confstore()

    def subscribe(self, component : str, events : list) -> str:
        '''
           Register all the events for the notification. It maintains
           list of events registered by the components. It maps the event
           name with component name and store it in the consul
           Ex:
           key: /cortx/ha/v2/events/subscribe/sspl
           value: ['enclosure:sensor:voltage', ...]
        '''
        try:
            if component:
                # Create and register message type for this component
                message_bus_admin = MessageBusAdmin(const.HA_MESSAGE_BUS_ADMIN)
                message_type = const.EVENT_MGR_MESSAGE_TYPE.replace("<component_id>", component)
                message_type_list = message_bus_admin.list_message_types()
                if message_type not in message_type_list:
                    message_bus_admin.register_message_type(message_types = [message_type], partitions = 1)
                # Add message type key/value to confstore
                message_type_key = const.EVENT_MGR_MESSAGE_TYPE_KEY.replace("<component_id>", component)
                if not self._confstore.key_exists(message_type_key):
                    self._confstore.set(message_type_key, message_type)
                Log.debug(f"Created message type {message_type} for component {component}")
                # Update component list subscribed to these events
                if events:
                    for event in events:
                        component_list = []
                        # Read the components list if it exists in confstore.
                        component_list_key = const.EVENT_COMPONENT_LIST.replace("<event_name>", event)
                        if self._confstore.key_exists(component_list_key):
                            component_list_key_val = self._confstore.get(component_list_key)
                            _, value = component_list_key_val.popitem()
                            component_list = json.loads(value)
                        Log.debug(f"Components {component_list} already subscribed to event {event}")
                        # Update the component list if the component does not exist already.
                        if component not in component_list:
                            component_list.append(component)
                        if self._confstore.key_exists(component_list_key):
                            self._confstore.update(component_list_key, json.dumps(component_list))
                        else:
                            self._confstore.set(component_list_key, json.dumps(component_list))
                        Log.debug(f"Updated components {component_list} subscribed to event {event}")
                Log.info(f"Subscribed component {component} with message type {message_type}")
                return message_type
        except Exception as e:
            Log.error(f"{component} subscription failed, Error: {e}")
            raise SubscriptionException(f"{component} subscription failed, Error: {e}")

    def _validate_component(self, component: str) -> None:
        '''Checks if component is valid or not'''

    def _validate_events(self, event: list) -> None:
        '''Checks if event is valid or not'''

    def unsubscribe(self, component : str, events : list = None) -> None:
        '''Unregister the event for the specific component'''
        try:
            if component:
                # Delete this component from subscribed list to these events
                if events:
                    for event in events:
                        component_list = []
                        # Read the components list if it exists in confstore.
                        component_list_key = const.EVENT_COMPONENT_LIST.replace("<event_name>", event)
                        if self._confstore.key_exists(component_list_key):
                            component_list_key_val = self._confstore.get(component_list_key)
                            _, value = component_list_key_val.popitem()
                            component_list = json.loads(value)
                        Log.debug(f"Components {component_list} subscribed to event {event}")
                        # Delete the component if it exists in the list.
                        if component in component_list:
                            component_list.remove(component)
                        if len(component_list) == 0:
                            self._confstore.delete(component_list_key)
                        else:
                            self._confstore.update(component_list_key, json.dumps(component_list))
                        Log.debug(f"Updated components {component_list} subscribed to event {event}")

                # TODO: Before below, check if any subscriptions present for this component
                # Check and remove message type (Queue) if it exists for this component
                message_bus_admin = MessageBusAdmin(const.HA_MESSAGE_BUS_ADMIN)
                message_type = const.EVENT_MGR_MESSAGE_TYPE.replace("<component_id>", component)
                message_type_list = message_bus_admin.list_message_types()
                if message_type in message_type_list:
                    message_bus_admin.deregister_message_type(message_types = [message_type])
                # Remove message type key from confstore
                message_type_key = const.EVENT_MGR_MESSAGE_TYPE_KEY.replace("<component_id>", component)
                if self._confstore.key_exists(message_type_key):
                    self._confstore.delete(message_type_key)
                Log.debug(f"Removed message type {message_type} for component {component}")
                Log.info(f"Unsubscribed component {component}")
        except Exception as e:
            Log.error(f"{component} unsubscription failed, Error: {e}")
            raise UnsubscriptionException(f"{component} unsubscription failed, Error: {e}")

    def publish(self, event: ActionEvent) -> None:
        """
        Publish event.
        Args:
            event (ActionEvent): Action event.
        """
        try:
            component_list = []
            # Run through list of components subscribed for this event and send event to each of them
            component_list_key = const.EVENT_COMPONENT_LIST.replace("<event_name>", event.resource_type)
            if self._confstore.key_exists(component_list_key):
                component_list_key_val = self._confstore.get(component_list_key)
                _, value = component_list_key_val.popitem()
                component_list = json.loads(value)
            for component in component_list:
                producer_id = const.EVENT_MGR_PRODUCER_ID.replace("<component_id>", component)
                message_type_key = const.EVENT_MGR_MESSAGE_TYPE_KEY.replace("<component_id>", component)
                message_type_key_val = self._confstore.get(message_type_key)
                _, message_type = message_type_key_val.popitem()
                message_producer = MessageProducer(producer_id = producer_id,
                                        message_type = message_type,
                                        method = const.EVENT_MGR_PRODUCER_METHOD)
                event_to_send = event.to_json()
                Log.debug(f"Sending action event {event_to_send} to component {component}")
                message_producer.send([event_to_send])
        except Exception as e:
            Log.error(f"Failed sending message for {event.resource_type}, Error: {e}")
            raise PublishException(f"Failed sending message for {event.resource_type}, Error: {e}")