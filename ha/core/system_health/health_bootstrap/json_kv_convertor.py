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
from ha.core.system_health.health_bootstrap.health_event_generator import HealthEventGenerator
from ha.execute import SimpleCommand
from ha.core.system_health.const import NODE_HEALTH_KV_FILE

class KVGenerator:

    """
    Parse the json file and return KVs for all the matching data values
    required for system health
    """

    def __init__(self):

        self._path = []
        self._execute = SimpleCommand()
        self._kvfile = NODE_HEALTH_KV_FILE

        # values that need to be collected
        self._filter_list = ["uid:", "last_updated:", "health.status:"]


    def _update_kv(self, file_nm, k , v):

        kv = f"{k}:{v}\n"

        for pattern in self._filter_list:
            if re.search(pattern, kv):
                if pattern == "uid:":
                    if re.search("health.specifics", kv) or re.search("sites.uid:", kv) or re.search("sites.racks.uid", kv) or  re.search("sites.racks.cortx_nodes.uid", kv) :
                        break
                elif  re.search("sites.racks.cortx_nodes.last_updated:", kv):
                    break

                f = open(file_nm, "a")
                f.write(kv)
                f.close()

    def _remove_kvfile(self):
        command = f"rm -f {self._kvfile}"
        self._execute.run_cmd(command)

    def _get_line_params(self, fp):
        line = fp.readline()
        kv = line.split(":")
        key = kv[0]
        val = kv[1].strip('\n')
        return key, val

    # Call HealthEvent for each of the status values in kv file
    def generate_health_event(self, file_nm, conf_index, conf_store):
        fp = open(file_nm, 'r')

        lines = fp.readlines()
        count = len(lines)
        fp.close()
        fp = open(file_nm, 'r')

        for _ in range(0, int(count/3)):

            key, uid = self._get_line_params(fp)
            key, last_modified = self._get_line_params(fp)
            key, status = self._get_line_params(fp)

            # cleanup the key
            key = key.replace('sites.racks.cortx_nodes.','').replace('.health.status','')

            # create health event
            healthEvent = HealthEventGenerator()
            healthEvent.create_health_event(key, uid, last_modified, status, conf_index, conf_store)

        # remove the kv file
        self._remove_kvfile()


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
                    self._update_kv(self._kvfile, key, val)
                    self._path.pop()

                else:
                    if isinstance(v[0], dict):
                        for v_int in v:
                            self._walk(v_int)
                    # End value in the KV  is a list
                    else:
                        key = (".".join(self._path))
                        val = v
                        self._update_kv(self._kvfile, key, val)
                    self._path.pop()

            else:
                # conditions handled isinstance(v, str) or isinstance(v, int) etc
                self._path.append(k)
                key = (".".join(self._path))
                val = v
                self._update_kv(self._kvfile, key, val)
                self._path.pop()


    def parse_json(self, json_file_nm):
        try:
            with open(json_file_nm, "r") as fi:
                schema = json.load(fi)

            self._walk(schema)
            Log.info(f"Parsing successful for {json_file_nm}  ")
            return self._kvfile

        except Exception as e:
            Log.error(f"Failed parsing file {json_file_nm}, Exception received {e} ")
            raise InvalidHealthDataException(f"Failed parsing file {json_file_nm}")
