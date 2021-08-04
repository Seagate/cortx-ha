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


import json
import re

from cortx.utils.log import Log
from ha.core.system_health.system_health_exception import InvalidHealthDataException
from ha.core.system_health.bootstrap.health_event_generator import HealthEventGenerator
from ha.execute import SimpleCommand
from cortx.utils.conf_store import Conf


class KVGenerator:

    """
    Parse the json file and return KVs for all the matching data values
    required for system health
    """

    def __init__(self):

        self._path = []
        self._execute = SimpleCommand()
        self._healthEvent = HealthEventGenerator()
        self._conf_index =  self._conf_store = None
        # values that need to be collected
        self._filter_list = ["uid:", "last_updated:", "health.status:"]

        self._uid = self._last_modified = self._status = self._key = None


    # collct kvs and if all 3 values for a component are avilable, generate healthEvent
    def _update_health(self, key, val):

        if re.search(self._filter_list[0].replace(':',''), key):
            self._uid = val
        elif re.search(self._filter_list[1].replace(':',''), key):
            self._last_modified = val
        elif re.search(self._filter_list[2].replace(':',''), key):
            self._status = val
            if self._status.upper() in ["NA", "UNKNOWN", "N/A"]:
                return
            # cleanup the key
            self._key = key.replace('.health.status','')
            self._healthEvent.create_health_event(self._key, self._uid, self._last_modified, self._status, self._conf_index, self._conf_store)
            self._uid = self._last_modified = self._status = self._key = None

    def _get_required_compute_kv(self, compute_resource_list, key=None):
        """Get the required key values from Confstore"""
        for compute_res in compute_resource_list:
            if isinstance(self.compute_health_list[compute_res], dict):
                if compute_res == 'health':
                    new_key = key + f'.{compute_res}.status'
                    val = self.compute_health_list[compute_res]['status']
                    self._update_health(new_key, val)
                else:
                    for comp in self.compute_health_list[compute_res]:
                        new_key = key + f'.{compute_res}.{comp}'
                        self._parse_health_comp_dict(self.compute_health_list[compute_res][comp], new_key)
            elif compute_res == 'uid' or compute_res == 'last_updated':
                new_key = key + f'.{compute_res}'
                val = self.compute_health_list[compute_res]
                self._update_health(new_key, val)

    def _get_required_storage_kv(self, storage_resource_list, key=None):
        """Get the required key values from Confstore"""
        for storage_res in storage_resource_list:
            if isinstance(self.storage_health_list[storage_res], dict):
                if storage_res == 'health':
                    new_key = key + f'.{storage_res}.status'
                    val = self.storage_health_list[storage_res]['status']
                    self._update_health(new_key, val)
                else:
                    for comp in self.storage_health_list[storage_res]:
                        new_key = key + f'.{storage_res}.{comp}'
                        self._parse_health_comp_dict(self.storage_health_list[storage_res][comp], new_key)
            elif storage_res == 'uid' or storage_res == 'last_updated':
                new_key = key + f'.{storage_res}'
                val = self.storage_health_list[storage_res]
                self._update_health(new_key, val)

    def _parse_health_comp_dict(self, component, key):
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
    def generate_health(self, json_file_nm, conf_index, conf_store):

        self._conf_index = conf_index
        self._conf_store = conf_store

        try:
            Conf.load('node_health', f'json://{json_file_nm}')
            self.compute_health_list = Conf.get('node_health', f'node>compute[0]')
            self.storage_health_list = Conf.get('node_health', f'node>storage[0]')
            compute_resource_list = []
            storage_resource_list = []
            for compute_component in self.compute_health_list:
                compute_resource_list.append(compute_component)
            for storage_component in self.storage_health_list:
                storage_resource_list.append(storage_component)
            self._get_required_compute_kv(compute_resource_list, key='node.compute')
            self._get_required_storage_kv(storage_resource_list, key='node.storage')
            Log.info(f"Health updates successful for {json_file_nm}  ")
        except Exception as e:
            Log.error(f"Failed parsing file {json_file_nm}, Exception received {e} ")
            raise InvalidHealthDataException(f"Failed parsing file {json_file_nm}")
