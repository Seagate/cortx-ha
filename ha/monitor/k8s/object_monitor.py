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


class ObjectMonitor(Thread):
    def __init__(self, k_object, **kwargs):
        super().__init__()
        self._object = k_object
        self.name = f"Monitor-{k_object}-Thread"
        self._args = kwargs
        self._starting_up = True
        self._object_state = {}

    def run(self):
        # Setup Credentials
        config.load_kube_config()

        # Initialize client
        k8s_client = client.CoreV1Api()

        # Initialize watch
        k8s_watch = watch.Watch()

        # Get method pointer
        object_function = getattr(k8s_client, ObjectMap.get_subscriber_func(self._object))

        # Start watching events corresponding to self._object
        for an_event in k8s_watch.stream(object_function, **self._args):
            alert = EventParser.parse(self._object, an_event, self._object_state)
            if alert is None:
                continue
            if self._starting_up:
                if an_event[K8SEventsConst.TYPE] == EventStates.ADDED:
                    alert.is_status = True
                else:
                    self._starting_up = False

            # Write to message bus
            print(f"Thread = {self.name} Alert = {alert.to_dict()}")
