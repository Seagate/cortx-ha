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

import abc
import json
import re
import time
import uuid
from cortx.utils.log import Log
from ha.const import HA_DELIM
from ha.core.system_health.system_health_hierarchy import HealthHierarchy
from ha.core.config.config_manager import ConfigManager
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.system_health_metadata import SystemHealthComponents
from ha.core.error import HaSystemHealthException
from ha.core.system_health.system_health_manager import SystemHealthManager
from ha.core.system_health.system_health_exception import HealthNotFoundException

# TODO: (Task Refactore) Refactore and move system health update element code to element

class ElementHealthEvaluator(metaclass=abc.ABCMeta):
    """
    Generic cluster elements class.
    """

    HEALTH_MANAGER = None

    def __init__(self):
        self._confstore = ConfigManager.get_confstore()
        self.healthmanager = SystemHealthManager(self._confstore)

    @staticmethod
    def prepare_key(component: str, **kwargs) -> str:
        """
        Prepare Key. This is an internal method for preparing component status key.
        This will be used when updating/querying a component status.
        """
        # Get the key template.
        key = SystemHealthComponents.get_key(component)
        if "comp_id" in kwargs:
            key = key.replace(f"${component}_id", kwargs["comp_id"])
        # Check what all substitutions with actual values passed in kwargs to be done.
        subs = re.findall("\$\w+", key)
        # Check if the related argument present in kwargs, if yes substitute the same.
        for sub in subs:
            argument = re.split("\$", sub)
            if argument[1] in kwargs:
                key = re.sub("\$\w+", kwargs[argument[1]], key, 1)
            else:
                # Argument not present, break and return the key till this missing argument.
                key = re.split("\$", key)
                key = key[0]
                break
        return key

    def get_children(self, element: str, element_id: str, **kwargs) -> dict:
        """
        Get children of element.

        Args:
            element (str): [description]

        Returns:
            dict: Map of children and ids: {component: {component_type:{component_ids:{}}}}
        """
        # TODO: update code to get com_type, currently assuming comp = com_type
        children_ids: list = []
        children: list = HealthHierarchy.get_next_components(element)
        if len(children) == 0:
            return {}
        key = ElementHealthEvaluator.prepare_key(element, comp_id=element_id, **kwargs)
        key = key.replace(f"{HA_DELIM}health", "").replace(HA_DELIM, "", 1)
        data = self.healthmanager.get_key(key, just_value=False)
        for element in data.keys():
            key_list = element.split(HA_DELIM)
            if children[0] in key_list:
                child_index = key_list.index(children[0])
                element_id = key_list[child_index + 1]
                if element_id not in children_ids:
                    children_ids.append(key_list[child_index + 1])
        Log.debug(f"Children for {element}:{element_id} are {children_ids}")
        #{component: {component_type: [component_ids]}}}
        return { children[0]: { children[0]: children_ids }}

    def get_status_map(self, children: dict, **kwargs) -> dict:
        """
        Get status map from children

        Args:
            children (dict): children list

        Returns:
            dict: map of children with status.
        """
        status_map: dict = {}
        for element in children.keys():
            status_map[element] = {}
            for element_type in children[element]:
                status_map[element][element_type] = {}
                for element_id in children[element][element_type]:
                    Log.debug(f"Checking status for {element}:{element_type}:{element_id}....")
                    current_health = self.get_status_raw(element, element_id,
                                        comp_type=element_type, **kwargs)
                    if current_health:
                        event = json.loads(current_health).get("events")[0]
                        Log.debug(f"Status for {element}:{element_type}:{element_id} with {kwargs} is {event}")
                        status_map[element][element_type][element_id] = event.get("status")
                    else:
                        raise HealthNotFoundException(f"Missing health for component: {element}, component_id: {element_id}, component_type: {element_type}")
        Log.debug(f"status map is {status_map}")
        return status_map

    def _get_new_event(self, event_type, resource_type, resource_id, subelement_event) -> HealthEvent:
        """
        Update health event
        """
        new_event =  HealthEvent(
            source=subelement_event.source,
            event_id=subelement_event.event_id,
            event_type=event_type,
            severity=subelement_event.severity,
            site_id=subelement_event.site_id,
            rack_id=subelement_event.rack_id,
            cluster_id=subelement_event.cluster_id,
            storageset_id=subelement_event.storageset_id,
            node_id=subelement_event.node_id,
            host_id=subelement_event.host_id,
            resource_type=resource_type,
            timestamp=subelement_event.timestamp,
            resource_id=resource_id,
            specific_info=None
        )
        Log.info(f"New event is created: {resource_type}:{resource_id}, status: {resource_id}")
        return new_event

    def count_status(self, element_status_map: dict, status: str) -> int:
        """
        Get count of element having match status.

        Args:
            element_status_map (dict): status map
            status (str): element status

        Returns:
            int: count.
        """
        return list(element_status_map.values()).count(status)

    def get_status_raw(self, component: str, component_id: str=None, **kwargs):
        """
        get status method. This is a generic method which can return status of any component(s).
        """
        status = None
        try:
            # Prepare key and read the health value.
            if component_id != None:
                key = ElementHealthEvaluator.prepare_key(component, comp_id=component_id, **kwargs)
                status = self.healthmanager.get_key(key)
            else:
                key = ElementHealthEvaluator.prepare_key(component, **kwargs)
                status = self.healthmanager.get_key(key, just_value=False)
                # Remove any keys which are not for the health status.
                ignore_keys = []
                for key in status:
                    if "health" not in key:
                        ignore_keys.append(key)
                for key in ignore_keys:
                    del status[key]
            return status
        except Exception as e:
            Log.error(f"Failed reading status for component: {component} with Error: {e}")
            raise HaSystemHealthException("Failed reading status")

    @abc.abstractmethod
    def evaluate_status(self, health_event: HealthEvent) -> HealthEvent:
        """
        Evaluate health event of children and return its health event.

        Args:
            health_event (HealthEvent): Health event of children

        Returns:
            HealthEvent: Health event of current element.
        """
        pass
