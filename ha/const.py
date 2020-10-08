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

#LOGS
RA_LOG_DIR="/var/log/seagate/cortx/ha"
PACEMAKER_LOG="/var/log/pacemaker.log"
PCSD_LOG="/var/log/pcsd/pcsd.log"
HA_CMDS_OUTPUT="{}/ha_cmds_output".format(RA_LOG_DIR)
COROSYNC_LOG="/var/log/cluster/corosync.log"
SUPPORT_BUNDLE_ERR="{}/support_bundle.err".format(RA_LOG_DIR)
SUPPORT_BUNDLE_LOGS=[RA_LOG_DIR, PCSD_LOG, PACEMAKER_LOG, COROSYNC_LOG]

HA_INIT_DIR="/var/cortx/ha/"
CONFIG_DIR="/etc/cortx/ha"
RESOURCE_SCHEMA="{}/decision_monitor_conf.json".format(CONFIG_DIR)
RESOURCE_GLOBAL_INDEX="decision_monitor"
RULE_ENGINE_SCHAMA="{}/rules_engine_schema.json".format(CONFIG_DIR)
RULE_GLOBAL_INDEX="rules_engine"
HA_CONFIG_FILE="{}/ha.conf".format(CONFIG_DIR)
HA_GLOBAL_INDEX="ha_conf"

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

PCS_CLEANUP="pcs resource cleanup"
PCS_FAILCOUNT_STATUS="pcs resource failcount show"
PCS_STATUS="pcs status"

NODE_DISCONNECTED="Disconnected"
NODE_ONLINE="Online"