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

import json

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from ha import const
from ha.core.error import HaEntityHealthException

class EntityEvent:
    """
    Entity Event. This class implements an entity event object,
    which will be stored in the entity health.
    """

    def __init__(self, event_timestamp: str, created_timestamp: str, status: str, specific_info: dict=None):
        """
        Init method.
        """

        self.event_timestamp = event_timestamp
        self.created_timestamp = created_timestamp
        self.status = status
        self.specific_info = specific_info

    def ret_dict(self):
        """
        Return dictionary attribute.
        """

        return vars(self)

class EntityAction:
    """
    This class implements an action object stored in the entity health.
    """

    def __init__(self, modified_timestamp: str, status: str):
        """
        Init method.
        """
        self.modified_timestamp = modified_timestamp
        self.status = status

    def ret_dict(self):
        """
        Return dictionary attribute.
        """

        return vars(self)

class EntityHealth:
    """
    Entity Health. This class implements a health object, which will be stored in store
    for every component.
    """

    def __init__(self):
        """
        Init method.
        """

        self.events: list = []
        self.action: EntityAction = {}
        self.attributes: dict = {}

    def add_event(self, event: EntityEvent):
        """
        Adds a new event to the entity health.
        """

        # Insert the new event as a first element in th events array
        self.events.insert(0, event)
        # Keep the history of events as per the configuration
        num_events = Conf.get(const.HA_GLOBAL_INDEX, "SYSTEM_HEALTH.num_entity_health_events")
        if len(self.events) > num_events:
            # Delete the last event entry
            del self.events[len(self.events) - 1]

    def set_action(self, action: EntityAction):
        """
        Sets action to a specified value.
        """

        self.action = action

    def add_attributes(self, attributes: dict):
        """
        Add attibutes to the existing attributes.
        """

        for key, value in attributes.items():
            self.attibutes[key] = value

    def ret_dict(self):
        """
        Return dictionary attribute.
        """

        return vars(self)

    @staticmethod
    def write(entity_health) -> json:
        """
        Converts the entity health object into a json string which then
        could be written to the store.
        """

        return json.dumps(entity_health, default=lambda o: o.ret_dict(), indent=None)

    @staticmethod  
    def read(current_health: json):
        """
        Converts the entity health json into an object of this class.
        """

        try:
            # TODO: Check and optimize below code.
            # Load the current health json.
            current_health_dict = json.loads(current_health)

            # Create, populate and return the object.
            entity_health = EntityHealth()
            for key in current_health_dict.keys():
                if key == "events":
                    num_events = len(current_health_dict[key])
                    while num_events:
                        num_events = num_events - 1
                        entity_event = EntityEvent(current_health_dict[key][num_events]["event_timestamp"],
                                                   current_health_dict[key][num_events]["created_timestamp"],
                                                   current_health_dict[key][num_events]["status"],
                                                   current_health_dict[key][num_events]["specific_info"])
                        entity_health.add_event(entity_event)
                elif key == "action":
                    entity_action = EntityAction(current_health_dict[key]["modified_timestamp"], current_health_dict[key]["status"])
                    entity_health.set_action(entity_action)
                elif key == "attributes":
                    entity_health.add_attributes(current_health_dict[key])
                else:
                    Log.error(f"Unrecognized key found in entity health in store: {key}")
                    raise HaEntityHealthException("Unrecognized key found in entity health in store")
            return entity_health

        except Exception as e:
            Log.error(f"Failed converting Entity Health json into an object with Error: {e}")
            raise HaSystemHealthException("Failed converting Entity Health json into an object")