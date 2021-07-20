#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
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

from collections import OrderedDict
import json

from cortx.utils.log import Log
from ha.core.config.config_manager import ConfigManager
from ha.core.event_manager import const
from ha.core.event_manager.error import SubscriptionException, UnsubscriptionException, InvalidEvent


class EventManager:
    '''Module responsible for publishing the HA event to a cortx component
       who has subscribed for the specific HA event through message bus'''

    def __init__(self):
        '''Make initialization work for Event Manager'''
        self._confstore = ConfigManager.get_confstore()

    def subscribe(self, component : str, events : list):
        '''
           Register all the events for the notification. It maintains
           list of events registered by the components. It maps the event
           name with component name and store it in the consul. \
           Also, maps the component with event
        '''
        Log.info(f'Received a subscribe request from {component} for event: {events}')
        # self._validate_component(component)
        self._validate_events(events)
        self._store_component_key(f'{const.COMPONENT_KEY}/{component}', events)
        self._store_event_key(f'{const.EVENT_KEY}', events=events, comp=component)
        Log.info('Subscription request is successfully stored into consul')

    def _store_component_key(self, key: str, val: list) -> None:
        '''
           Perform actual consul store operation for component keys
           Ex:
           key: /cortx/ha/v2/events/subscribe/sspl
           self._confstore.key_existsvalue: ['enclosure:sensor:voltage', ...]
        '''
        if self._confstore.key_exists(key):
            comp_json_list = self._confstore.get(key)

            # Get the compnent listfrom consul first
            comp_list = json.loads(comp_json_list['cortx/ha/v1/' + f'{key}'])

            # Merge the old and new component list
            comp_list.extend(val)

            # Make sure that list is not duplicated
            set_comp_list = list(OrderedDict.fromkeys(comp_list))

            # Finally update it in the json string format
            event_string = json.dumps(set_comp_list)
            Log.debug(f'{component} has already subscribed. Updating the \
                        subscription using event list')
            self._confstore.update(key, event_string)
            Log.info('Subscription request is successfully stored into consul')
        else:
            # Store the key in the json string format
            event_list = json.dumps(val)
            self._confstore.set(f'{key}', event_list)

    def _store_event_key(self, key: str, events: list = [], comp: str = None) -> None:
        '''
           Perform actual consul store operation for event keys
           key: /cortx/ha/v2/events/subscribe/sspl
           value: ['enclosure:sensor:voltage', ...]
        '''
        if events:
            for event in events:
                new_key = key + f'/{event}'
                if self._confstore.key_exists(new_key):
                    comp_json_list = self._confstore.get(new_key)

                    # Get the list of components from consul
                    comp_list = json.loads(comp_json_list['cortx/ha/v1/' + f'{new_key}'])
                    if comp not in comp_list:
                        # If not already added, append to the old list
                        comp_list.append(comp)

                    # Store new updated list in json string format to consul
                    new_comp_list = json.dumps(comp_list)
                    self._confstore.update(new_key, new_comp_list)
                else:
                    new_comp_list = []
                    new_comp_list.append(comp)
                    # Store in go consul in the json string format
                    comp_list = json.dumps(new_comp_list)
                    self._confstore.set(f'{new_key}', comp_list)

    def _validate_component(self, component: str) -> None:
        '''Checks if component is valid or not'''
        pass

    def _validate_events(self, event: list) -> None:
        '''Checks if event is valid or not'''
        if not isinstance(event, list):
            Log.error(f'{event} is not a valid event')
            raise InvalidEvent('event type should be list')
        Log.debug(f'event: {event} is valid for subscription request')

    def _delete_component_key(self, component: str, events: list = None) -> None:
        '''
          Deletes the component from the event key
          Ex:
          Already existed consul key: cortx/ha/v1/events/subscribe/motr:["node:os:memory_usage", "node:interface:nw"]
          Request to delete: 'hare', 'node:interface:nw'
          Stored key after deletion will be: cortx/ha/v1/events/subscribe/motr:["node:os:memory_usage"]
        '''
        if self._confstore.key_exists(f'{const.COMPONENT_KEY}/{component}'):
            comp_json_list = self._confstore.get(f'{const.COMPONENT_KEY}/{component}')
            # Get the event list from consul
            event_list = json.loads(comp_json_list['cortx/ha/v1/' + f'{const.COMPONENT_KEY}/{component}'])
            for event in events:
                # Remove the event from the list(coming from consul)
                if event in event_list:
                    event_list.remove(event)
            if event_list:
                # After deletion, if list is not empty, update the consul key
                new_event_list = json.dumps(event_list)
                self._confstore.update(f'{const.COMPONENT_KEY}/{component}', new_event_list)
            else:
                # else, delete the whole component
                self._confstore.delete(f'{const.COMPONENT_KEY}/{component}')
        else:
            # If component key is not there, means event with that key will not be there,
            # hence safely raise exception here so that _delete_event_key will not be called
            raise UnsubscriptionException('Can not unsubscribe the component: {component} as it was not regostered earlier')

    def _delete_event_key(self, component: str, events: list = None):
        '''
          Deletes the event from the component key
          Ex:
          Already existed consul key: cortx/ha/v1/events/node:os:memory_usage:["motr", "hare"]
          Request to delete: 'hare', 'node:os:memory_usage'
          Stored key after deletion will be: cortx/ha/v1/events/node:os:memory_usage:["motr"]
        '''
        for event in events:
            if self._confstore.key_exists(f'{const.EVENT_KEY}/{event}'):
                comp_json_list = self._confstore.get(f'{const.EVENT_KEY}/{event}')
                # Get the component list
                comp_list = json.loads(comp_json_list['cortx/ha/v1/' + f'{const.EVENT_KEY}/{event}'])
                # Remove component from the list
                if component in comp_list:
                    comp_list.remove(component)
                if comp_list:
                    # If still list is not empty, update the consul key
                    new_comp_list = json.dumps(comp_list)
                    self._confstore.update(f'{const.EVENT_KEY}/{event}', new_comp_list)
                # Else delete the event from the consul
                else: self._confstore.delete(f'{const.EVENT_KEY}/{event}')

    def unsubscribe(self, component : str, events : list = None):
        '''
           Unregister the event for the specific component and the component \
           for the event using consul deletion
        '''
        self._validate_events(events)
        self._delete_component_key(component, events)
        self._delete_event_key(component, events)

ev = EventManager()
ev.subscribe('hare', ['node:os:memory_usage', 'node:interface:nw'])
ev.subscribe('hare', 'node:os:memory_usage')
ev.subscribe('motr', ['node:os:memory_usage', 'node:interface:nw', 'enclosure:interface:sas'])
ev.unsubscribe('hare', ['node:os:memory_usage', 'node:interface:nw'])
