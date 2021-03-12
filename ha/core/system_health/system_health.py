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

import os
import sys
import pathlib
import re

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))
from ha import const
from ha.core.system_health.health_event import HealthEvent
from ha.core.system_health.status_mapper import StatusMapper
from ha.core.system_health.entity_health import EntityHealth
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

    def _prepare_key(self, component, **kwargs) -> str:
        """
        Prepare Key. This is an internal method for preparing component status key.
        This will be used when updating/querying a component status.
        """

        # Get the key template.
        key = const.SYSTEM_HEALTH_KEYS[component]
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

    def get_status(self, component, component_id, **kwargs):
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
    def _update(self, component, comp_type, comp_id, healthvalue, next_component=None):
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
            # Get system health component from the resource type in the event
            component = None
            for key in const.SYSTEM_HEALTH_COMPONENTS:
                for item in const.SYSTEM_HEALTH_COMPONENTS[key][const.RESOURCE_LIST]:
                    if item in healthevent.resource_type:
                        component = key
                        self.update_hierarchy = const.SYSTEM_HEALTH_COMPONENTS[key][const.UPDATE_HIERARCHY]
                        break
                if component:
                    break

            if component is None:
                # System health does not support ths component.
                Log.error(f"System health does not support health update for component: {component}")
                raise HaSystemHealthException(f"Health update for an unsupported component: {component}")

            # Get the component type and id received in the event.
            if (len(self.update_hierarchy) - 1) > self.update_hierarchy.index(component):
                next_component = self.update_hierarchy[self.update_hierarchy.index(component) + 1]
            else:
                next_component = None
            component_type = healthevent.resource_type.split(':')[-1]
            component_id = healthevent.resource_id
            # Read the currently stored health value
            current_health = self.get_status(component, component_id, comp_type=component_type,
                                        cluster_id=healthevent.cluster_id, site_id=healthevent.site_id,
                                        rack_id=healthevent.rack_id, storageset_id=healthevent.storageset_id,
                                        node_id=healthevent.node_id, server_id=healthevent.node_id,
                                        storage_id=healthevent.node_id)

            # Get the updated health value
            updated_health = EntityHealth(healthevent.timestamp, status, const.ACTION_STATUS.PENDING.value,
                                          previous_health=current_health)
            # Update the node map
            self.node_id = healthevent.node_id
            self.node_map = {'cluster_id':healthevent.cluster_id, 'site_id':healthevent.site_id,
                             'rack_id':healthevent.rack_id, 'storageset_id':healthevent.storageset_id}

            self._update(component, component_type, component_id, updated_health, next_component=next_component)
            Log.info(f"Updated health for component: {component}, Type: {component_type}, Id: {component_id}")

        except Exception as e:
            Log.error(f"Failed processing system health event with Error: {e}")
            raise HaSystemHealthException("Failed processing system health event")

def main(argv: dict):
    pass

if __name__ == '__main__':
    # TODO: Import and use config_manager.py
    Conf.init(delim='.')
    Conf.load(const.HA_GLOBAL_INDEX, f"yaml://{const.SOURCE_CONFIG_FILE}")
    log_path = Conf.get(const.HA_GLOBAL_INDEX, "LOG.path")
    log_level = Conf.get(const.HA_GLOBAL_INDEX, "LOG.level")
    Log.init(service_name='ha_system_health', log_path=log_path, level=log_level)
    sys.exit(main(sys.argv))