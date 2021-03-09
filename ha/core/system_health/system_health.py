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

from cortx.utils.log import Log
from ha import const
from ha.core.system_health.health_event import HealthEvent
from ha.core.system_health.status_mapper import StatusMapper
from ha.core.system_health.entity_health import EntityHealth
from ha.core.system_health.system_health_manager import SystemHealthManager


class HaSystemHealthException(Exception):
    """
    Exception to indicate that some error happened during HA System Health processing.
    """
    pass


class SystemHealth:
    """
    System Health. This class implements an interface to the HA System Health module.
    """

    def __init__(self):
        """
        Init method.
        """
        self.cluster_id =  # TODO: Read from store
        self.node_map = {}
        self.update_hierarchy = ()
        self.statusmapper = StatusMapper()
        self.healthmanager = SystemHealthManager()

    def process_event(self, HealthEvent):
        """
        Process Event method. This method could be called for updating the health status.
        """

        # TODO: Check the user and see if allowed to update the system health.

        try:
            status = self.statusmapper.map_event(HealthEvent.event_type)
            # Check what component the health event is for
            component = HealthEvent.resource_type.split(':')[0]
            if component == const.ENCLOSURE:
                self.update_hierarchy = const.STORAGE_COMPONENT_UPDATE_HIERARCHY
            elif component == const.NODE:
                sub_component = HealthEvent.resource_type.split(':')[1]
                if sub_component == const.SOFTWARE:
                    self.update_hierarchy = const.NODE_SERVICE_UPDATE_HIERARCHY
                else:
                    self.update_hierarchy = const.NODE_HW_UPDATE_HIERARCHY
            else:
                Log.error(f"System health does not support health update for component: {component}")
                raise HaSystemHealthException(f"Health update for an unsupported component: {component}")
                return

            _update(self.update_hierarchy[0], )
            Log.info(f"Updating status for . Output: {machine_id}, Err: {err}, RC: {rc}")

    def _update(self, component, type, id, healthvalue, next_component=None):
    """
    update method. This is an internal method for updating the system health.
    """
        key = self._prepare_key(component,)
        self.system_health_manager.set_key(key, healthvalue)

    def _prepare_key(self, component, **kwargs) -> str:
    """
    Prepare Key. This is an internal method for preparing component status key.
    This will be used when updating/querying a component status.
    """ 

    def get_status(self, component, type, id, **kwargs):
    """
    get status method. This is a generic method which can return status of any component(s).
    """

    def get_service_status(self, type=None, node_id=None):
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