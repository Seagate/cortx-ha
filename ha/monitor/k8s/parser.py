#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>. For any questions
# about this software or licensing, please email opensource@seagate.com or
# cortx-questions@seagate.com.


import time

from ha.monitor.k8s.error import NotSupportedObjectError
from ha.monitor.k8s.const import K8SEventsConst
from ha.monitor.k8s.const import AlertStates, AlertResourceType
from ha.monitor.k8s.const import EventStates

from cortx.utils.log import Log
from ha.fault_tolerance.event import Event
from ha.fault_tolerance.const import HEALTH_ATTRIBUTES, HEALTH_EVENT_SOURCES


class ObjectParser:
    def __init__(self):
        self.payload = {HEALTH_ATTRIBUTES.SOURCE.value: HEALTH_EVENT_SOURCES.MONITOR.value, \
                    HEALTH_ATTRIBUTES.CLUSTER_ID.value: None, HEALTH_ATTRIBUTES.SITE_ID.value: None, \
                    HEALTH_ATTRIBUTES.RACK_ID.value: None, HEALTH_ATTRIBUTES.STORAGESET_ID.value: None, \
                    HEALTH_ATTRIBUTES.NODE_ID.value: None, HEALTH_ATTRIBUTES.RESOURCE_TYPE.value: None, \
                    HEALTH_ATTRIBUTES.RESOURCE_ID.value: None, HEALTH_ATTRIBUTES.RESOURCE_STATUS.value: None, \
                    HEALTH_ATTRIBUTES.SPECIFIC_INFO.value: {}}

    def parse(self, an_event, cached_state):
        pass


class NodeEventParser(ObjectParser):
    def __init__(self):
        super().__init__()
        self._type = AlertResourceType.HOST

    def _create_health_alert(self, res_type: str, res_name: str, health_status: str) -> dict:
        """
        Instantiates Event class which creates Health event object with necessary
        attributes to pass it for further processing.

        Args:
        res_type: resource_type for which event needs to be created. Ex: node, disk
        res_name: actual resource name. Ex: machine_id in case of node alerts
        health_status: health of that resource. Ex: online, failed
        """
        self.event = Event()
        self.payload[HEALTH_ATTRIBUTES.RESOURCE_TYPE.value] = res_type
        self.payload[HEALTH_ATTRIBUTES.RESOURCE_ID.value] = self.payload[HEALTH_ATTRIBUTES.NODE_ID.value] = res_name
        self.payload[HEALTH_ATTRIBUTES.RESOURCE_STATUS.value] = health_status
        self.event.set_payload(self.payload)
        return self.event.ret_dict()

    def parse(self, an_event, cached_state):
        resource_type = self._type
        raw_object = an_event[K8SEventsConst.RAW_OBJECT]

        if K8SEventsConst.TYPE in an_event:
            event_type = an_event[K8SEventsConst.TYPE]
        if K8SEventsConst.NAME in raw_object[K8SEventsConst.METADATA]:
            resource_name = raw_object[K8SEventsConst.METADATA][K8SEventsConst.NAME]

        ready_status = None
        try:
            for a_condition in raw_object[K8SEventsConst.STATUS][K8SEventsConst.CONDITIONS]:
                if a_condition[K8SEventsConst.TYPE] == K8SEventsConst.READY:
                    ready_status = a_condition[K8SEventsConst.STATUS]
        except Exception as e:
            Log.debug(f"Exception received during parsing {e}")

        if ready_status is None:
            Log.debug(f"ready_status is None for node resource {resource_name}")
            cached_state[resource_name] = ready_status
            return None

        if event_type == EventStates.ADDED:
            cached_state[resource_name] = ready_status.lower()
            if ready_status.lower() == K8SEventsConst.true:
                event_type = AlertStates.ONLINE
                health_alert = self._create_health_alert(resource_type, resource_name, event_type)
                return health_alert, self.event
            else:
                Log.debug(f"[EventStates ADDED] No change detected for node resource {resource_name}")
                return None

        if event_type == EventStates.MODIFIED:
            if resource_name in cached_state:
                if cached_state[resource_name] != K8SEventsConst.true and ready_status.lower() == K8SEventsConst.true:
                    cached_state[resource_name] = ready_status.lower()
                    event_type = AlertStates.ONLINE
                    health_alert = self._create_health_alert(resource_type, resource_name, event_type)
                    return health_alert, self.event
                elif cached_state[resource_name] == K8SEventsConst.true and ready_status.lower() != K8SEventsConst.true:
                    cached_state[resource_name] = ready_status.lower()
                    event_type = AlertStates.FAILED
                    health_alert = self._create_health_alert(resource_type, resource_name, event_type)
                    return health_alert, self.event
                else:
                    Log.debug(f"[EventStates MODIFIED] No change detected for node resource {resource_name}")
                    return None
            else:
                Log.debug(f"[EventStates MODIFIED] No cached state detected for node resource {resource_name}")
                return None

        # Handle DELETED event - Not required for Cortx

        return None


