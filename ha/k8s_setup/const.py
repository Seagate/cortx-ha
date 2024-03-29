# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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

import enum

HA_LOG_LEVEL="INFO"
CONFIG_DIR="/etc/cortx/ha"
HA_CONFIG_FILE="{}/ha.conf".format(CONFIG_DIR)
SOURCE_PATH="/opt/seagate/cortx/ha"
SOURCE_CONFIG_PATH="{}/conf/etc".format(SOURCE_PATH)
SOURCE_HEALTH_HIERARCHY_FILE = "{}/system_health_hierarchy.json".format(SOURCE_CONFIG_PATH)
HEALTH_HIERARCHY_FILE = "{}/system_health_hierarchy.json".format(CONFIG_DIR)

# Set retry count and sleep time for connecting to message bus
# From message bus side, we have 60s timeout.
# So, 62s(60s + 2s sleep)*5=310 ~ 300s for HA POD to be up and running
MESSAGE_BUS_RETRY_COUNT = 5
MESSAGE_BUS_SLEEP_TIME = 2

#Confstore delimiter
_DELIM=">"

# consul endpoint scheme: http
consul_scheme = 'http'
# kafka endpoint scheme: tcp
kafka_scheme = 'tcp'

# Event_manager keys
POD_EVENT="node"
DISK_EVENT="disk"
EVENT_COMPONENT="hare"

# Cluster Cardinality Keys
CLUSTER_CARDINALITY_KEY = "cluster_cardinality"
CLUSTER_CARDINALITY_NUM_NODES = "num_nodes"
CLUSTER_CARDINALITY_NODES = "node_id_dict"
CLUSTER_CARDINALITY_NODE_MAPPING = "node_name_to_id_dict"

# GConf keys
class GconfKeys(enum.Enum):
    NODE_CONST = "node"
    SERVICE_CONST = "services"
    NAME_CONST = "name"
    CONSUL_ENDPOINTS_NUM_KEY = "cortx{_DELIM}external{_DELIM}consul{_DELIM}num_endpoints"
    CONSUL_ENDPOINT_KEY = "cortx{_DELIM}external{_DELIM}consul{_DELIM}endpoints[{endpoint_index}]"
    KAFKA_ENDPOINTS_NUM_KEY = "cortx{_DELIM}external{_DELIM}kafka{_DELIM}num_endpoints"
    KAFKA_ENDPOINT_KEY = "cortx{_DELIM}external{_DELIM}kafka{_DELIM}endpoints[{endpoint_index}]"
    NUM_CVG = "num_cvg"
    CVG_NAME = "node{_DELIM}{node_id}{_DELIM}cvg[{cvg_index}]{_DELIM}name"
    CVG_COUNT = "node{_DELIM}{node_id}{_DELIM}num_cvg"
    DATA_COUNT = "node{_DELIM}{node_id}{_DELIM}cvg[{cvg_index}]{_DELIM}devices{_DELIM}num_data"
    METADATA_COUNT = "node{_DELIM}{node_id}{_DELIM}cvg[{cvg_index}]{_DELIM}devices{_DELIM}num_metadata"
    DATA_DISK = "node{_DELIM}{node_id}{_DELIM}cvg[{cvg_index}]{_DELIM}devices{_DELIM}data[{d_index}]"
    METADATA_DISK = "node{_DELIM}{node_id}{_DELIM}cvg[{cvg_index}]{_DELIM}devices{_DELIM}metadata[{m_index}]"
