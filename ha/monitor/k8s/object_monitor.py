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
from ha.monitor.k8s.const import EventStates, K8SClientConst
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
        self._sigterm_received = False
        self._stop_event_processing = False
        self._producer = self._get_producer()
        Log.info(f"Initialization done for {self._object} monitor")

    def _init_log(self):
        # Initialize logging for the object
        log_file = f"{self._object}_monitor"
        ConfigManager.init(log_file)

    def _get_producer(self):
        message_type = Conf.get(const.HA_GLOBAL_INDEX, f"MONITOR{_DELIM}message_type")
        producer_id = Conf.get(const.HA_GLOBAL_INDEX, f"MONITOR{_DELIM}producer_id")
        MessageBus.init()
        return MessageBus.get_producer(producer_id, message_type)

    def set_sigterm(self, signum, frame):
        """
        Callback function for signal.signal
        through which monitor will be notified for sigterm.
        """
        Log.info(f"Received signal: {signum}")
        Log.debug(f"Received signal: {signum} during execution of frame: {frame}")
        self._sigterm_received = True

    def check_for_signals(self, k8s_watch: watch.Watch):
        """
        Check if any pending signal while watching on kubernetes.watch.stream synchronusly.
        Note: curretnly handling only SIGTERM signal
        but if required we can make use of this function for convey some message/events/signals
        to handle while loopping  over synchronus watch.stream call
        """
        # SIGTERM signal
        if self._sigterm_received:
            Log.info("Handling SIGTERM signal.")
            self.handle_sigterm(k8s_watch)
            # clear the flag once handled
            self._sigterm_received = False

    def handle_sigterm(self, k8s_watch: watch.Watch):
        """
        handling pending sigterm signal which must have came,
        while watching on kubernetes.watch.stream synchronusly.
        """
        # set the stop flag so it will not pick the new events
        k8s_watch.stop()
        # flush out already fetched events and release the connection and other acquired resources
        # timeout_seconds needs to set no wait i.e. 0 as we have called stop only needs to flush stucked events
        kwargs = self._args
        kwargs[K8SClientConst.TIMEOUT_SECONDS] = K8SClientConst.VAL_WATCH_TIMEOUT_NOWAIT
        for an_event in k8s_watch.stream(self._object_function, **kwargs):
            # Debug logging event type and metadata
            Log.debug(f'flushing out the event type: {an_event[K8SEventsConst.TYPE]} \
                metadata: {an_event[K8SEventsConst.RAW_OBJECT][K8SEventsConst.METADATA]}')
        # Setting flag to stop event processing loop
        Log.info(f"Stopped watching for {self._object} events.")
        self._stop_event_processing = True

    def run(self):

        # Initialize log
        self._init_log()
        Log.info(f"{self._object} monitor is started.")

        # Setup Credentials
        config.load_incluster_config()

        # Initialize client
        k8s_client = client.CoreV1Api()

        # Initialize watch
        k8s_watch = watch.Watch()

        # Get method pointer
        self._object_function = getattr(k8s_client, ObjectMap.get_subscriber_func(self._object))
        Log.info(f'Starting watch on {self._object} events: {self._object_function}')

        # While True loop restrt the watch.Watch.stream() after specified timeout
        # Note: if we don't specify timeout no need to restart the loop it will happen internally
        while self.TIMEOUT_SECONDS in self._args:
            # Start watching events corresponding to self._object
            for an_event in k8s_watch.stream(self._object_function, **self._args):

                # Check for the signals (SIGTERM signal)
                self.check_for_signals(k8s_watch)

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
                Log.info(f"Sending alert on message bus {alert.to_dict()}")
                self._producer.publish(str(alert.to_dict()))
            # If stop processing events is set then no need to retry just break the loop
            if self._stop_event_processing:
                break
        Log.info(f'{self.name} stopped.')
