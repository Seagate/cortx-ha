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

import json
from cortx.utils.log import Log
from ha.core.health_monitor.const import HEALTH_MON_ACTIONS
from ha.core.health_monitor.const import HEALTH_MON_KEYS
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.config.config_manager import ConfigManager
from ha.core.system_health.const import HEALTH_STATUSES

class MonitorRulesManager:

    def __init__(self):

        self._confstore = ConfigManager.get_confstore()

    def evaluate(self, event: HealthEvent):

        val = []
        key = f"{HEALTH_MON_KEYS.ACT_RULE.value}/{event.resource_type}/{event.event_type}"

        Log.debug(f"Evaluating rule for {key}")
        if self._confstore.key_exists(key):
            kv  = self._confstore.get(key)
            _, val = kv.popitem()
            val = json.loads(val)
        return val

    def add_rule(self, resource: str, event: HEALTH_STATUSES , action: HEALTH_MON_ACTIONS):

        key = f"{HEALTH_MON_KEYS.ACT_RULE.value}/{resource}/{event}"
        val = []

        Log.info(f"Adding rule for key: {key} ,value: {action}")

        if self._confstore.key_exists(key):
            kv = self._confstore.get(key)
            k, val = kv.popitem()
            val = json.loads(val)
            if action not in val:
                val.append(action)
                val = json.dumps(val)
                self._confstore.update(key, val)
            else:
                Log.warn(f"key value already exists for {k} , {action}")
                return

        else:
            val.append(action)
            val = json.dumps(val)
            self._confstore.set(key, val)


    def remove_rule(self, resource: str, event: HEALTH_STATUSES , action: HEALTH_MON_ACTIONS):

        key = f"{HEALTH_MON_KEYS.ACT_RULE.value}/{resource}/{event}"
        val = []
        Log.info(f"Removing rule for key: {key} ,value: {action}")

        if self._confstore.key_exists(key):
            kv = self._confstore.get(key)
            _, val = kv.popitem()
            val = json.loads(val)
            if action not in val:
                Log.warn(f"KV not found for key: {key}, value: {action}")
            else:
                val.remove(action)
                if len(val) == 0:
                    self._confstore.delete(key)
                    Log.debug(f"key value removed for {key} , {action}. value list empty; deleting key {key}")
                else:
                    val = json.dumps(val)
                    self._confstore.update(key, val)
                    Log.debug(f"KV removed for {key} , {action}")
        else:
            Log.warn(f"key {key} not found")

