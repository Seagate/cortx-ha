#!/usr/bin/env python3

# CORTX-Py-Utils: CORTX Python common library.
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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

from cortx.utils.conf_store import Conf
from ha.util.msg_bus.tcp.kafka import const
from ha.util.msg_bus.error import InvalidConfigError, ConnectionEstError
from ha.util.msg_bus.tcp.kafka.kafka import KafkaProducerComm, KafkaConsumerComm
from cortx.utils.log import Log

_DELIM = ">"

class ConfInit:
    __instance = None

    def __init__(self):
        if ConfInit.__instance == None:
            ConfInit.__instance = self
            Conf.init()
            try:
                Conf.load(const.CONFIG_INDEX, (const.MESSAGE_BUS_CONF), skip_reload=True)
            except Exception as e:
                Log.warn(e)

class MessageBusComm:
    def __init__(self, **kwargs):

        """
        Parameters required for initialization -
        1. comm_type: Type of communication (PRODUCER or CONSUMER)
        2. client_id: Unique string identifying a PRODUCER. For comm_type as
           PRODUCER this field is required.
        3. group_id: This field signifies the consumer group.For comm_type as
           CONSUMER this field is required.
        4. consumer_name: This field signifies the name of the consumer inside
           a consumer group. For comm_type as CONSUMER this field is required.
        """

        self._comm_obj = None
        self._message_bus_type = 'kafka'
        self._comm_type = kwargs.get(const.COMM_TYPE, None)
        self._init_config(**kwargs)

    def _init_config(self, **kwargs):
        try:
            ConfInit()
            if self._message_bus_type == const.KAFKA:
                self._init_kafka_conf(**kwargs)
            else:
                raise InvalidConfigError("Invalid config")
        except Exception as ex:
            Log.error(f"Invalid config error. {ex}")
            raise InvalidConfigError(f"Invalid config. {ex}")

    def _init_kafka_conf(self, **kwargs):
        """
        Get the kafka (server) endpoints & assign to _hosts in the form of :
        {'server': kafka.default.svc.cluster.local, 'port': '9092'}
        """
        bootstrap_servers = ""
        count = 1
        message_server_endpoints = Conf.get(const.CONFIG_INDEX, f'cortx{_DELIM}external{_DELIM}kafka{_DELIM}endpoints')
        kafka_cluster = MessageBusComm.get_server_list(message_server_endpoints)
        for values in kafka_cluster:
            if len(kafka_cluster) <= count:
                bootstrap_servers = bootstrap_servers + f"{values[const.SERVER]}:{values[const.PORT]}"
            else:
                bootstrap_servers = bootstrap_servers + f"{values[const.SERVER]}:{values[const.PORT]}, "
            count = count +1
        self._hosts = bootstrap_servers
        self._client_id = kwargs.get(const.CLIENT_ID)
        self._group_id = kwargs.get(const.GROUP_ID)
        self._consumer_name = kwargs.get(const.CONSUMER_NAME)
        self._retry_counter = const.RETRY_COUNTER
        Log.debug(f"Message bus config initialized. Hosts: {self._hosts}, "\
            f"Client ID: {self._client_id}, Group ID: {self._group_id}")
        self.init()

    def init(self):
        """
        Initialise communication channel on the basis of comm_type( PRODUCER or CONSUMER )
        """
        try:
            if self._message_bus_type == const.KAFKA:
                self._comm_obj = self._init_kafka_comm()
            self._comm_obj.init()
            Log.debug(f"Initialized the communication channel for {self._comm_type}")
        except Exception as ex:
            Log.error(f"Unable to connect to message bus. {ex}")
            raise ConnectionEstError(f"Unable to connect to message bus. {ex}")

    def _init_kafka_comm(self):
        obj = None
        try:
            if self._comm_type == const.PRODUCER:
                obj = KafkaProducerComm(hosts = self._hosts, client_id = self._client_id, \
                    retry_counter = self._retry_counter)
            elif self._comm_type == const.CONSUMER:
                obj = KafkaConsumerComm(hosts = self._hosts, group_id = self._group_id, \
                    retry_counter = self._retry_counter, consumer_name = self._consumer_name)
            return obj
        except Exception as ex:
            Log.error(f"Unable to initialize message bus. {ex}")
            raise ex

    @staticmethod
    def get_server_list(message_server_endpoints: list) -> tuple:
        """
        Args:
            message_server_endpoints: list of endpoints
        Returns:
            list: ([message_server_list])
        """
        message_server_list = []
        server_info = {}

        for server in message_server_endpoints:
            # Endpoint : tcp://kafka.default.svc.cluster.local:9092
            # Value of server can be <server_fqdn:port> or <server_fqdn>
            if ':' in server:
                endpoints = server.split('//')[1]
                server_fqdn, port = endpoints.split(':')
                server_info['server'] = server_fqdn
                server_info['port'] = port
            else:
                server_info['server'] = server
                server_info['port'] = '9092'  # 9092 is default kafka server port

            message_server_list.append(server_info)
        return message_server_list

    def send(self, message: list, **kwargs):
        """
        Send message list to message bus.
        Args:
            **kwargs: Variable number of arguments, e.g. TOPIC to register message type.
        """
        try:
            ret = self._comm_obj.send_message_list(message, **kwargs)
            Log.debug("Sent messages to message bus")
            return ret.msg()
        except Exception as ex:
            Log.error(f"Unable to send messages to message bus. {ex}")
            raise ex

    def recv(self, **kwargs):
        """
        Recieve message from message bus.
        Args:
            **kwargs: Variable number of arguments, e.g. TOPIC to register message type.
        Returns:
            str: Message.
        """
        try:
            msg = self._comm_obj.recv(**kwargs)
            Log.debug(f"Received message from message bus - {msg}")
            return msg
        except Exception as ex:
            Log.error(f"Unable to receive message from message bus. {ex}")
            raise ex

    def commit(self):
        """
        Consumer will receive the message and process it. Once the messages are processed,
        consumer will send an acknowledgement to the Kafka broker.
        """
        try:
            ret = self._comm_obj.acknowledge()
            Log.debug("Commited to message bus")
            return ret.msg()
        except Exception as ex:
            Log.error(f"Unable to commit to message bus. {ex}")
            raise ex

    def close(self):
        """
        Close the consumer channel.
        """
        try:
            ret = self._comm_obj.disconnect()
            Log.debug("Closing the consumer channel")
            return ret.msg()
        except Exception as ex:
            Log.error(f"Unable to close the consumer channel. {ex}")
            raise ex