class PodEventParser(ObjectParser):
    def __init__(self):
        super().__init__()

        # Note: The below type is not a Kubernetes 'node'.
        #       in cortx cluster the pod is called or considered as a node.
        #       hence while sending alert to cortx, below type is set to 'node'.
        self._type = AlertResourceType.NODE

    def _create_health_alert(self, res_type, res_name, health_status, generation_id):
        """
        Instantiates Event class which creates Health event object with necessary
        attributes to pass it for further processing.

        Args:
        res_type: resource_type for which event needs to be created. Ex: node, disk
        res_name: actual resource name. Ex: machine_id in case of node alerts
        health_status: health of that resource. Ex: online, failed
        generation_id: name of the node in case of node alert
        """
        self.event = Event()
        self.payload[HEALTH_ATTRIBUTES.RESOURCE_TYPE.value] = res_type
        self.payload[HEALTH_ATTRIBUTES.RESOURCE_ID.value] = self.payload[HEALTH_ATTRIBUTES.NODE_ID.value] = res_name
        self.payload[HEALTH_ATTRIBUTES.RESOURCE_STATUS.value] = health_status
        self.payload[HEALTH_ATTRIBUTES.SPECIFIC_INFO.value]["generation_id"] = generation_id
        self.event.set_payload(self.payload)
        return self.event.ret_dict()

    def parse(self, an_event, cached_state):
        resource_type = self._type
        raw_object = an_event[K8SEventsConst.RAW_OBJECT]

        labels = raw_object[K8SEventsConst.METADATA][K8SEventsConst.LABELS]
        if K8SEventsConst.MACHINEID in labels:
            resource_name = labels[K8SEventsConst.MACHINEID]
        if K8SEventsConst.TYPE in an_event:
            event_type = an_event[K8SEventsConst.TYPE]
        # Actual physical host information is not needed now.
        # If required, can be available in K8SEventsConst.SPEC.
        # So, removing it from now.
        if K8SEventsConst.NAME in raw_object[K8SEventsConst.METADATA]:
            generation_id = raw_object[K8SEventsConst.METADATA][K8SEventsConst.NAME]

        ready_status = None
        try:
            for a_condition in raw_object[K8SEventsConst.STATUS][K8SEventsConst.CONDITIONS]:
                if a_condition[K8SEventsConst.TYPE] == K8SEventsConst.READY:
                    ready_status = a_condition[K8SEventsConst.STATUS]
        except Exception as e:
            Log.debug(f"Exception received during parsing {e}")

        if ready_status is None:
            Log.debug(f"ready_status is None for pod resource {resource_name}")
            cached_state[resource_name] = ready_status
            return None

        if an_event[K8SEventsConst.TYPE] == EventStates.ADDED:
            cached_state[resource_name] = ready_status.lower()
            if ready_status.lower() != K8SEventsConst.true:
                Log.debug(f"[EventStates ADDED] No change detected for pod resource {resource_name}")
                return None
            else:
                event_type = AlertStates.ONLINE
                health_alert = self._create_health_alert(resource_type, resource_name, event_type, generation_id)
                return health_alert, self.event

        if event_type == EventStates.MODIFIED:
            if resource_name in cached_state:
                if cached_state[resource_name] != K8SEventsConst.true and ready_status.lower() == K8SEventsConst.true:
                    cached_state[resource_name] = ready_status.lower()
                    event_type = AlertStates.ONLINE
                    health_alert = self._create_health_alert(resource_type, resource_name, event_type, generation_id)
                    return health_alert, self.event
                elif cached_state[resource_name] == K8SEventsConst.true and ready_status.lower() != K8SEventsConst.true:
                    cached_state[resource_name] = ready_status.lower()
                    event_type = AlertStates.FAILED
                    health_alert = self._create_health_alert(resource_type, resource_name, event_type, generation_id)
                    return health_alert, self.event
                else:
                    Log.debug(f"[EventStates MODIFIED] No change detected for pod resource {resource_name}")
                    return None
            else:
                Log.debug(f"[EventStates MODIFIED] No cached state detected for pod resource {resource_name}")
                return None

        # Handle DELETED event - Not required for Cortx

        return None


class EventParser:
    parser_map = {
        'node': NodeEventParser(),
        'pod': PodEventParser()
    }

    @staticmethod
    def parse(k_object, an_event, cached_state):
        if k_object in EventParser.parser_map:
            object_event_parser = EventParser.parser_map[k_object]
            return object_event_parser.parse(an_event, cached_state)

        raise NotSupportedObjectError(f"object = {k_object}")

