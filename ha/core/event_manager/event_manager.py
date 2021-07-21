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

from cortx.utils.log import Log
from ha.core.system_health.const import EVENTS
from ha.core.event_manager.error import *
from ha.core.event_manager.model.action_event import RecoveryActionEvent
from ha.core.event_manager.const import SUBSCRIPTION_LIST

class EventManager:

    __instance = None

    @staticmethod
    def get_instance():
        """
        Static method to fetch the current instance.
        Performs initialization related to common database and message bus
        """
        if not EventManager.__instance:
            EventManager(singleton_check=True)
        return EventManager.__instance

    def __init__(self, singleton_check: bool = False):
        """
        Private Constructor.
        """
        if singleton_check is False:
            raise Exception("Please use EventManager.get_instance() to fetch singleton instance of class")
        if EventManager.__instance is None:
            EventManager.__instance = self
        else:
            raise Exception("EventManager is singleton class, use EventManager.get_instance().")

    def _validate_component(self, component: str) -> None:
        """
        Validate component raise error invalid component.

        Args:
            component (str): Component name
        """
        if component not in SUBSCRIPTION_LIST:
            raise InvalidComponent(f"Invalid component {component}, not part of subscription list.")

    def _validate_events(self, events: list) -> None:
        """
        Raise error InvalidEvent if event is not valid.

        Args:
            events (list): Event list.
        """
        if not isinstance(events, list):
            raise InvalidEvent(f"Invalid type {events}, event type should be list")
        for event in events:
            if event not in EVENTS:
                raise InvalidEvent(f"Invalid event: {event}, not part of HA event list.")
        Log.debug(f"event: {event} is valid for subscription request")

    def subscribe(self, component: str, events: list) -> str:
        """
        Register events for the notification. It maintains list of events registered by the components.

        Args:
            component (str): Component Name
            events (list): Events.
        """
        pass

    def unsubscribe(self, component: str, events: list = None) -> None:
        """
        Unregistered events for the notification. Remove event name from the list

        Args:
            component (str): [description]
            events (list, optional): [description]. Defaults to None.
        """
        pass

    def get_events(self, component : str) -> list:
        """
        It returns list of registered events by the requested component.

        Args:
            component (str): Component name.

        Returns:
            list: List of events.
        """
        pass

    def publish(self, component:str, event: RecoveryActionEvent) -> None:
        """
        Publish event.

        Args:
            component (str): Component name.
            event (RecoveryActionEvent): Action event.
        """
        pass

    def message_type(self, component: str) -> str:
        """
        It returns message type name (queue name) mapped with component.

        Args:
            component (str): component name.
        """
        pass
