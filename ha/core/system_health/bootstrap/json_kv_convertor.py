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
            # cleanup the key
            self._key = key.replace('sites.racks.cortx_nodes.','').replace('.health.status','')

            # create health event
            self._healthEvent.create_health_event(self._key, self._uid, self._last_modified, self._status, self._conf_index, self._conf_store)
            self._uid = self._last_modified = self._status = self._key = None


    def _update_kv(self, k , v):

        kv = f"{k}:{v}\n"

        for pattern in self._filter_list:
            if re.search(pattern, kv):
                if pattern == "uid:":
                    if re.search("health.specifics", kv) or re.search("sites.uid:", kv) or re.search("sites.racks.uid:", kv) or  re.search("sites.racks.cortx_nodes.uid:", kv) :
                        break
                elif  re.search("sites.racks.cortx_nodes.last_updated:", kv):
                    break

                self._update_health(k,v)


    def _walk(self, d):

        for k,v in d.items():
            if isinstance(v, dict):
                self._path.append(k)
                self._walk(v)
                self._path.pop()

            elif isinstance(v, list):
                self._path.append(k)
                if not v:
                    key = (".".join(self._path))
                    val = v
                    self._update_kv(key, val)
                    self._path.pop()

                else:
                    if isinstance(v[0], dict):
                        for v_int in v:
                            self._walk(v_int)
                    # End value in the KV  is a list
                    else:
                        key = (".".join(self._path))
                        val = v
                        self._update_kv(key, val)
                    self._path.pop()

            else:
                # conditions handled isinstance(v, str) or isinstance(v, int) etc
                self._path.append(k)
                key = (".".join(self._path))
                val = v
                self._update_kv(key, val)
                self._path.pop()

    # parse json and generate health events
    def generate_health(self, json_file_nm, conf_index, conf_store):

        self._conf_index = conf_index
        self._conf_store = conf_store

        try:
            with open(json_file_nm, "r") as fi:
                schema = json.load(fi)

            self._walk(schema)
            Log.info(f"Health updates successful for {json_file_nm}  ")

        except Exception as e:
            Log.error(f"Failed parsing file {json_file_nm}, Exception received {e} ")
            raise InvalidHealthDataException(f"Failed parsing file {json_file_nm}")
