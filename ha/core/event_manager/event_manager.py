#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

'''Module which provides interfaces to subscribe or unsubscribe for HA
   events to cortx components'''

import json
from collections import OrderedDict
from cortx.utils.log import Log
from ha.util.message_bus import MessageBus
from ha.core.config.config_manager import ConfigManager
from ha.core.event_manager import const
from ha.core.event_manager.error import InvalidComponent
from ha.core.event_manager.error import InvalidEvent
from ha.core.event_manager.error import SubscribeException
from ha.core.event_manager.error import UnSubscribeException
from ha.core.event_manager.error import PublishException
from ha.core.event_manager.model.action_event import RecoveryActionEvent
from ha.core.event_manager.const import SUBSCRIPTION_LIST

class EventManager:
    """
    Module responsible for publishing the HA event to a cortx component
    who has subscribed for the specific HA event through message bus
    """
    __instance = None

    @staticmethod
    def get_instance(default_log_enable=True):
        """
        Static method to fetch the current instance.
        Performs initialization related to common database and message bus
        """
        if not EventManager.__instance:
            EventManager(default_log_enable, singleton_check=True)
        return EventManager.__instance

    def __init__(self, default_log_enable, singleton_check: bool = False):
        """
        Private Constructor.
        Make initialization work for Event Manager
        """
        if singleton_check is False:
            raise Exception("Please use EventManager.get_instance() to fetch \
                             singleton instance of class")
        if EventManager.__instance is None:
            EventManager.__instance = self
        else:
            raise Exception("EventManager is singleton class, use EventManager.get_instance().")
        if default_log_enable:
            ConfigManager.init(const.EVENT_MANAGER_LOG)
        self._confstore = ConfigManager.get_confstore()

    @staticmethod
    def _validate_events(events: list) -> None:
        """
        Raise error InvalidEvent if event is not valid.
        Args:
        events (list): Event list.
        """
        if events is None or not isinstance(events, list):
            raise InvalidEvent(f"Invalid type {events}, event type should be list")

    @staticmethod
    def _validate_component(component: str = None) -> None:
        """
        Validate component raise error invalid component.

        Args:
            component (str): Component name
        """
        if component is None or component.lower() not in SUBSCRIPTION_LIST:
            raise InvalidComponent(f"Invalid component {component}, not part of subscription list.")

    def _create_message_type(self, component: str) -> str:
        """
        Create and register message type for this component

        Args:
            component (str): Component name.

        Returns:
            str: Message type.
        """
        # TODO: Separate this logic in another class
        message_type = const.EVENT_MGR_MESSAGE_TYPE.replace("<component_id>", component)
        MessageBus.register(message_type)
        # Add message type key/value to confstore
        message_type_key = const.EVENT_MGR_MESSAGE_TYPE_KEY.replace("<component_id>", component)
        if not self._confstore.key_exists(message_type_key):
            self._confstore.set(message_type_key, message_type)
        Log.debug(f"Created {message_type} with {message_type_key}")
        return message_type

    def _delete_message_type(self, component: str) -> None:
        """
        Deletes the message type created earlier

        Args:
            component (str): Component name.
        """
        message_type = const.EVENT_MGR_MESSAGE_TYPE.replace("<component_id>", component)
        MessageBus.deregister(message_type)
        # Remove message type key from confstore
        message_type_key = const.EVENT_MGR_MESSAGE_TYPE_KEY.replace("<component_id>", component)
        if self._confstore.key_exists(message_type_key):
            self._confstore.delete(message_type_key)
        Log.info(f"Unsubscribed component {component} from message_type {message_type}")

    def _store_component_key(self, key: str, resource_type: str, val: list) -> None:
        '''
           Perform actual confstore store operation for component keys
           Ex:
           key: /cortx/ha/v1/events/subscribe/sspl
           confstore value: ['enclosure:sensor:voltage/failed', ...]
        '''
        if self._confstore.key_exists(key):
            event_json_list = self._confstore.get(key)

            # Get the event list from confstore first
            _, event_list = event_json_list.popitem()

            event_list = json.loads(event_list)
            for event in val:
                new_val = resource_type + '/' + event
                if new_val in event_list:
                    continue
                # Merge the old and new component list
                event_list.append(new_val)

            # Make sure that list is not duplicated
            set_event_list = list(OrderedDict.fromkeys(event_list))

            Log.debug(f'Final newly added list of subscription is: {event_list}, \
                       Key is: {key}')
            # Finally update it in the json string format
            event_string = json.dumps(set_event_list)
            Log.debug(f'Subscription is already done with key \
                       {key}. Updating the subscription using event list')
            self._confstore.update(key, event_string)
        else:
            new_event = []
            for event in val:
                new_val = resource_type + '/' + event
                new_event.append(new_val)
            # Store the key in the json string format
            event_list = json.dumps(new_event)
            Log.debug(f'Final newly added list of subscription is: {event_list}, \
                       Key is: {key}')
            self._confstore.set(f'{key}', event_list)

    def _store_event_key(self, key: str, resource_type: str, states: list = None, comp: str = None) -> None:
        '''
           Perform actual confstore store operation for event keys
           key: /cortx/ha/v1/events/enclosure:hw:disk/online
           value: ['sspl', ...]
        '''
        if states:
            for state in states:
                new_key = key + f'/{resource_type}/{state}'
                if self._confstore.key_exists(new_key):
                    comp_json_list = self._confstore.get(new_key)

                    # Get the list of components from confstore
                    _, comp_list = comp_json_list.popitem()
                    comp_list = json.loads(comp_list)
                    if comp not in comp_list:
                        # If not already added, append to the old list
                        comp_list.append(comp)

                    # Store new updated list in json string format to confstore
                    new_comp_list = json.dumps(comp_list)
                    Log.debug(f'Final newly added list of subscription is: {new_comp_list}, \
                                Key is: {key}')
                    self._confstore.update(new_key, new_comp_list)
                else:
                    new_comp_list = []
                    new_comp_list.append(comp)
                    # Store in go confstore in the json string format
                    comp_list = json.dumps(new_comp_list)
                    Log.debug(f'Final newly added list of subscription is: {new_comp_list}, \
                                Key is: {key}')
                    self._confstore.set(f'{new_key}', comp_list)

    def _delete_component_key(self, component: str, resource_type: str, states: list = None) -> None:
        '''
          Deletes the component from the event key
          Ex:
          Already existed confstore key:
             key: cortx/ha/v1/events/subscribe/hare:
             value: ["node:os:memory_usage/failed", "node:interface:nw/online"]
          Request to delete:
            'hare', 'node:interface:nw'
          Stored key after deletion will be:
            key: cortx/ha/v1/events/subscribe/hare:
            value: ["node:os:memory_usage/failed"]
        '''
        for state in states:
            delete_required_state = resource_type + '/' + state
            if self._confstore.key_exists(f'{const.COMPONENT_KEY}/{component}'):
                comp_json_list = self._confstore.get(f'{const.COMPONENT_KEY}/{component}')
                # Get the event list from confstore
                _, event_list = comp_json_list.popitem()
                event_list = json.loads(event_list)
                # Remove the event from the list(coming from confstore)
                if delete_required_state in event_list:
                    Log.debug(f'Deleting the subscription for {component}. For: {delete_required_state}')
                    event_list.remove(delete_required_state)
                if event_list:
                    # After deletion, if list is not empty, update the confstore key
                    new_event_list = json.dumps(event_list)
                    Log.debug(f'Updating the subscription for {component}. new list: {new_event_list}')
                    self._confstore.update(f'{const.COMPONENT_KEY}/{component}', new_event_list)
                else:
                    Log.debug(f'Deleting subscription for {component} completely as there are \
                                no other subscriptions')
                    # else, delete the whole component
                    self._confstore.delete(f'{const.COMPONENT_KEY}/{component}')
                    # As there is no subscription for this component,
                    # delete the topic key
                    self._delete_message_type(component)
            else:
                # If component key is not there, means event with that key will not be there,
                # hence safely raise exception here so that _delete_event_key will not be called
                raise UnSubscribeException('Can not unsubscribe the component: \
                                            {component} as it was not registered earlier')

    def _delete_event_key(self, component: str, resource_type: str, states: list = None):
        '''
          Deletes the event from the component key
          Ex:
          Already existed confstore key: cortx/ha/v1/events/node:os:memory_usage/failed:["motr", "hare"]
          Request to delete: 'hare', 'node:os:memory_usage' 'failed'
          Stored key after deletion will be: cortx/ha/v1/events/node:os:memory_usage/failed:["motr"]
        '''
        for state in states:
            if self._confstore.key_exists(f'{const.EVENT_KEY}/{resource_type}/{state}'):
                comp_json_list = self._confstore.get(f'{const.EVENT_KEY}/{resource_type}/{state}')
                # Get the component list
                _, comp_list = comp_json_list.popitem()
                comp_list = json.loads(comp_list)
                # Remove component from the list
                if component in comp_list:
                    Log.debug(f'Deleting the key for {resource_type}/{state}. For: {component}')
                    comp_list.remove(component)
                if comp_list:
                    # If still list is not empty, update the confstore key
                    new_comp_list = json.dumps(comp_list)
                    Log.debug(f'Updating the key for {resource_type}/{state}. new comp list:{new_comp_list}')
                    self._confstore.update(f'{const.EVENT_KEY}/{resource_type}/{state}', new_comp_list)
                # Else delete the event from the confstore
                else:
                    Log.debug(f'Deleting the key for {resource_type}/{state} completely \
                                as there are no more subscriptions')
                    self._confstore.delete(f'{const.EVENT_KEY}/{resource_type}/{state}')
            else:
                Log.error(f'Key: {const.EVENT_KEY}/{resource_type}/{state} does not present')

    def _get_producer(self, component: str) -> object:
        """
        Get Producer object.

        Args:
            component (str): Component
        """
        producer_id = const.EVENT_MGR_PRODUCER_ID.replace("<component_id>", component)
        message_type_key = const.EVENT_MGR_MESSAGE_TYPE_KEY.replace("<component_id>", component)
        message_type_key_val = self._confstore.get(message_type_key)
        _, message_type = message_type_key_val.popitem()
        return MessageBus.get_producer(producer_id, message_type)

    def check_event_key(self, resource_type: str, state: str = None) -> bool:
        """
        Check if event exists.

        Args:
            resource_type (str): Event key.
            state (str, optional): Status. Defaults to None.

        Returns:
            bool: True if key exists.
        """
        event_key = f"{const.EVENT_KEY}/{resource_type}/{state}"
        return self._confstore.key_exists(event_key)

    def subscribe(self, component: str = None, events: list = None) -> None:
        """
        Register all the events for the notification. It maintains
        list of events registered by the components. It maps the event
        name with component name and store it in the consul.
        Also, maps the component with event

        Args:
            component (str): Component Name
            events (list): Events.

        Raise:
            SubscribeException: Raise error if failed.
        """
        # TODO: Add health monitor rules
        Log.info(f'Received a subscribe request from {component}')
        try:
            EventManager._validate_component(component)
            EventManager._validate_events(events)
            message_type = self._create_message_type(component)
            for event in events:
                self._store_component_key(f'{const.COMPONENT_KEY}/{component}', event.resource_type, event.states)
                self._store_event_key(f'{const.EVENT_KEY}', event.resource_type, event.states, comp=component)
            Log.info(f"Successfully Subscribed component {component} with message_type {message_type}")
            return message_type
        except Exception as e:
            raise SubscribeException(f"Failed to subscribe {component}. Error: {e}")

    def unsubscribe(self, component: str = None, events: list = None):
        """
        Deregister the event for the specific component and the component \
        for the event using consul deletion

        Args:
            component (str): Component Name.
            events (list, optional): Event List. Defaults to None.

        Raise:
            UnSubscribeException: Raise error if failed.
        """
        #TODO: Provide way to unsubscribe all event
        Log.info(f"Received unsubscribe for {component}")
        try:
            self._validate_component(component)
            self._validate_events(events)
            for event in events:
                self._delete_component_key(component, event.resource_type, event.states)
                self._delete_event_key(component, event.resource_type, event.states)
            Log.info(f"Successfully UnSubscribed component {component}")
        except Exception as e:
            raise UnSubscribeException(f"Failed to unsubscribe {component}. Error: {e}")

    def get_events(self, component : str) -> list:
        """
        It returns list of registered events by the requested component.

        Args:
            component (str): Component name.

        Returns:
            list: List of events.
        """
        key = f'{const.COMPONENT_KEY}/{component}'
        value = []
        Log.debug(f"Fetching subscribed events for {key}")

        kv = self._confstore.get(key)
        if kv:
            for k, v in kv.items():
                if k.endswith(key):
                    value.extend(json.loads(v))
                    break
        return value

    def publish(self, event: RecoveryActionEvent) -> None:
        """
        Publish event.
        Args:
            event (RecoveryActionEvent): Action event.
        """
        try:
            component_list = []
            # Run through list of components subscribed for this event and send event to each of them
            component_list_key = f'{const.EVENT_KEY}/{event.resource_type}/{event.event_type}'
            component_list_key_val = self._confstore.get(component_list_key)
            if component_list_key_val:
                _, value = component_list_key_val.popitem()
                component_list = json.loads(value)
            for component in component_list:
                message_producer = self._get_producer(component)
                event_to_send = str(event)
                Log.info(f"Sending action event {event_to_send} to component {component}")
                message_producer.publish(event_to_send)
        except Exception as e:
            Log.error(f"Failed sending message for {event.resource_type}, Error: {e}")
            raise PublishException(f"Failed sending message for {event.resource_type}, Error: {e}")

    def message_type(self, component: str) -> str:
        """
        It returns message type name (queue name) mapped with component.
        Args:
            component (str): component name.
        """
        key = const.EVENT_MGR_MESSAGE_TYPE_KEY.replace("<component_id>", component)
        value = None
        Log.debug(f"Fetching message type for {key}")

        kv = self._confstore.get(key)
        if kv:
            for k, v in kv.items():
                if k.endswith(key):
                    value = v
                    break
        return value
