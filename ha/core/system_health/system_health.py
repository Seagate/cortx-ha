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
import ast
import json

from cortx.utils.log import Log
from ha import const
from ha.core.system_health.const import NODE_MAP_ATTRIBUTES
from ha.core.event_analyzer.subscriber import Subscriber
from ha.core.system_health.system_health_metadata import SystemHealthComponents, SystemHealthHierarchy
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.model.entity_health import EntityEvent, EntityAction, EntityHealth
from ha.core.system_health.status_mapper import StatusMapper
from ha.core.system_health.system_health_manager import SystemHealthManager
from ha.core.error import HaSystemHealthException
from ha.core.cluster.const import SYSTEM_HEALTH_OUTPUT_V1, GET_SYS_HEALTH_ARGS
from ha.core.system_health.const import CLUSTER_ELEMENTS, HEALTH_STATUSES
from ha.core.system_health.model.health_status import StatusOutput, ComponentStatus
from ha.core.system_health.system_health_hierarchy import HealthHierarchy

class SystemHealth(Subscriber):
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

    def get_status_raw(self, component: str, component_id: str=None, **kwargs):
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

    def get_status(self, component: CLUSTER_ELEMENTS = CLUSTER_ELEMENTS.CLUSTER.value, depth: int = 1, version: str = SYSTEM_HEALTH_OUTPUT_V1, **kwargs):
        """
        Return health status for the requested components.
        Args:
            component ([CLUSTER_ELEMENTS]): The component whose health status is to be returned.
            depth ([int]): A depth of elements starting from the input "component" that the health status
                is to be returned.
            **kwargs([dict]): Variable number of arguments that are used as filters,
                e.g. "id" of the input "component".
        Returns:
            ([dict]): Returns dictionary. {"status": "Succeeded"/"Failed"/"Partial", "output": "", "error": ""}
                status: Succeeded, Failed, Partial
                output: Dictionary with element health status
                error: Error information if the request "Failed"
        """

        try:
            component_id = None
            if GET_SYS_HEALTH_ARGS.ID.value in kwargs and kwargs[GET_SYS_HEALTH_ARGS.ID.value] is not "":
                component_id = kwargs[GET_SYS_HEALTH_ARGS.ID.value]

            # Get raw status starting from cluster
            self._status_dict = self.get_status_raw(CLUSTER_ELEMENTS.CLUSTER.value)
            # Remove any keys which are not for the health status.
            ignore_keys = []
            for key in self._status_dict:
                if "health" not in key:
                    ignore_keys.append(key)
            for key in ignore_keys:
                del self._status_dict[key]

            # Get the requested component level in the health hierarchy
            self._health_hierarchy = HealthHierarchy()
            component_level = self._health_hierarchy.get_component_level(component)

            # Set the depth to be returned, check for partial status.
            self._partial_status = False
            total_depth = self._health_hierarchy.get_total_depth()
            if depth == 0:
                depth = total_depth
            else:
                depth += component_level - 1 # Decrement by 1 for the component level itself.
                if depth > self._health_hierarchy.get_total_depth():
                    depth = total_depth
                    self._partial_status = True

            # Prepare and return the output
            output = StatusOutput(version)
            self._prepare_status(component, component_id = component_id, start_level = component_level, current_level = component_level, depth = depth, parent = output)
            output_status = const.STATUSES.SUCCEEDED.value
            if self._partial_status:
                output_status = const.STATUSES.PARTIAL.value
            return json.dumps({"status": output_status, "output": json.loads(output.to_json()), "error": ""})
        except Exception as e:
            Log.error(f"Failed reading status. Error: {e}")
            raise HaSystemHealthException("Failed reading status")

    def _prepare_status(self, component, component_id: str = None, start_level: int = 1, current_level: int = 1, depth: int = 1, parent: object = None):
        # At requested level in the hierarchy
        if current_level == depth:
            # If request was with depth = 1 and id was provided.
            if component_id != None:
                status_key = self._is_status_present(component, component_id = component_id)
                component_status = self._prapare_component_status(component, component_id = component_id, key = status_key)
                if current_level == start_level:
                    parent.add_health(component_status)
                else:
                    parent.add_resource(component_status)
            else:
                # Prepare and return status for all available components at this level
                while True:
                    status_key = self._is_status_present(component)
                    if status_key == None:
                        break
                    component_status = self._prapare_component_status(component, key = status_key)
                    if current_level == start_level:
                        parent.add_health(component_status)
                    else:
                        parent.add_resource(component_status)
                    del self._status_dict[status_key]
        else:
            # Prepare and return status for all available components at this and further levels
            if component_id != None:
                status_key = self._is_status_present(component, component_id = component_id)
                component_status = self._prapare_component_status(component, component_id = component_id, key = status_key)
                parent.add_health(component_status)
                if status_key:
                    del self._status_dict[status_key]
                else:
                    return
                next_components = self._health_hierarchy.get_next_components(component)
                for _, value in enumerate(next_components):
                    self._prepare_status(value, start_level = start_level, current_level = current_level + 1, depth = depth, parent = component_status)
            else:
                # Prepare and return status for all available components at this and further levels
                while True:
                    status_key = self._is_status_present(component)
                    if status_key == None:
                        break
                    component_status = self._prapare_component_status(component, key = status_key)
                    if current_level == start_level:
                        parent.add_health(component_status)
                    else:
                        parent.add_resource(component_status)
                    del self._status_dict[status_key]
                    next_components = self._health_hierarchy.get_next_components(component)
                    for _, value in enumerate(next_components):
                        self._prepare_status(value, start_level = start_level, current_level = current_level + 1, depth = depth, parent = component_status)

    def _is_status_present(self, component, component_id: str = None) -> str:
        status_key = None
        if component_id is not None:
            for key in self._status_dict:
                if re.search(f"{component}/{component_id}/health", key):
                    status_key = key
                    break
        else:
            for key in self._status_dict:
                if re.search(f"{component}/.+/health", key):
                    split_key = re.split("/", key)
                    if component == split_key[-3]:
                        status_key = key
                        break
        return status_key

    def _prapare_component_status(self, component: str, component_id: str = None, key: str = None) -> object:
            status = HEALTH_STATUSES.UNKNOWN.value
            created_timestamp = HEALTH_STATUSES.UNKNOWN.value
            if key is not None:
                entity_health = self._status_dict[key]
                entity_health = json.loads(entity_health)
                split_key = re.split("/", key)
                component_id = split_key[-2]
                status = entity_health["events"][0]["status"]
                created_timestamp = entity_health['events'][0]['created_timestamp']

            Component_status = ComponentStatus(component, component_id, status, created_timestamp)
            return Component_status

    def get_service_status(self, service_type=None, node_id=None):
        """
        get service status method. This method is for returning a status of a service.
        """

    def get_node_status(self, node_id, **kwargs):
        """
        get node status method. This method is for returning a status of a node.
        """
        try:
            # Prepare key and read the health value.
            key = self._prepare_key(const.COMPONENTS.NODE_MAP.value, node_id=node_id)
            node_map_val = self.healthmanager.get_key(key)
            if node_map_val is not None:
                node_map_dict = ast.literal_eval(node_map_val)
                key = self._prepare_key(component='node', cluster_id=node_map_dict[NODE_MAP_ATTRIBUTES.CLUSTER_ID.value],
                                        site_id=node_map_dict[NODE_MAP_ATTRIBUTES.SITE_ID.value], rack_id=node_map_dict[NODE_MAP_ATTRIBUTES.RACK_ID.value],
                                        storageset_id=node_map_dict[NODE_MAP_ATTRIBUTES.STORAGESET_ID.value], node_id=node_id, **kwargs)
                node_health_dict = json.loads(self.healthmanager.get_key(key))
                node_status = {"status": node_health_dict['events'][0]['status'],
                               "created_timestamp": node_health_dict['events'][0]['created_timestamp']}
                return node_status
            else:
                raise HaSystemHealthException(f"node_id : {node_id} doesn't exist")

        except Exception as e:
            Log.error(f"Failed reading status for component: node with Error: {e}")
            raise HaSystemHealthException(f"Failed reading status for node with node_id : {node_id}")

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
            current_health = self.get_status_raw(component, component_id, comp_type=component_type,
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