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
from ha.const import HA_DELIM
from ha.core.health_monitor.const import HEALTH_MON_ACTIONS
from ha.core.health_monitor.const import HEALTH_MON_KEYS
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.config.config_manager import ConfigManager
from ha.core.system_health.const import HEALTH_STATUSES
from ha.core.health_monitor.error import InvalidAction

class MonitorRulesManager:

    def __init__(self):

        self._confstore = ConfigManager.get_confstore()

    def _prepare_key(self, resource_type: str, event_type: str, functional_type: str) -> str:
        """
        Prepare a key for the health monitor rules lookup, using HEALTH_MON_KEYS

        Args:
            resource_type(str)
            event_type(str)

        Returns:
            str: key string
        """
        if functional_type:
            resource_type = f"{resource_type}{HA_DELIM}{functional_type}"
        return f"{HEALTH_MON_KEYS.ACT_RULE.value}{HA_DELIM}{resource_type}{HA_DELIM}{event_type}"

    def _get_val(self, key: str) -> str:
        """
        Check if the key exists. Return KV if yes else return None

        Args
            key(str)

        Returns:
            val(str): Returns KV
        """
        val = None
        if self._confstore.key_exists(key):
            val = self._confstore.get(key)
        return val

    def _get_k_v(self, kv: dict):
        """
        Extract key, value from the KV
        Convert value from string to list

        Args:
            kv : KV returned from confstore

        Returns:
            key
            value
        """
        key, val = kv.popitem()
        val = json.loads(val)
        return key, val

    def _validate_action(self, action: str):
        """
        Check action.

        Args:
            action (str): Action
        """
        if action not in HEALTH_MON_ACTIONS:
            raise InvalidAction(f"Action for MonitorRule: {action} is not valid.")

    def evaluate(self, event: HealthEvent) -> list:
        """
        Check if rule exists for received HealthEvent
        If yes, return the actions for that rule

        Args:
            HealthEvent

        Returns:
            list: actions configured for the rule
        """
        val = []
        functional_type = event.specific_info.get("type")
        key = self._prepare_key(event.resource_type, event.event_type, functional_type)
        Log.debug(f"Evaluating rule for {key}")
        kv = self._get_val(key)
        if kv:
            _, val = self._get_k_v(kv)
        Log.info(f"Evaluated action {val} for key {key}")
        return val

    def add_rule(self, resource: str, event: HEALTH_STATUSES , action: HEALTH_MON_ACTIONS):
        """
        Add rule to confstore for resource/event.
        If rule exists, append the "action" to same rule

        Args:
            resource(str): resource name
            event(str): event type
            action(str): action to be added
        """
        self._validate_action(action)
        key = self._prepare_key(resource, event)
        val = []
        Log.info(f"Adding rule for key: {key} ,value: {action}")
        kv = self._get_val(key)
        if kv:
            _, val = self._get_k_v(kv)
            if action not in val:
                val.append(action)
                val = json.dumps(val)
                self._confstore.update(key, val)
            else:
                Log.warn(f"key value already exists for {key} , {action}")
                return
        else:
            val.append(action)
            val = json.dumps(val)
            self._confstore.set(key, val)

    def remove_rule(self, resource: str, event: HEALTH_STATUSES , action: HEALTH_MON_ACTIONS):
        """
        For the rule resource/event  remove "action" from confstore.
        If actions list becomes empty, delete the rule

        Args:
            resource(str): resource name
            event(str): event type
            action(str): action to be removed
        """
        self._validate_action(action)
        key = self._prepare_key(resource, event)
        val = []
        Log.info(f"Removing rule for key: {key} ,value: {action}")
        kv = self._get_val(key)
        if kv:
            _, val = self._get_k_v(kv)
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
