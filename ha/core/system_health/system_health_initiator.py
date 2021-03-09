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

from cortx.utils.log import Log
from cortx.utils.kv_store.kv_payload import KvPayload
from ha import const
from ha.core.system_health.health_event import HealthEvent
from ha.core.system_health.system_health import SystemHealth

class SystemHealthInitiator:
    """
    System Health Initiator. This class provides an initiator for system health
    which could be called for initiating a system health for a node.
    """

    def __init__(self):
        """
        Init method.
        """
        self.cluster_id =  # TODO: Read from store
        self.system_health = SystemHealth()

    def process_schema(self, filename: str):
        # TODO: Read the health view schema file. Convert the same into the KvPayLoad.
        # Create HealthEvent object and call process_event for every entity within the health view schema file.
        # self.system_health.process_event(healthevent)