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

from ha import const
from ha.const import _DELIM
from cortx.utils.log import Log
from cortx.utils.conf_store.conf_store import Conf
from ha.core.event_manager.model.action_event import RecoveryActionEvent
from ha.core.system_health.model.health_event import HealthEvent


class FiletrEvent:
    """
    Filter the Alert
    """

    def process_event(self, event: HealthEvent) -> object:
        """
        Get event from HealthEvent class.
        Drop a event if it is not belongs to namspace=cortx & pod name starts with cortx-data
        Args:
            event (Event): Event object.

        Returns:
            object: RecoveryActionEvent.
        """
        event_namespace = event.namespace
        event_pod_name = event.pod_name

        namespace = Conf.get(const.HA_GLOBAL_INDEX, f"K8S:POD{_DELIM}namespace")
        pod_name = Conf.get(const.HA_GLOBAL_INDEX, f"K8S:POD{_DELIM}pods")
        # Create RecoveryActionEvent
        if event_namespace == namespace and event_pod_name.startswith(pod_name):
            recovery_action_event = RecoveryActionEvent(event)
            return recovery_action_event
        else:
            Log.info("Event is dropped as it doesn't meet criteria")
            return None
