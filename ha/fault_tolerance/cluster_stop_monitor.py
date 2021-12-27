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

"""
Handler for handling cluster stop events received from CSM
"""

import json
import ast

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from ha.util.message_bus import MessageBus, CONSUMER_STATUS, MessageBusConsumer

from ha import const
from ha.k8s_setup.const import _DELIM

class ClusterStopMonitor:

    def __init__(self):
        """Init method"""
        self._consumer = self._get_consumer()

    def start(self):
        """
        Start to listen messages.
        """
        self._consumer.start()

    def _get_consumer(self) -> MessageBusConsumer:
        """
           Returns an object of MessageBusConsumer class which will listen on
           cluster_event message type and callback will be executed
        """

        self._consumer_id = Conf.get(const.HA_GLOBAL_INDEX, f'CLUSTER_STOP_MON{_DELIM}consumer_id')
        self._consumer_group = Conf.get(const.HA_GLOBAL_INDEX, f'CLUSTER_STOP_MON{_DELIM}consumer_group')
        self._message_type = Conf.get(const.HA_GLOBAL_INDEX, f'CLUSTER_STOP_MON{_DELIM}message_type')
        return MessageBus.get_consumer(consumer_id=self._consumer_id, \
                                consumer_group=self._consumer_group, \
                                message_type=self._message_type, \
                                callback=self.process_message)

    def process_message(self, message: str):
        """Callback method for MessageConsumer"""
        #Log.debug(f'Received the message from message bus: {message}')
        Log.debug(f'Received the message from message bus: {message}')
        try:
            # parse the message and check if cluster stop received
            msg_decode = message.decode('utf-8')
            msg = json.dumps(ast.literal_eval(msg_decode))
            cluster_alert = json.loads(msg)

            if cluster_alert["start_cluster_shutdown"] == '1':
                # Placeholder function, to be replaced by appropriate function as part of EOS-24900
                self.stop_cluster()
        except Exception as err:
            Log.error(f'Failed to analyze the event: {message} error: {err}')
            return CONSUMER_STATUS.SUCCESS
        return CONSUMER_STATUS.SUCCESS

    def stop_cluster(self):
        """
        Placeholder function
        """
        Log.info('Cluster stop received ')
