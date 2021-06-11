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

from ha.core.config.config_manager import ConfigManager
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.system_health_metadata import SystemHealthComponents
import re
from ha.core.error import HaSystemHealthException
from cortx.utils.log import Log
from ha.core.system_health.system_health_manager import SystemHealthManager

# TODO: (Task Refactore) Refactore and move system health update element code to element

class Element(metaclass=abc.ABCMeta):
    """
    Generic cluster elements class.
    """

    def __init__(self):
        self._confstore = ConfigManager.get_confstore()
        self.healthmanager = SystemHealthManager(self._confstore)

    @abc.abstractmethod
    def get_event_from_subelement(self, children_event: HealthEvent):
        """
        Get element id for given healthevent.

        Args:
            healthevent (HealthEvent): Health event.
        """
        pass

    #TODO: Remove _prepare_key from system health
    def _prepare_key(self, component: str, **kwargs) -> str:
        """
        Prepare Key. This is an internal method for preparing component status key.
        This will be used when updating/querying a component status.
        """

        # Get the key template.
        key = SystemHealthComponents.get_key(component)
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

    #TODO: Remove get_status from system health
    def get_status(self, component: str, component_id: str=None, **kwargs):
        """
        get status method. This is a generic method which can return status of any component(s).
        """
        status = None
        try:
            # Prepare key and read the health value.
            if component_id != None:
                key = self._prepare_key(component, comp_id=component_id, **kwargs)
                status = self.healthmanager.get_key(key)
            else:
                key = self._prepare_key(component, **kwargs)
                status = self.healthmanager.get_key(key, just_value=False)
            return status

        except Exception as e:
            Log.error(f"Failed reading status for component: {component} with Error: {e}")
            raise HaSystemHealthException("Failed reading status")
