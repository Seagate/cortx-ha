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
from ha.core.error import HaSystemHealthComponentsException, HaSystemHealthHierarchyException

class SystemHealthComponents:
    """
    System Health Components. This class provides a method for fetching component/key
    associated with the resource type received in the health event.
    """

    # Components/resources maintained by System Health module. Note: Do not change the order.
    _components = {const.COMPONENTS.SERVER_HARDWARE.value: {const.RESOURCE_LIST: ["node:fru", "node:sensor", "node:os", "node:interface"],
                                                            const.KEY: "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/server/$server_id/hw/$comp_type/$comp_id/health"},
                   const.COMPONENTS.SERVER_SERVICE.value: {const.RESOURCE_LIST: ["node:sw"],
                                                           const.KEY: "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/server/$server_id/service/$comp_type/$comp_id/health"},
                   const.COMPONENTS.SERVER.value: {const.RESOURCE_LIST: ["server"],
                                                   const.KEY: "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/server/$server_id/health"},
                   const.COMPONENTS.STORAGESET.value: {const.RESOURCE_LIST: ["storageset"],
                                                       const.KEY: "/cortx/ha/system/cluster/$cluster_id/storageset/$storageset_id/health"},
                   const.COMPONENTS.STORAGE_COMPONENT.value: {const.RESOURCE_LIST: ["enclosure"],
                                                              const.KEY: "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/storage/$storage_id/hw/$comp_type/$comp_id/health"},
                   const.COMPONENTS.STORAGE.value: {const.RESOURCE_LIST: ["storage"],
                                                    const.KEY: "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/storage/$storage_id/health"},
                   const.COMPONENTS.NODE.value: {const.RESOURCE_LIST: ["node"],
                                                 const.KEY: "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/node/$node_id/health"},
                   const.COMPONENTS.RACK.value: {const.RESOURCE_LIST: ["rack"],
                                                 const.KEY: "/cortx/ha/system/cluster/$cluster_id/site/$site_id/rack/$rack_id/health"},
                   const.COMPONENTS.SITE.value: {const.RESOURCE_LIST: ["site"],
                                                 const.KEY: "/cortx/ha/system/cluster/$cluster_id/site/$site_id/health"},
                   const.COMPONENTS.CLUSTER.value: {const.RESOURCE_LIST: ["cluster"],
                                                    const.KEY: "/cortx/ha/system/cluster/$cluster_id/health"},
                   const.COMPONENTS.AGG_SERVICE.value: {const.RESOURCE_LIST: [],
                                                        const.KEY: "/cortx/ha/system/cluster/$cluster_id/service/$comp_type/$comp_id/aggregate"},
                   const.COMPONENTS.NODE_MAP.value: {const.RESOURCE_LIST: [],
                                                     const.KEY: "/cortx/ha/system/cluster/node_map/$node_id"}}

    @staticmethod
    def get_component(resource_type: str) -> str:
        """
        This method returns a component associated with a resource type,
        received in the health event.
        """

        try:
            # Get system health component using the resource type
            for key in SystemHealthComponents._components:
                for item in SystemHealthComponents._components[key][const.RESOURCE_LIST]:
                    if item in resource_type:
                        return key

            # System health does not support this component.
            Log.error(f"System health does not support health update for resource type: {resource_type}")
            raise HaSystemHealthComponentsException(f"Health update for an unsupported resource type: {resource_type}")

        except Exception as e:
            Log.error(f"Failed to get component with Error: {e}")
            raise HaSystemHealthComponentsException("Failed to get component")

    @staticmethod
    def get_key(component: str) -> str:
        """
        This method returns a key for a component, this key is used for storing/retrieving
        the component health value in the store.
        """

        try:
            # return the key of the component
            return SystemHealthComponents._components[component][const.KEY]

        except KeyError as e:
            Log.error(f"Key is not available for the {component} with Error: {e}")
            raise HaSystemHealthComponentsException("Key is not available for the component")

        except Exception as e:
            Log.error(f"Failed to get {component} with Error: {e}")
            raise HaSystemHealthComponentsException("Failed to get component")

class SystemHealthHierarchy:
    """
    System Health Hierarchy. This class provides system health component health update hierarchy.
    """

    _common_hierarchy = [const.COMPONENTS.NODE.value, const.COMPONENTS.RACK.value, const.COMPONENTS.SITE.value,
                         const.COMPONENTS.CLUSTER.value]
    _server = [const.COMPONENTS.SERVER.value] + _common_hierarchy
    _server_service = [const.COMPONENTS.SERVER_SERVICE.value, const.COMPONENTS.AGG_SERVICE.value] + _server
    _server_hw = [const.COMPONENTS.SERVER_HARDWARE.value] + _server
    _storage = [const.COMPONENTS.STORAGE_COMPONENT.value,  const.COMPONENTS.STORAGE.value] + _common_hierarchy

    @staticmethod
    def get_hierarchy(component: str) -> dict:
        """
        This method returns a component health update hierarchy.
        """

        try:
            if component in SystemHealthHierarchy._server_hw:
                return SystemHealthHierarchy._server_hw[SystemHealthHierarchy._server_hw.index(component):]
            elif component in SystemHealthHierarchy._server_service:
                return SystemHealthHierarchy._server_service[SystemHealthHierarchy._server_service.index(component):]
            elif component in SystemHealthHierarchy._storage:
                return SystemHealthHierarchy._storage[SystemHealthHierarchy._storage.index(component) : ]
            else:
                Log.error(f"Health update hierarchy not present for component: {component}")
                raise HaSystemHealthHierarchyException("Health update hierarchy not present for the component")

        except Exception as e:
            Log.error(f"Failed to get health update hierarchy for component with Error: {e}")
            raise HaSystemHealthHierarchyException("Failed to get health update hierarchy")