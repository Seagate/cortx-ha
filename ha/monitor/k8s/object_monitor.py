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

import threading
from kubernetes import config, client, watch

from ha.core.config.config_manager import ConfigManager
from ha.monitor.k8s.objects import ObjectMap
from ha.monitor.k8s.parser import EventParser
from ha.monitor.k8s.const import EventStates, K8SClientConst
from ha.monitor.k8s.const import K8SEventsConst
from cortx.utils.log import Log
from ha import const

class ObjectMonitor(threading.Thread):
    def __init__(self, producer, k_object, **kwargs):
        """
        Init method
        Initialization of member objects, and Thread super calss
        """
        super().__init__()
        self._publish_alert = True
        self._object = k_object
        self.name = f"Monitor-{k_object}-Thread"
        self._args = kwargs
        self._starting_up = True
        self._object_state = {}
        self._sigterm_received = threading.Event()
        self._stop_event_processing = False
        self._producer = producer
        self._confstore = ConfigManager.get_confstore()
        Log.info(f"Initialization done for {self._object} monitor")

    def set_sigterm(self, signum, frame):
        """
        Callback function for signal.signal
        through which monitor will be notified for sigterm.
        """
        Log.info(f"{self.name} Received signal: {signum}")
        Log.debug(f"{self.name} Received signal: {signum} during execution of frame: {frame}")
        if self._confstore.key_exists(const.CLUSTER_STOP_KEY):
            Log.debug(f"Deleting the key ({const.CLUSTER_STOP_KEY}) from confstore so next time we will not go in cluster stop mode.")
            self._confstore.delete(key=const.CLUSTER_STOP_KEY, recurse=True)
        self._sigterm_received.set()

    def check_for_signals(self, k8s_watch: watch.Watch, k8s_watch_stream):
        """
        Check if any pending signal while watching on kubernetes.watch.stream synchronusly.
        Note: curretnly handling only SIGTERM signal
        but if required we can make use of this function for convey some message/events/signals
        to handle while loopping  over synchronus watch.stream call
        """
        # SIGTERM signal
        if self._sigterm_received.is_set():
            Log.info(f"{self.name} Handling SIGTERM signal.")
            self.handle_sigterm(k8s_watch, k8s_watch_stream)
            # clear the flag once handled
            self._sigterm_received.clear()

    def handle_sigterm(self, k8s_watch: watch.Watch, k8s_watch_stream):
        """
        handling pending sigterm signal which must have came,
        while watching on kubernetes.watch.stream synchronusly.
        """
        # set the stop flag so it will not pick the new events
        k8s_watch.stop()
        # flush out already fetched events and release the connection and other acquired resources
        Log.info(f"Flusing remaining Kubernetes {self._object} events.")
        for an_event in k8s_watch_stream:
            # Debug logging event type and metadata
            Log.debug(f'{self.name} flushing out the event type: {an_event[K8SEventsConst.TYPE]} \
                metadata: {an_event[K8SEventsConst.RAW_OBJECT][K8SEventsConst.METADATA]}')
        # Setting flag to stop event processing loop
        Log.info(f"Stopped watching for {self._object} events.")
        self._stop_event_processing = True

    def is_publish_enable(self) -> bool:
        """
        Check if cluster_stop key is exist and if exist check if it is enable
        if enable then publish event should be stopped
        """
        if self._publish_alert:
            if self._confstore.key_exists(const.CLUSTER_STOP_KEY):
                _, cluster_stop = (self._confstore.get(const.CLUSTER_STOP_KEY)).popitem()
                if cluster_stop == const.CLUSTER_STOP_VAL_ENABLE:
                    Log.info(f"{self._object}_monitor stopping publish alert as cluster stop message is received.")
                    self._publish_alert = False
        return self._publish_alert

    def publish_alert(self, alert):
        """
        If publish is enabled, i.e. Yet the cluster stop message has not been received.
        then publish the alert for Fault Tolerance Monitor
        """
        if self.is_publish_enable():
            # Write to message bus
            Log.info(f"{self._object}_monitor sending alert on message bus {alert.to_dict()}")
            self._producer.publish(str(alert.to_dict()))
        else:
            Log.info(f"{self._object}_monitor received cluster stop message so skipping publish alert: {str(alert.to_dict())}.")

    def run(self):
        """
        Thread target method which loops on Kubernetes Watch.stream() to get pod or node events
        """
        Log.info(f"Starting the {self.name}...")

        # Setup Credentials
        config.load_incluster_config()

        # Initialize client
        k8s_client = client.CoreV1Api()

        # Initialize watch
        k8s_watch = watch.Watch()

        # Get method pointer
        self._object_function = getattr(k8s_client, ObjectMap.get_subscriber_func(self._object))
        Log.info(f'Starting watch on {self._object} events: {self._object_function.__name__}')

        # While True loop to restart the watch.Watch.stream() after specified timeout
        while True:
            # create a object of Watch.stream generator loop on it.
            k8s_watch_stream =  k8s_watch.stream(self._object_function, **self._args)
            # Start watching events corresponding to self._object
            for an_event in k8s_watch_stream:

                # Check for the signals (SIGTERM signal)
                self.check_for_signals(k8s_watch, k8s_watch_stream)

                # Due to SIGTERM signal stopping further event processing
                if self._stop_event_processing:
                    Log.info(f"Stopped processing {self._object} events.")
                    break

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
                self.publish_alert(alert)

            # If stop processing events is set then no need to retry just break the loop
            # If we don't specify timeout no need to restart the loop it will happen internally
            # as Watch.stream will be blocking call which has while True loop so no need a loop for it.
            if self._stop_event_processing or K8SClientConst.TIMEOUT_SECONDS not in self._args:
                break
        Log.info(f"Stopping the {self.name}...")

