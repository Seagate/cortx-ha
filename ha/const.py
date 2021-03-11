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

from enum import Enum

#LOGS
RA_LOG_DIR="/var/log/seagate/cortx/ha"
PACEMAKER_LOG="/var/log/pacemaker.log"
PCSD_LOG="/var/log/pcsd/pcsd.log"
HA_CMDS_OUTPUT="{}/ha_cmds_output".format(RA_LOG_DIR)
COROSYNC_LOG="/var/log/cluster"
SUPPORT_BUNDLE_ERR="{}/support_bundle.err".format(RA_LOG_DIR)
SUPPORT_BUNDLE_LOGS=[RA_LOG_DIR, PCSD_LOG, PACEMAKER_LOG, COROSYNC_LOG]
CORTX_SUPPORT_BUNDLE_LOGS=[RA_LOG_DIR]

HA_INIT_DIR="/var/cortx/ha/"
CONFIG_DIR="/etc/cortx/ha"
SOURCE_CONFIG_PATH="/opt/seagate/cortx/ha/conf/etc"
RESOURCE_SCHEMA="{}/decision_monitor_conf.json".format(CONFIG_DIR)
RESOURCE_GLOBAL_INDEX="decision_monitor"
RULE_ENGINE_SCHAMA="{}/rules_engine_schema.json".format(CONFIG_DIR)
RULE_GLOBAL_INDEX="rules_engine"
HA_CONFIG_FILE="{}/ha.conf".format(CONFIG_DIR)
HA_GLOBAL_INDEX="ha_conf"
SOURCE_CONFIG_FILE="{}/ha.conf".format(SOURCE_CONFIG_PATH)
BACKUP_DEST_DIR="/opt/seagate/cortx/ha_backup"
BACKUP_DEST_DIR_CONF = "{}/conf".format(BACKUP_DEST_DIR)
BACKUP_DEST_DIR_CONSUL = "{}/Consul".format(BACKUP_DEST_DIR)

CURRENT_NODE_STATUS="self_node_status"
OTHER_NODE_STATUS="other_node_status"
CURRENT_NODE="self_node"
NODE_LIST="nodes"
LOCALHOST_KEY="local"

FILENAME_KEY="filename"
OCF_FILENAME="OCF_RESKEY_{}".format(FILENAME_KEY)
PATH_KEY="path"
OCF_PATH="OCF_RESKEY_{}".format(PATH_KEY)
OCF_NODE="OCF_RESKEY_node"
SERVICE_KEY="service"
OCF_SERVICE="OCF_RESKEY_{}".format(SERVICE_KEY)

STATE_RUNNING="monitoring"
STATE_START="starting"
STATE_STOP="stopping"

OCF_SUCCESS=0
OCF_ERR_GENERIC=1
OCF_ERR_ARGS=2
OCF_ERR_UNIMPLEMENTED=3
OCF_ERR_PERM=4
OCF_ERR_INSTALLED=5
OCF_ERR_CONFIGURED=6
OCF_NOT_RUNNING=7

CLUSTER_COMMAND="cluster"
NODE_COMMAND="node"
SERVICE_COMMAND="service"
BUNDLE_COMMAND="support_bundle"

PCS_CLUSTER_PACKAGES=["pacemaker", "corosync", "pcs"]
PCS_CLEANUP="pcs resource cleanup"
PCS_FAILCOUNT_STATUS="pcs resource failcount show"
PCS_STATUS = "pcs status"
PCS_CLUSTER_DESTROY="pcs cluster destroy"
CIB_FILE="/var/log/seagate/cortx/ha/cortx-r2-cib.xml"


NODE_DISCONNECTED="Disconnected"
NODE_ONLINE="Online"

HCTL_START="hctl start"
HCTL_STOP="hctl shutdown"
HCTL_STATUS="hctl status"
HCTL_STARTED_STATUS="Online"
HCTL_STOPPED_STATUS="Offline"

# Systemd wrapper resource agent
HARE_FID_MAPPING_FILE="/var/lib/hare/consul-server-conf/consul-server-conf.json"

CORTX_VERSION_1="1"
CORTX_VERSION_2="2"
PCS_CLUSTER_START_ALL="pcs cluster start --all"
PCS_CLUSTER_START="pcs cluster start"
PCS_CLUSTER_STATUS="pcs cluster status"
PCS_CLUSTER_UNSTANDBY="pcs cluster unstandby --all"
PCS_STATUS_NODES="pcs status nodes"
PCS_NODE_UNSTANDBY="pcs node unstandby <node>"
PCS_NODE_CLEANUP= PCS_CLEANUP + " --node <node>"
PCS_NODE_FAILCOUNT_STATUS= PCS_FAILCOUNT_STATUS + " --node <node>"

# Cluster manager
CM_CONTROLLER_INDEX="controller_interface"
CM_CONTROLLER_SCHEMA="{}/controller_interface.json".format(CONFIG_DIR)
CM_ELEMENT=["cluster", "node", "service", "storageset"]
CONTROLLER_FAILED="Failed"
CONTROLLER_SUCCESS="Success"
CONTROLLER_INPROGRESS="InProgress"
NO_FAILCOUNT = "No failcounts"
RETRY_COUNT = 2
PCS_NODE_START_GROUP_SIZE = 3
NODE_CONTROLLER = "node_controller"


class STATUSES(Enum):
    IN_PROGRESS = "InProgress"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"


class NODE_STATUSES(Enum):
    OFFLINE = "Offline"
    STANDBY = "Standby"
    ONLINE = "Online"
    STANDBY_WITH_RESOURCES_RUNNING = "Standby with resource(s) running"
    MAINTENANCE = "Maintenance"
    UNKNOWN = "Unknown"
