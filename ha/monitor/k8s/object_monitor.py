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


from threading import Thread

from kubernetes import config, client, watch

from ha.monitor.k8s.objects import ObjectMap
from ha.monitor.k8s.parser import EventParser
from ha.monitor.k8s.const import EventStates
from ha.monitor.k8s.const import K8SEventsConst

from cortx.utils.log import Log
from ha.core.config.config_manager import ConfigManager
from ha.util.message_bus import MessageBus
from cortx.utils.conf_store import Conf
from ha import const
from ha.const import _DELIM

class ObjectMonitor(Thread):
    def __init__(self, k_object, **kwargs):
        super().__init__()
        self._object = k_object
        self.name = f"Monitor-{k_object}-Thread"
        self._args = kwargs
        self._starting_up = True
        self._object_state = {}
        # Initialize logging for the object
        log_file = f"{k_object}_monitor"
        ConfigManager.init(log_file)
        Log.info(f"Init done for {k_object} monitor")
        self._producer = self._get_producer()

    def _get_producer(self):
        message_type = Conf.get(const.HA_GLOBAL_INDEX, f"MONITOR{_DELIM}message_type")
        producer_id = Conf.get(const.HA_GLOBAL_INDEX, f"MONITOR{_DELIM}producer_id")
        MessageBus.init()
        return MessageBus.get_producer(producer_id, message_type)

    def run(self):

        # Setup Credentials
        config.load_incluster_config()

        # Initialize client
        k8s_client = client.CoreV1Api()

        # Initialize watch
        k8s_watch = watch.Watch()

        # Get method pointer
        object_function = getattr(k8s_client, ObjectMap.get_subscriber_func(self._object))

        # Start watching events corresponding to self._object
        for an_event in k8s_watch.stream(object_function, **self._args):
            Log.debug(f"Received event {an_event}")
            alert = EventParser.parse(self._object, an_event, self._object_state)
            if alert is None:
                continue
            if self._starting_up:
                if an_event[K8SEventsConst.TYPE] == EventStates.ADDED:
                    alert.is_status = True
                else:
                    self._starting_up = False

            # Write to message bus
            Log.info(f"Sending alert on message bus {alert.to_dict()}")
            self._producer.publish(str(alert.to_dict()))
