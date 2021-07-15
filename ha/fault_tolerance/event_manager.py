#!/usr/bin/env python3

'''Module whoch provides interfaces to subscribe or unsubscribe for HA
   events to cortx components'''

import json

from cortx.utils.log import Log
from ha.core.config.config_manager import ConfigManager


class EventManager:
    '''Module responsible for publishing the HA event to a cortx component
       who has subscribed for the specific HA event through message bus'''

    def __init__(self):
        '''Make initialization work for Event Manager'''
        self._confstore = ConfigManager.get_confstore()
        self.cortx_comp_list = ['sspl', 'csm', 's3', 'motr', 'hare', 'ha']
        self._event_key = 'events/subscribe'

    def subscribe(self, component : str, events : list):
        '''
           Register all the events for the notification. It maintains
           list of events registered by the components. It maps the event
           name with component name and store it in the consul
           Ex:
           key: /cortx/ha/v2/events/subscribe/sspl
           value: ['enclosure:sensor:voltage', ...]
        '''
        Log.info(f'Received a subscribe request from {component} for event: {events}')
        self._validate_component(component)
        self._validate_events(events)
        event_string = json.dumps(events)
        if self._confstore.key_exists(f'self._event_key/{component}'):
            Log.error(f'{component} has already subscribed')
            raise Exception(f'{component} has already subescribed')
        self._confstore.set(f'{self._event_key}/{component}', event_string)
        Log.info('Subscription request is successfully stored into consul')

    def _validate_component(self, component: str) -> None:
        '''Checks if component is valid or not'''
        if component.lower() not in self.cortx_comp_list:
            Log.error(f'{component} is not a valid cortx component')
            raise Exception(f'{component} is not a valid cortx component')
        Log.info(f'{component} is valid for subscription request')

    def _validate_events(self, event: list) -> None:
        '''Checks if event is valid or not'''
        if not isinstance(event, list):
            Log.error(f'{event} is not a valid event')
            raise Exception('event type should be list')
        Log.info(f'event: {event} is valid for subscription request')

    def unsubscribe(self, component : str, events : list = None):
        '''Unregister the event for the specific component'''
