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
import uuid

from cortx.utils.log import Log

from ha import const
from ha.util.message_bus import MessageBus
from cortx.utils.conf_store.conf_store import Conf
from ha.const import _DELIM, CLUSTER_CONFSTORE_PREFIX
from ha.core.config.config_manager import ConfigManager
from ha.core.system_health.health_evaluators.element_health_evaluator import ElementHealthEvaluator
from ha.core.system_health.const import EVENT_SEVERITIES, NODE_MAP_ATTRIBUTES
from ha.core.event_analyzer.subscriber import Subscriber
from ha.core.system_health.system_health_metadata import SystemHealthComponents, SystemHealthHierarchy
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.model.entity_health import EntityEvent, EntityAction, EntityHealth
from ha.core.system_health.status_mapper import StatusMapper
from ha.core.system_health.system_health_manager import SystemHealthManager
from ha.core.error import HaSystemHealthException
from ha.core.system_health.health_evaluator_factory import HealthEvaluatorFactory
from ha.core.cluster.const import SYSTEM_HEALTH_OUTPUT_V2, GET_SYS_HEALTH_ARGS
from ha.core.system_health.const import CLUSTER_ELEMENTS, HEALTH_STATUSES, HEALTH_EVENT_ACTIONS, HEALTH_EVENTS
from ha.core.system_health.model.health_status import StatusOutput, ComponentStatus
from ha.core.system_health.system_health_hierarchy import HealthHierarchy
from ha.core.event_manager.resources import RESOURCE_TYPES
from ha.fault_tolerance.const import HEALTH_EVENT_SOURCES

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
        # TODO: Convert SystemHealthManager to singleton class
        self.healthmanager = SystemHealthManager(store)
        HealthEvaluatorFactory.init_evaluators()
        # TODO: Temporary code remove when all status method moved to evaluators
        self.health_evaluator = HealthEvaluatorFactory.get_generic_evaluator()
        self.producer = self._get_producer()
        Log.info("All cluster element are loaded, Ready to process alerts .................")

    def _get_producer(self):
        message_type = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_MANAGER{_DELIM}message_type")
        producer_id = Conf.get(const.HA_GLOBAL_INDEX, f"EVENT_MANAGER{_DELIM}producer_id")
        return MessageBus.get_producer(producer_id, message_type)

    def _prepare_key(self, component: str, **kwargs) -> str:
        """
        Prepare Key. This is an internal method for preparing component status key.
        This will be used when updating/querying a component status.
        """
        return ElementHealthEvaluator.prepare_key(component, **kwargs)

    def get_status_raw(self, component: str, component_id: str=None, **kwargs):
        """
        get status method. This is a generic method which can return status of any component(s).
        """
        return self.health_evaluator.get_status_raw(component, component_id, **kwargs)

    def get_status(self, component: CLUSTER_ELEMENTS = CLUSTER_ELEMENTS.CLUSTER.value, depth: int = 1, version: str = SYSTEM_HEALTH_OUTPUT_V2, **kwargs):
        """
        Return health status for the requested components.
        Args:
            component ([CLUSTER_ELEMENTS]): The component whose health status is to be returned.
            depth ([int]): A depth of elements starting from the input "component" that the health status
                is to be returned.
            version ([str]): The health status json output version
            **kwargs([dict]): Variable number of arguments that are used as filters,
                e.g. "id" of the input "component".
        Returns:
            ([dict]): Returns dictionary. {"status": "Succeeded"/"Failed"/"Partial", "output": "", "error": ""}
                status: Succeeded, Failed, Partial
                output: Dictionary with element health status
                error: Error information if the request "Failed"
        """

        try:
            Log.debug(f"Get {component} health status version {version} with depth {depth} and filters {kwargs}")
            component_id = None
            if GET_SYS_HEALTH_ARGS.ID.value in kwargs and kwargs[GET_SYS_HEALTH_ARGS.ID.value] != "":
                component_id = kwargs[GET_SYS_HEALTH_ARGS.ID.value]

            # Get the requested component level in the health hierarchy
            component_level = HealthHierarchy.get_component_level(component)
            # Set the depth to be returned, check for partial status.
            self._partial_status = False
            total_depth = HealthHierarchy.get_total_depth()
            if depth == 0:
                depth = total_depth
            else:
                depth += component_level - 1 # Decrement by 1 for the component level itself.
                if depth > HealthHierarchy.get_total_depth():
                    depth = total_depth
                    self._partial_status = True
            Log.debug(f"{component} level {component_level}, depth to return {depth}, total available depth {total_depth}")

            self._id_not_found = False
            # Get raw status starting from cluster
            self._status_dict = self.get_status_raw(CLUSTER_ELEMENTS.CLUSTER.value)
            # Prepare and return the output
            output = StatusOutput(version)
            self._prepare_status(component, component_id = component_id, start_level = component_level, current_level = component_level, depth = depth, parent = output)
            status = const.STATUSES.SUCCEEDED.value
            if self._partial_status:
                status = const.STATUSES.PARTIAL.value
            if self._id_not_found:
                output_json = json.dumps({"status": const.STATUSES.FAILED.value, "output": "", "error": "Invalid id"})
            else:
                output_json = json.dumps({"status": status, "output": json.loads(output.to_json()), "error": ""})
            Log.debug(f"Output json {output_json}")
            return output_json
        except Exception as e:
            Log.error(f"Failed reading status. Error: {e}")
            raise HaSystemHealthException("Failed reading status")

    def _prepare_status(self, component, component_id: str = None, start_level: int = 1, current_level: int = 1, depth: int = 1, parent: object = None):
        Log.debug(f"Prepare status for component {component}, id {component_id}, level {current_level}, depth {depth}")
        # At requested level in the hierarchy
        if current_level == depth:
            # If request was with depth = 1 and id was provided.
            if component_id != None:
                status_key = self._is_status_present(component, component_id = component_id)
                if status_key is None:
                    self._id_not_found = True
                    return
                component_status = self._prapare_component_status(component, component_id = component_id, key = status_key)
                parent.add_health(component_status)
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
                if status_key is None:
                    self._id_not_found = True
                    return
                component_status = self._prapare_component_status(component, component_id = component_id, key = status_key)
                parent.add_health(component_status)
                del self._status_dict[status_key]
                next_components = HealthHierarchy.get_next_components(component)
                for _, value in enumerate(next_components):
                    self._prepare_status(value, start_level = start_level, current_level = current_level + 1, depth = depth, parent = component_status)
            else:
                # Prepare and return status for all available components at this and further levels
                found_any_components = False
                while True:
                    status_key = self._is_status_present(component)
                    if status_key == None:
                        break
                    found_any_components = True
                    component_status = self._prapare_component_status(component, key = status_key)
                    if current_level == start_level:
                        parent.add_health(component_status)
                    else:
                        parent.add_resource(component_status)
                    del self._status_dict[status_key]
                    next_components = HealthHierarchy.get_next_components(component)
                    for _, value in enumerate(next_components):
                        self._prepare_status(value, start_level = start_level, current_level = current_level + 1, depth = depth, parent = component_status)
                if found_any_components == False:
                    self._partial_status = True

    def _is_status_present(self, component, component_id: str = None) -> str:
        status_key = None
        if component_id is not None:
            for key in self._status_dict:
                if re.search(f"{component}{const.HA_DELIM}{component_id}{const.HA_DELIM}health", key):
                    status_key = key
                    break
        else:
            for key in self._status_dict:
                if re.search(f"{component}{const.HA_DELIM}.+{const.HA_DELIM}health", key):
                    split_key = re.split(const.HA_DELIM, key)
                    if component == split_key[-3]:
                        status_key = key
                        break
        Log.debug(f"Status key {status_key} present for component {component}, id {component_id}")
        return status_key

    def _prapare_component_status(self, component: str, component_id: str = None, key: str = None) -> object:
            status = HEALTH_STATUSES.UNKNOWN.value
            created_timestamp = HEALTH_STATUSES.UNKNOWN.value
            if key is not None:
                entity_health = self._status_dict[key]
                entity_health = json.loads(entity_health)
                split_key = re.split(const.HA_DELIM, key)
                component_id = split_key[-2]
                status = entity_health["events"][0]["status"]
                created_timestamp = entity_health['events'][0]['created_timestamp']

            component_status = ComponentStatus(component, component_id, status, created_timestamp)
            Log.debug(f"Component {component}, id {component_id} health status is {component_status.to_json()}")
            return component_status

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
        pass

    def _is_update_required(self, current_health: str, updated_health: str, event: HealthEvent) -> HEALTH_EVENT_ACTIONS:
        """
        Check if update is needed for system health.

        Args:
            current_health (dict): current health.
            healthevent (HealthEvent): health event object.

        Returns:
            HEALTH_EVENT_ACTIONS
        """
        event_action: HEALTH_EVENT_ACTIONS = HEALTH_EVENT_ACTIONS.UPDATEPUBLISH.value
        if not current_health:
            return event_action
        old_health = json.loads(current_health)
        new_health = json.loads(updated_health)
        old_status = old_health["events"][0]["status"]
        new_status = new_health["events"][0]["status"]

        # Common cases
        if old_status == new_status:
            event_action = HEALTH_EVENT_ACTIONS.IGNORE.value

        # specific cases
        # 1. Do not overwrite node status to failed if offline already
        if event.resource_type == RESOURCE_TYPES.NODE.value and \
            old_status == HEALTH_STATUSES.OFFLINE.value and new_status == HEALTH_STATUSES.FAILED.value:
            Log.info(f"Updating is not needed node is in {old_status} and received {new_status}")
            event_action = HEALTH_EVENT_ACTIONS.IGNORE.value
        return event_action

    def publish_event(self, healthevent: HealthEvent):
        """
        Produce event
        """
        node_id = healthevent.node_id
        self.producer.publish(str(healthevent))
        healthevent.node_id = node_id

    def _update(self, healthevent: HealthEvent, healthvalue: str, next_component: str=None):
        """
        update method. This is an internal method for updating the system health.
        """
        component = SystemHealthComponents.get_component(healthevent.resource_type)
        comp_type = healthevent.resource_type.split(':')[-1]
        comp_id = healthevent.resource_id

        key = self._prepare_key(component, cluster_id=self.node_map['cluster_id'], site_id=self.node_map['site_id'],
                                rack_id=self.node_map['rack_id'], storageset_id=self.node_map['storageset_id'],
                                node_id=self.node_id, server_id=self.node_id, storage_id=self.node_id,
                                comp_type=comp_type, comp_id=comp_id, cvg_id=self.cvg_id)
        is_key_exists = self.healthmanager.key_exists(key)
        self.healthmanager.set_key(key, healthvalue)
        if is_key_exists:
            self.publish_event(healthevent)

        # Check the next component to be updated, if none then return.
        if next_component is None:
            Log.info(f"SystemHealth: Updated status for {component}:{comp_type}:{comp_id}")
            return
        else:
            Log.info(f"SystemHealth: Updated status for {component}:{comp_type}:{comp_id}")
            Log.info(f"Updating element {next_component} status")
            element = HealthEvaluatorFactory.get_element_evaluator(next_component)
            new_event = element.evaluate_status(healthevent)
            self.process_event(new_event)
            return

    @staticmethod
    def create_updated_event_object(event_timestamp: str, current_timestamp: str, status: str, spec_info: dict, updated_health: EntityHealth) -> str:
        """
        Creates objects of EntityEvent and EntityAction using incoming
        health status(coming from incoming health event from parser) and
        other required values and adds it to the latest health object.
        converts it to a appropriate format which needs to be updated in
        the system health
        """
        # Create a new event and action
        entity_event = EntityEvent(event_timestamp, current_timestamp, status, spec_info)
        entity_action = EntityAction(current_timestamp, const.ACTION_STATUS.PENDING.value)
        # Add the new event and action to the health value
        updated_health.add_event(entity_event)
        updated_health.set_action(entity_action)
        # Convert the health value as appropriate for writing to the store.
        updated_health = EntityHealth.write(updated_health)
        return updated_health

    def _check_and_update(self, current_health: str, updated_health: str, healthevent: HealthEvent, next_component: str) -> None:
        # Update in the store.
        update_action = self._is_update_required(current_health, updated_health, healthevent)
        if update_action != HEALTH_EVENT_ACTIONS.IGNORE.value:
            self._update(healthevent, updated_health, next_component=next_component)

    def _get_cvg_list(self, healthevent, match_with):
        """
        Parse system health key and get cvg id for matching criteria.
        Args:
            healthevent: health event of resource
            match_with : Additional resource information to be matched with expecting key
        Returns:
            List of cvg ids.
        """
        cvg_list = []
        cluster_prefix = self._prepare_key(CLUSTER_ELEMENTS.CLUSTER.value,
                                           cluster_id=healthevent.cluster_id)
        cluster_key = _DELIM.join(cluster_prefix.split(_DELIM)[:-1])
        key_prefix = f"{CLUSTER_CONFSTORE_PREFIX.strip(_DELIM)}{cluster_key}"
        cvg_list = self.healthmanager.parse_key(CLUSTER_ELEMENTS.CVG.value,
                                                match_with, key_prefix)
        if not cvg_list:
            Log.error(f"Failed to get cvg_id for {healthevent.resource_id} of node {self.node_id}")
        return cvg_list

    def process_event(self, healthevent: HealthEvent):
        """
        Process Event method. This method could be called for updating the health status.
        """

        # TODO: Check the user and see if allowed to update the system health.
        try:
            status = self.statusmapper.map_event(healthevent)
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
            Log.info(f"SystemHealth: Processing {component}:{component_type}:{component_id} with status {status}")

            # Update the node map
            self.node_id = healthevent.node_id
            self.cvg_id = None
            if component_type == CLUSTER_ELEMENTS.DISK.value:
                if not isinstance(healthevent.specific_info, dict):
                    healthevent.specific_info = {}
                if healthevent.specific_info.get(NODE_MAP_ATTRIBUTES.CVG_ID.value):
                    self.cvg_id = healthevent.specific_info[NODE_MAP_ATTRIBUTES.CVG_ID.value]
                else:
                    match_criteria = {CLUSTER_ELEMENTS.NODE.value: self.node_id,
                                      component_type: component_id}
                    cvg_list = self._get_cvg_list(healthevent, match_criteria)
                    self.cvg_id = cvg_list[0] if cvg_list else None
                    healthevent.specific_info[NODE_MAP_ATTRIBUTES.CVG_ID.value] = self.cvg_id

            self.node_map = {'cluster_id':healthevent.cluster_id, 'site_id':healthevent.site_id,
                    'rack_id':healthevent.rack_id, 'storageset_id':healthevent.storageset_id}

            # Read the currently stored health value
            current_health = self.get_status_raw(component, component_id, comp_type=component_type,
                                        cluster_id=healthevent.cluster_id, site_id=healthevent.site_id,
                                        rack_id=healthevent.rack_id, storageset_id=healthevent.storageset_id,
                                        node_id=healthevent.node_id, server_id=healthevent.node_id,
                                        storage_id=healthevent.node_id, cvg_id=self.cvg_id)

            current_timestamp = str(int(time.time()))
            if current_health:
                current_health_dict = json.loads(current_health)
                specific_info = current_health_dict["events"][0]["specific_info"]
                if (component_type == CLUSTER_ELEMENTS.NODE.value) and specific_info \
                    and healthevent.source == HEALTH_EVENT_SOURCES.MONITOR.value:
                    # If health is already stored and its a node_health, check further
                    stored_genration_id = current_health_dict["events"][0]["specific_info"]["generation_id"]
                    incoming_generation_id = healthevent.specific_info["generation_id"]
                    incoming_health_status = healthevent.event_type
                    pod_restart_val = current_health_dict["events"][0]["specific_info"]["pod_restart"]
                    # Update the current health value itself.
                    latest_health = EntityHealth.read(current_health)
                    if stored_genration_id and (stored_genration_id != incoming_generation_id):
                        if incoming_health_status == HEALTH_EVENTS.ONLINE.value:
                            # In delete scenario, online event comes first, followed by failed event.
                            # System health is expected to update the failed event first, then online event.
                            # If incoming is online event, change the stored event type to failed.
                            # Update the failed event in system health and followed by incoming online event.
                            healthevent.specific_info = {"generation_id": stored_genration_id, "pod_restart": 1}
                            healthevent.event_type = "failed"
                            updated_health = SystemHealth.create_updated_event_object(healthevent.timestamp, current_timestamp, healthevent.event_type, healthevent.specific_info, latest_health)
                            # Create a "failed" event and update it in system health and publish
                            self._check_and_update(current_health, updated_health, healthevent, next_component)
                            current_health = updated_health
                            # Now create an "online" event and update it in system health and publish
                            healthevent.specific_info = {"generation_id": incoming_generation_id, "pod_restart": 1}
                            healthevent.event_type = "online"
                            updated_health = SystemHealth.create_updated_event_object(healthevent.timestamp, current_timestamp, healthevent.event_type, healthevent.specific_info, latest_health)
                            self._check_and_update(current_health, updated_health, healthevent, next_component)
                        elif pod_restart_val is not None and pod_restart_val:
                            # Check the pod_restart value associated with Node, if its 1,
                            # means this alert is already updated. No need to send the alert again.
                            # Just need to reset the pod_restart value
                            key = self._prepare_key(component, cluster_id=self.node_map['cluster_id'], \
                                site_id=self.node_map['site_id'], rack_id=self.node_map['rack_id'], \
                                node_id=self.node_id)
                            latest_health_dict = json.loads(current_health)
                            new_spec_info = {"generation_id": stored_genration_id, "pod_restart": 0}
                            latest_health_dict["events"][0]["specific_info"] = new_spec_info
                            updated_health = EntityHealth.write(latest_health_dict)
                            self.healthmanager.set_key(key, updated_health)
                    else:
                        # current health is there and generation id is also already present.
                        # That means its a normal failure scenario
                        updated_health = SystemHealth.create_updated_event_object(healthevent.timestamp, current_timestamp, status, healthevent.specific_info, latest_health)
                        self._check_and_update(current_health, updated_health, healthevent, next_component)
                else:
                    # Update hierarchical components. such as site, rack
                    latest_health = EntityHealth.read(current_health)
                    updated_health = SystemHealth.create_updated_event_object(healthevent.timestamp, current_timestamp, status, healthevent.specific_info, latest_health)
                    self._check_and_update(current_health, updated_health, healthevent, next_component)
            else:
                # Health value not present in the store currently, create now.
                latest_health = EntityHealth()
                updated_health = SystemHealth.create_updated_event_object(healthevent.timestamp, current_timestamp, status, healthevent.specific_info, latest_health)
                self._check_and_update(current_health, updated_health, healthevent, next_component)
        except Exception as err:
            Log.error(f"Failed processing system health event with Error: {err}")
            raise HaSystemHealthException("Failed processing system health event")

    def get_health_event_template(self, nodeid: str, event_type: str, source: str) -> dict:
        """
        Create health event
        Args:
            source: Source (Ex: monitor, hare) who wants this event template
            nodeid (str): nodeid
            event_type (str): event type will be offline, online, failed

        Returns:
            dict: Return dictionary of health event
        """
        key = self._prepare_key(const.COMPONENTS.NODE_MAP.value, node_id=nodeid)
        node_map_val = self.healthmanager.get_key(key)
        if node_map_val is None:
            raise HaSystemHealthException("Failed to fetch node_map value")
        node_map_dict = ast.literal_eval(node_map_val)

        timestamp = str(int(time.time()))
        event_id = timestamp + str(uuid.uuid4().hex)
        initial_event = {
            const.EVENT_ATTRIBUTES.SOURCE: source,
            const.EVENT_ATTRIBUTES.EVENT_ID : event_id,
            const.EVENT_ATTRIBUTES.EVENT_TYPE : event_type,
            const.EVENT_ATTRIBUTES.SEVERITY : EVENT_SEVERITIES.WARNING.value,
            const.EVENT_ATTRIBUTES.SITE_ID : node_map_dict[NODE_MAP_ATTRIBUTES.SITE_ID.value],
            const.EVENT_ATTRIBUTES.RACK_ID : node_map_dict[NODE_MAP_ATTRIBUTES.RACK_ID.value],
            const.EVENT_ATTRIBUTES.CLUSTER_ID : node_map_dict[NODE_MAP_ATTRIBUTES.CLUSTER_ID.value],
            const.EVENT_ATTRIBUTES.STORAGESET_ID : node_map_dict[NODE_MAP_ATTRIBUTES.STORAGESET_ID.value],
            const.EVENT_ATTRIBUTES.NODE_ID : nodeid,
            const.EVENT_ATTRIBUTES.HOST_ID : node_map_dict[NODE_MAP_ATTRIBUTES.HOST_ID.value],
            const.EVENT_ATTRIBUTES.RESOURCE_TYPE : CLUSTER_ELEMENTS.NODE.value,
            const.EVENT_ATTRIBUTES.TIMESTAMP : timestamp,
            const.EVENT_ATTRIBUTES.RESOURCE_ID : nodeid,
            const.EVENT_ATTRIBUTES.SPECIFIC_INFO : None
        }
        return initial_event
