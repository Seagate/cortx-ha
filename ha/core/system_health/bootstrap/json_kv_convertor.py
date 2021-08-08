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

'''Module which provides set of routines to parse the json structured node health
   and helps in storing the data to confstore(KV based) and retrieveing the kv
   based data from confstore which is required to form the HA health event'''

import re

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from ha.core.system_health.system_health_exception import InvalidHealthDataException
from ha.core.system_health.bootstrap.health_event_generator import HealthEventGenerator
from ha.core.system_health.const import NODE_HEALTH_CONF_INDEX, NODE_DATA_KEY, \
     NODE_COMPUTE_DATA_KEY, NODE_STORAGE_DATA_KEY, HA_ALERT_COMPUTE_KEY, \
     HA_ALERT_STORAGE_KEY
from ha.execute import SimpleCommand


class KVGenerator:

    """
    Parse the json file and return KVs for all the matching data values
    required for system health
    """

    def __init__(self):

        self._path = []
        self.compute_resource_list, self.storage_resource_list = [], []
        self.compute_health_list, self.storage_health_list = [], []
        self._execute = SimpleCommand()
        self._health_event = HealthEventGenerator()
        self._conf_index =  self._conf_store = None
        # values that need to be collected
        self._filter_list = ["uid:", "last_updated:", "health.status:"]

        self._uid = self._last_modified = self._status = self._key = None


    # collct kvs and if all 3 values for a component are avilable, generate healthEvent
    def _update_health(self, key: str, val: str) -> None:
        """
           Get the required uid, last_updated abd helath status value.
           Cleans up the key. Ex: node.compute.hw.cpu.health.status will
           be node.compute.hw.cpu. If health status value is appropriate,
           calls the API to create health event with above and additional
           conf index and conf store object parameters
        """
        if re.search(self._filter_list[0].replace(':',''), key):
            self._uid = val
        elif re.search(self._filter_list[1].replace(':',''), key):
            self._last_modified = val
        elif re.search(self._filter_list[2].replace(':',''), key):
            self._status = val
            # cleanup the key
            # Previous key is node.compute....health.status or node.storage....helath.status
            # Remove node. and .health.status and form a new key as compute... or storage...
            self._key = key.replace('node.', '').replace('.health.status','')
            self._health_event.create_health_event(self._key, self._uid, self._last_modified, self._status, self._conf_index, self._conf_store)
            self._uid = self._last_modified = self._status = self._key = None

    def _get_required_compute_kv(self, key=None):
        """
           The node health json structure is:
           {
              node: {
                        compute: []
                    },
                    {
                        storage: []
                    }
           }
           This routine will help to get the all required key values from
           confstore. Prefix: 'node_health' key: node>compute[0]
           uid, last_updated_status and health status will be updated for
           each compute as well as sub component of compute
           Ex: node.compute.hw.cpu.uid CPU-0
        """
        for compute_res in self.compute_resource_list:
            if isinstance(self.compute_health_list[compute_res], dict):
                for comp in self.compute_health_list[compute_res]:
                    new_key = key + f'.{compute_res}.{comp}'
                    self._parse_health_comp_dict(self.compute_health_list[compute_res][comp], new_key)

    def _get_required_storage_kv(self, key: str = None) -> None:
        """
           The node health json structure is:
           {
              node: {
                        compute: []
                    },
                    {
                        storage: []
                    }
           }
           This routine will help to get the all required key values from
           confstore. Prefix: 'node_health' key: node>storage[0]
           uid, last_updated_status and health status will be updated for
           storage as well as each sub component of storage
           Ex: node.storage.fw.logical_volume.last_updated 1626950494
        """
        for storage_res in self.storage_resource_list:
            if isinstance(self.storage_health_list[storage_res], dict):
                for comp in self.storage_health_list[storage_res]:
                    new_key = key + f'.{storage_res}.{comp}'
                    self._parse_health_comp_dict(self.storage_health_list[storage_res][comp], new_key)

    def _parse_health_comp_dict(self, component, key: str) -> None:
        """
           The node health json structure is:
           {
              node: {
                        compute: [
                            "hw": {
                                "cpu": [ {"uid": CPU-0, ...}, {}, ...]
                                }
                            "platform_sensor": {[], [], []}
                        ]
                    },
                    {
                        storage: []
                    }
           }
           This routine further handles the inside hierarchy of compute and storage.
        """
        if isinstance(component, list) and component:
            for res_comp in component:
                if 'uid' in res_comp and 'last_updated' in res_comp:
                    val = res_comp['uid']
                    self._update_health(f'{key}.uid', val)
                    val = res_comp['last_updated']
                    self._update_health(f'{key}.last_updated', val)
                if 'health' in res_comp:
                    new_key = key + '.health.status'
                    val = res_comp['health']['status']
                    self._update_health(new_key, val)
        else:
            if isinstance(component, dict) and component:
                for sub_comp in component:
                    new_key = key + f'.{sub_comp.lower()}'
                    self._parse_health_comp_dict(component[sub_comp], new_key)

    # parse json and generate health events
    def generate_health(self, json_file_nm: str, conf_index, conf_store) -> None:
        """
           Load the json strctured node health data received from Discovery module
           to confstore and then retrives the required data using index and key
        """
        self._conf_index = conf_index
        self._conf_store = conf_store
        node_health_list = []

        try:
            Conf.load(NODE_HEALTH_CONF_INDEX, f'json://{json_file_nm}')
            node_health_list = Conf.get(NODE_HEALTH_CONF_INDEX, NODE_DATA_KEY)
            # Specifically to retrieve upper_level keys such as:
            # node.compute.<'uid', 'last_updated', 'health.status'>
            # node.storage.<'uid', 'last_updated', 'health.status'>
            for node_comp in node_health_list:
                if node_health_list[node_comp]:
                    uid = node_health_list[node_comp][0]['uid']
                    self._update_health(f'node.{node_comp}.uid', uid)
                    last_updated = node_health_list[node_comp][0]['last_updated']
                    self._update_health(f'node.{node_comp}.last_updated', last_updated)
                    health_status = node_health_list[node_comp][0]['health']['status']
                    self._update_health(f'node.{node_comp}.health.status', health_status)

            # Get the node.compute[0] and node.storage[0] data and iterate over it
            self.compute_health_list = Conf.get(NODE_HEALTH_CONF_INDEX, NODE_COMPUTE_DATA_KEY)
            self.storage_health_list = Conf.get(NODE_HEALTH_CONF_INDEX, NODE_STORAGE_DATA_KEY)

            if self.compute_health_list:
                for compute_component in self.compute_health_list:
                    # This will form the compute list as ['hw', 'sw', 'platform_sensor'] etc
                    self.compute_resource_list.append(compute_component)
                if self.compute_resource_list:
                    self._get_required_compute_kv(key=HA_ALERT_COMPUTE_KEY)
            else:
                Log.warn('storage health event is empty')

            if self.storage_health_list:
                for storage_component in self.storage_health_list:
                    # This will form the storage list as ['hw', 'sw', 'platform_sensor'] etc
                    self.storage_resource_list.append(storage_component)
                if self.storage_resource_list:
                    self._get_required_storage_kv(key=HA_ALERT_STORAGE_KEY)
            else:
                Log.warn(f'storage health event is empty')

            Log.info(f"Health updates successful for {json_file_nm}  ")
        except Exception as err:
            Log.error(f"Failed parsing file {json_file_nm}, Exception received {err} ")
            raise InvalidHealthDataException(f"Failed parsing file {json_file_nm}")
