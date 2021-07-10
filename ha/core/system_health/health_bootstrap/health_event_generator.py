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

import uuid
from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from ha.execute import SimpleCommand

from ha.core.system_health.const import NODE_MAP_ATTRIBUTES
from ha.core.system_health.const import RESOURCE_TYPE_MAPPING
from ha.core.system_health.const import CONFSTORE_KEY_ATTRIBUTES
from ha.const import _DELIM
from ha.const import EVENT_ATTRIBUTES
from ha.core.system_health.const import RESOURCE_TO_HEALTH_STATUS_MAPPING
from ha.core.system_health.const import HEALTH_STATUS_TO_EVENT_SEVERITY_MAPPING
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.system_health import SystemHealth
from ha.core.error import HaConfigException

class HealthEventGenerator:

    def __init__(self):
        """
        Init method.
        """
        self._execute = SimpleCommand()

    def _get_machine_id(self):
        command = "cat /etc/machine-id"
        machine_id, err, rc = self._execute.run_cmd(command, check_error=True)
        Log.info(f"Read machine-id. Output: {machine_id}, Err: {err}, RC: {rc}")
        return machine_id.strip()

    def create_health_event(self, key, uid, last_modified, status, conf_index, conf_store) -> None:

        try:
            machine_id = self._get_machine_id()
            node_id = Conf.get(conf_index, f"server_node{_DELIM}{machine_id}{_DELIM}node_id")
            cluster_id = Conf.get(conf_index, f"server_node{_DELIM}{machine_id}{_DELIM}{NODE_MAP_ATTRIBUTES.CLUSTER_ID.value}")
            site_id = Conf.get(conf_index, f"server_node{_DELIM}{machine_id}{_DELIM}{NODE_MAP_ATTRIBUTES.SITE_ID.value}")
            rack_id = Conf.get(conf_index, f"server_node{_DELIM}{machine_id}{_DELIM}{NODE_MAP_ATTRIBUTES.RACK_ID.value}")
            storageset_id = Conf.get(conf_index, f"server_node{_DELIM}{machine_id}{_DELIM}{CONFSTORE_KEY_ATTRIBUTES.STORAGE_SET_ID.value}")
            host_id = Conf.get(conf_index, f"server_node{_DELIM}{machine_id}{_DELIM}network{_DELIM}management{_DELIM}public_fqdn")

            timestamp = last_modified
            event_id = timestamp + str(uuid.uuid4().hex)
            initial_event = {
                EVENT_ATTRIBUTES.EVENT_ID : event_id,
                EVENT_ATTRIBUTES.EVENT_TYPE : RESOURCE_TO_HEALTH_STATUS_MAPPING[status.upper()],
                EVENT_ATTRIBUTES.SEVERITY : HEALTH_STATUS_TO_EVENT_SEVERITY_MAPPING[status.upper()],
                EVENT_ATTRIBUTES.SITE_ID : site_id,
                EVENT_ATTRIBUTES.RACK_ID : rack_id,
                EVENT_ATTRIBUTES.CLUSTER_ID : cluster_id,
                EVENT_ATTRIBUTES.STORAGESET_ID : storageset_id,
                EVENT_ATTRIBUTES.NODE_ID : node_id,
                EVENT_ATTRIBUTES.HOST_ID : host_id,
                EVENT_ATTRIBUTES.RESOURCE_TYPE : RESOURCE_TYPE_MAPPING[key],
                EVENT_ATTRIBUTES.TIMESTAMP : timestamp,
                EVENT_ATTRIBUTES.RESOURCE_ID : uid,
                EVENT_ATTRIBUTES.SPECIFIC_INFO : None
            }

            Log.debug(f"Adding health {initial_event} for node {node_id}")
            health_event = HealthEvent.dict_to_object(initial_event)

            system_health = SystemHealth(conf_store)
            system_health.process_event(health_event)
        except Exception as e:
            Log.error(f"Failed adding node health for {node_id} . Error: {e}")
            raise HaConfigException(f"Failed adding node health for {node_id}")