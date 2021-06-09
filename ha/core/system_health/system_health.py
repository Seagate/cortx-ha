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
from ha.core.system_health.cluster_element_factory import ClusterElementFactory

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
        ClusterElementFactory.build_elements()

    def get_service_status(self, service_type=None, node_id=None):
        """
        get service status method. This method is for returning a status of a service.
        """
        pass

    def get_status(self, component: str, component_id: str=None, **kwargs):
        """
        get status method. This is a generic method which can return status of any component(s).
        """
        try:
            cluster_element = ClusterElementFactory.get_element(component)
            return cluster_element.get_status(component, component_id, **kwargs)
        except Exception as e:
            Log.error(f"Failed reading status for component: {component} with Error: {e}")
            raise HaSystemHealthException("Failed reading status")

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

    def process_event(self, healthevent: HealthEvent):
        """
        Process Event method. This method could be called for updating the health status.
        """

        # TODO: Check the user and see if allowed to update the system health.
        try:
            component = SystemHealthComponents.get_component(healthevent.resource_type)
            hierarchy = SystemHealthHierarchy.get_hierarchy(component)
            for element in hierarchy:
                cluster_element = ClusterElementFactory.get_element(component)
                cluster_element.process_event(healthevent)
        except Exception as e:
            Log.error(f"Failed processing system health event with Error: {e}")
            raise HaSystemHealthException("Failed processing system health event")