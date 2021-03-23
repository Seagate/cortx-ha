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

import re
import time

from cortx.utils.log import Log
from ha import const
from ha.core.system_health.system_health_metadata import SystemHealthComponents, SystemHealthHierarchy
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.model.entity_health import EntityEvent, EntityAction, EntityHealth
from ha.core.system_health.status_mapper import StatusMapper
from ha.core.system_health.system_health_manager import SystemHealthManager
from ha.core.error import HaSystemHealthException

class SystemHealth:
    """
    System Health. This class implements an interface to the HA System Health module.
    """

    def __init__(self, store):
        """
        Init method.
        """
        self.update_hierarchy = []
        self.node_id = None
        self.node_map = {}
        self.statusmapper = StatusMapper()
        self.healthmanager = SystemHealthManager(store)

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

    def get_status(self, component: str, component_id: str, **kwargs):
        """
        get status method. This is a generic method which can return status of any component(s).
        """
        try:
            # Prepare key and read the health value.
            key = self._prepare_key(component, comp_id=component_id, **kwargs)
            return self.healthmanager.get_key(key)

        except Exception as e:
            Log.error(f"Failed reading status for component: {component} with Error: {e}")
            raise HaSystemHealthException("Failed reading status")

    def get_service_status(self, service_type=None, node_id=None):
        """
        get service status method. This method is for returning a status of a service.
        """

    def get_node_status(self, node_id, **kwargs):
        """
        get node status method. This method is for returning a status of a node.
        """

    def get_storageset_status(self, storageset_id, **kwargs):
        """
        get storageset status method. This method is for returning a status of a storageset.
        """

    def get_cluster_status(self, cluster_id, **kwargs):
        """
        get cluster status method. This method is for returning a status of a cluster.
        """
    def _update(self, component: str, comp_type: str, comp_id: str, healthvalue: str, next_component: str=None):
        """
        update method. This is an internal method for updating the system health.
        """
        key = self._prepare_key(component, cluster_id=self.node_map['cluster_id'], site_id=self.node_map['site_id'],
                                rack_id=self.node_map['rack_id'], storageset_id=self.node_map['storageset_id'],
                                node_id=self.node_id, server_id=self.node_id, storage_id=self.node_id,
                                comp_type=comp_type, comp_id=comp_id)
        self.healthmanager.set_key(key, healthvalue)

        # TODO: Check and if not present already, store the node map.

        # Check the next component to be updated, if none then return.
        if next_component is None:
            return
        else:
            # TODO: Calculate and update the health of the next component in the hierarchy.
            return

    def process_event(self, healthevent: HealthEvent):
        """
        Process Event method. This method could be called for updating the health status.
        """

        # TODO: Check the user and see if allowed to update the system health.

        try:
            status = self.statusmapper.map_event(healthevent.event_type)
            component = SystemHealthComponents.get_component(healthevent.resource_type)

            # Get the health update hierarchy
            self.update_hierarchy = SystemHealthHierarchy.get_hierarchy(component)
            if (len(self.update_hierarchy) - 1) > self.update_hierarchy.index(component):
                next_component = self.update_hierarchy[self.update_hierarchy.index(component) + 1]
            else:
                next_component = None

            # Get the component type and id received in the event.
            component_type = healthevent.resource_type.split(':')[-1]
            component_id = healthevent.resource_id
            # Read the currently stored health value
            current_health = self.get_status(component, component_id, comp_type=component_type,
                                        cluster_id=healthevent.cluster_id, site_id=healthevent.site_id,
                                        rack_id=healthevent.rack_id, storageset_id=healthevent.storageset_id,
                                        node_id=healthevent.node_id, server_id=healthevent.node_id,
                                        storage_id=healthevent.node_id)
            if current_health:
                # Update the current health value itself.
                updated_health = EntityHealth.read(current_health)
            else:
                # Health value not present in the store currently, create now.
                updated_health = EntityHealth()

            # Create a new event and action
            current_timestamp = str(int(time.time()))
            entity_event = EntityEvent(healthevent.timestamp, current_timestamp, status, healthevent.specific_info)
            entity_action = EntityAction(current_timestamp, const.ACTION_STATUS.PENDING.value)
            # Add the new event and action to the health value
            updated_health.add_event(entity_event)
            updated_health.set_action(entity_action)
            # Convert the health value as appropriate for writing to the store.
            updated_health = EntityHealth.write(updated_health)

            # Update the node map
            self.node_id = healthevent.node_id
            self.node_map = {'cluster_id':healthevent.cluster_id, 'site_id':healthevent.site_id,
                             'rack_id':healthevent.rack_id, 'storageset_id':healthevent.storageset_id}

            # Update in the store.
            self._update(component, component_type, component_id, updated_health, next_component=next_component)
            Log.info(f"Updated health for component: {component}, Type: {component_type}, Id: {component_id}")

        except Exception as e:
            Log.error(f"Failed processing system health event with Error: {e}")
            raise HaSystemHealthException("Failed processing system health event")