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
from ha.util.enum_list import EnumListMeta

#LOGS and config
CORTX_VERSION_1="1"
CORTX_VERSION_2="2"
HA_CLUSTER_SOFTWARE="corosync"
HACLUSTER_KEY = "cortx"
SERVER_NODE_KEY = "server_node"
RA_LOG_DIR="/var/log/seagate/cortx/ha"
RA_LOG_FILES = [f"{RA_LOG_DIR}/alert_monitor.log", f"{RA_LOG_DIR}/cluster_manager.log",
                f"{RA_LOG_DIR}/event_analyzerd.log", f"{RA_LOG_DIR}/event_manager.log",
                f"{RA_LOG_DIR}/health_monitor.log"]

PACEMAKER_LOG="/var/log/pacemaker.log"
AUTH_DIR="/var/lib/pcsd"
PCSD_LOG="/var/log/pcsd/pcsd.log"
HA_CMDS_OUTPUT="{}/ha_cmds_output".format(RA_LOG_DIR)
COROSYNC_LOG="/var/log/cluster"
PCSD_DIR="/var/log/pcsd"
LOG_DIR="/var/log"
CONFIG_DIR="/etc/cortx/ha"
SYSTEM_DIR="/etc/systemd/system"
SUPPORT_BUNDLE_ERR="{}/support_bundle.err".format(RA_LOG_DIR)
SUPPORT_BUNDLE_LOGS=[RA_LOG_DIR, PCSD_LOG, PACEMAKER_LOG, COROSYNC_LOG]
CORTX_SUPPORT_BUNDLE_LOGS=[RA_LOG_DIR, PCSD_LOG, PACEMAKER_LOG, CONFIG_DIR, COROSYNC_LOG]
DATASTORE_VERSION="v1"
CLUSTER_CONFSTORE_PREFIX = "cortx/ha/{}/".format(DATASTORE_VERSION)
HA_INIT_DIR="/var/cortx/ha/"
SOURCE_PATH="/opt/seagate/cortx/ha"
SOURCE_CONFIG_PATH="{}/conf/etc".format(SOURCE_PATH)
SOURCE_IEM_SCHEMA_PATH="{}/iem_ha.json".format(SOURCE_CONFIG_PATH)
RESOURCE_SCHEMA="{}/decision_monitor_conf.json".format(CONFIG_DIR)
RESOURCE_GLOBAL_INDEX="decision_monitor"
RULE_ENGINE_SCHAMA="{}/rules_engine_schema.json".format(CONFIG_DIR)
RULE_GLOBAL_INDEX="rules_engine"
HA_CONFIG_FILE="{}/ha.conf".format(CONFIG_DIR)
FIDS_CONFIG_FILE="{}/fids.json".format(CONFIG_DIR)
HA_GLOBAL_INDEX="ha_conf"
SOURCE_CONFIG_FILE="{}/ha.conf".format(SOURCE_CONFIG_PATH)
BACKUP_DEST_DIR="/opt/seagate/cortx/ha_backup"
BACKUP_DEST_DIR_CONF = "{}/conf".format(BACKUP_DEST_DIR)
BACKUP_CONFIG_FILE="{}/ha.conf".format(BACKUP_DEST_DIR_CONF)
BACKUP_DEST_DIR_CONSUL = "{}/Consul".format(BACKUP_DEST_DIR)
CORTX_CLUSTER_PACKAGES=["pacemaker", "corosync", "pcs", "cortx-py-utils", "cortx-csm", "cortx-motr", "cortx-hare", "cortx-s3server", "cortx-sspl"]
CIB_FILE="{}/cortx-r2-cib.xml".format(RA_LOG_DIR)
SOURCE_CLI_SCHEMA_FILE = "{}/cli_schema.json".format(SOURCE_CONFIG_PATH)
CLI_SCHEMA_FILE = "{}/cli_schema.json".format(CONFIG_DIR)
COMPONENTS_CONFIG_DIR = "{}/components".format(CONFIG_DIR)
SOURCE_HEALTH_HIERARCHY_FILE = "{}/system_health_hierarchy.json".format(SOURCE_CONFIG_PATH)
HEALTH_HIERARCHY_FILE = "{}/system_health_hierarchy.json".format(CONFIG_DIR)
IEM_SCHEMA="{}/iem_ha.json".format(CONFIG_DIR)
SOURCE_LOGROTATE_CONF_FILE = "{}/conf/logrotate/cortx_ha_log.conf".format(SOURCE_PATH)
LOGROTATE_CONF_DIR="/etc/logrotate.d"
SOURCE_ACTUATOR_SCHEMA="{}/actuator_req.json".format(SOURCE_CONFIG_PATH)
ACTUATOR_SCHEMA="{}/actuator_req.json".format(CONFIG_DIR)

# IEM DESCRIPTION string: To be removed
IEM_DESCRIPTION="WS0080010001,Node, The cluster has lost $host server. System is running in degraded mode. For more information refer the Troubleshooting guide. Extra Info: host=$host; status=$status;"

# Mini-provisioning
CLUSTER_CONFSTORE_NODES_KEY="nodes"

#Confstore delimiter
_DELIM=">"

# Node name mapping keys
PVTFQDN_TO_NODEID_KEY="pvtfqdn_to_nodeid"

# Cortx commands
CORTX_CLUSTER_NODE_ADD="cortx cluster add node --nodeid=<node> --username=<user> --password=<secret>"

# hare commands
HCTL_FETCH_FIDS="hctl fetch-fids --json"

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
USER_GROUP_HACLIENT="haclient"
USER_GROUP_ROOT="root"
USER_HA_INTERNAL="hauser"
CLUSTER_USER="hacluster"

NODE_DISCONNECTED="Disconnected"
NODE_ONLINE="Online"

# Systemd wrapper resource agent
HARE_FID_MAPPING_FILE="/var/lib/hare/consul-server-conf/consul-server-conf.json"

# PCS Commands
PCS_CLUSTER_START="pcs cluster start --all"
PCS_CLUSTER_START_NODE="pcs cluster start"
PCS_NODE_START="pcs cluster start <node>"
PCS_CLUSTER_ENABLE="pcs cluster enable"
PCS_CLUSTER_STATUS="pcs cluster status"
PCS_CLUSTER_UNSTANDBY="pcs cluster unstandby --all"
PCS_SETUP_CLUSTER="pcs cluster setup --start --name <cluster_name> <node>"
PCS_CLUSTER_NODE_AUTH="pcs cluster auth <node> -u <username> -p <password>"
PCS_CLUSTER_NODE_ADD="pcs cluster node add <node> --start --enable"
PCS_CLUSTER_NODE_REMOVE="pcs cluster node remove <node> --force"
PCS_CLUSTER_PCSD_STATUS="pcs status pcsd"
PCS_STATUS_NODES="pcs status nodes"
PCS_NODE_UNSTANDBY="pcs node unstandby <node>"
PCS_CLEANUP="pcs resource cleanup"
PCS_STONITH_ENABLE="pcs property set stonith-enabled=true"
PCS_STONITH_SHOW="pcs stonith show <resource_id>"
PCS_FAILCOUNT_STATUS="pcs resource failcount show"
PCS_NODE_CLEANUP= PCS_CLEANUP + " --node <node>"
PCS_STOP_NODE="pcs cluster stop <node> --request-timeout=<seconds>"
PCS_STOP_CLUSTER="pcs cluster stop --request-timeout=<seconds> --all"
PCS_STATUS = "pcs status"
PCS_CLUSTER_DESTROY="pcs cluster destroy"
PCS_CLUSTER_KILL="pcs cluster kill"
PCS_NODE_STANDBY="pcs node standby <node>"
PCS_CLUSTER_STANDBY="pcs node standby --all"
PCS_NODE_UNSTANDBY="pcs node unstandby <node>"
PCS_RESOURCE_REFRESH="pcs resource refresh --force"
PCS_DELETE_RESOURCE="pcs resource delete <resource> --force"
PCS_STONITH_DISABLE="pcs property set stonith-enabled=False"
PCS_BAN_RESOURCES="pcs resource ban <resource_id> <node>"
PCS_CLEAR_RESOURCES="pcs resource clear <resource_id> <node>"
LIST_PCS_RESOURCES = '/usr/sbin/crm_resource --list-raw'
DISABLE_STONITH="pcs resource disable stonith-<node>-clone"
ENABLE_STONITH="pcs resource enable stonith-<node>-clone"
CHECK_PCS_STANDBY_MODE = '/usr/sbin/crm_standby --query | awk \'{print $3}\''
GET_CLUSTER_STATUS = "crm_mon --as-xml"
GET_ONLINE_NODES_CMD = "crm_mon --as-xml"
GET_LOCAL_NODE_ID_CMD = "crm_node -i"
GET_LOCAL_NODE_NAME_CMD = "crm_node -n"

# Cluster manager
CM_CONTROLLER_INDEX="cluster_controller_interfaces"
CM_CONTROLLER_SCHEMA="{}/cluster_controller_interfaces.json".format(CONFIG_DIR)
CM_ELEMENT=["cluster", "node", "service", "storageset"]
RETRY_COUNT = 2
PCS_NODE_GROUP_SIZE = 3
NODE_CONTROLLER = "node_controller"
SERVICE_CONTROLLER = "service_controller"
CLUSTER_RETRY_COUNT = 6
BASE_WAIT_TIME = 5
NODE_STOP_TIMEOUT = 300 # 300 sec to stop single node
CLUSTER_STANDBY_UNSTANDBY_TIMEOUT = 600 # 600 sec to stop single node
NODE_POWERON_DELAY = 300 # Delay after node is powered-on before cluster start

# Event Analyzer
INCLUSION = "inclusion"
EXCLUSION = "exclusion"
ALERT_FILTER_INDEX = "alert_filter_rules"
ALERT_EVENT_INDEX = "alert_event_rules"
ALERT_FILTER_RULES_FILE = "{}/alert_filter_rules.json".format(CONFIG_DIR)
ALERT_EVENT_RULES_FILE = "{}/alert_event_rules.json".format(CONFIG_DIR)
SOURCE_ALERT_FILTER_RULES_FILE = "{}/alert_filter_rules.json".format(SOURCE_CONFIG_PATH)
SOURCE_ALERT_EVENT_RULES_FILE = "{}/alert_event_rules.json".format(SOURCE_CONFIG_PATH)
SYSTEM_EVENT_ANALYZER_SERVICE_FILE = "{}/event_analyzer.service".format(SYSTEM_DIR)
SOURCE_EVENT_ANALYZER_SERVICE_FILE = "{}/conf/service/event_analyzer.service".format(SOURCE_PATH)
SYSTEM_HEALTH_MONITOR_SERVICE_FILE = "{}/health_monitor.service".format(SYSTEM_DIR)
SOURCE_HEALTH_MONITOR_SERVICE_FILE = "{}/conf/service/health_monitor.service".format(SOURCE_PATH)
ACTUATOR_RESPONSE_TYPE= "actuator_response_type"
SENSOR_RESPONSE_TYPE= "sensor_response_type"
SPECIFIC_INFO = "specific_info"
INFO = "info"
COMPONENT = "component"
MODULE = "module"
RESOURCE_TYPE = "resource_type"
STONITH_AUTH_TYPE = 'PASSWORD'
logger_utility_iec_cmd="logger -i -p local3.err"

class STATUSES(Enum):
    IN_PROGRESS = "InProgress"
    SUCCEEDED = "Succeeded"
    PARTIAL = "Partial"
    FAILED = "Failed"
    WARNING = "warning"

class NODE_STATUSES(Enum):
    CLUSTER_OFFLINE = "Offline".lower() # Cluster not running on current node.
    STANDBY = "Standby".lower() # Cluster Running but resource are not running.
    ONLINE = "Online".lower() # Cluster and resource Running on current node.
    # STANDBY_WITH_RESOURCES_RUNNING: Cluster and few resource running, Unstable state.
    STANDBY_WITH_RESOURCES_RUNNING = "Standby with resource(s) running".lower()
    MAINTENANCE = "Maintenance".lower() # In maintenance mode, Resource not monitored.
    UNKNOWN = "Unknown".lower() # Unknown or Network problem
    POWEROFF = "Poweroff or Disconnected".lower() # Node is poweroff or disconnected from network.

# System Health
# Constants
class COMPONENTS(Enum):
    SERVER_HARDWARE = "server_hardware"
    SERVER_SERVICE = "server_service"
    SERVER = "server"
    STORAGE_COMPONENT = "storage_component"
    STORAGE = "storage"
    NODE = "node"
    RACK = "rack"
    SITE = "site"
    STORAGESET = "storageset"
    CLUSTER = "cluster"
    AGG_SERVICE = "agg_service"
    NODE_MAP = "node_map"

RESOURCE_LIST = "resource_list"
KEY = "key"

# Health update HA action status # TODO: move in health const class
class ACTION_STATUS(Enum):
    PENDING = "pending"
    COMPLETE = "complete"

class INSTALLATION_TYPE(Enum):
    HW = "hw"
    VM = "vm"
    SINGLE_VM = "single_vm"

# Alert attribute constants
class ALERT_ATTRIBUTES:
    USERNAME = "username"
    TITLE = "title"
    EXPIRES = "expires"
    SIGNATURE = "signature"
    TIME = "time"
    MESSAGE = "message"
    HEADER = "sspl_ll_msg_header"
    MSG_VERSION = "msg_version"
    SCHEMA_VERSION = "schema_version"
    SSPL_VERSION = "sspl_version"
    SENSOR_RESPONSE_TYPE = "sensor_response_type"
    ACTUATOR_RESPONSE_TYPE= "actuator_response_type"
    INFO = "info"
    EVENT_TIME = "event_time"
    RESOURCE_ID = "resource_id"
    SITE_ID = "site_id"
    NODE_ID = "node_id"
    CLUSTER_ID = "cluster_id"
    RACK_ID = "rack_id"
    RESOURCE_TYPE = "resource_type"
    DESCRIPTION = "description"
    ALERT_TYPE = "alert_type"
    SEVERITY = "severity"
    SPECIFIC_INFO = "specific_info"
    SOURCE = "source"
    COMPONENT = "component"
    MODULE = "module"
    EVENT = "event"
    IEC = "IEC"
    ALERT_ID = "alert_id"
    HOST_ID = "host_id"
    STATUS = "status"
    NAME = "name"
    ENCLOSURE_ID = "enclosure-id"
    DURABLE_ID = "durable-id"
    FANS = "fans"
    HEALTH_REASON = "health-reason"
    HEALTH = "health"
    LOCATION = "location"
    POSITION = "position"
    HEALTH_RECOMMENDATION = "health-recommendation"

# TBD combine ACTUATOR_ATTRIBUTES and ALERT_ATTRIBUTES to a single class
# or have common class and derive both from it
# Actuator request-response attributes
class ACTUATOR_ATTRIBUTES(ALERT_ATTRIBUTES):
    UUID = "uuid"
    REQUEST_PATH = "request_path"
    RESPONSE_DEST = "response_dest"
    TARGET_NODE_ID ="target_node_id"
    ACTUATOR_REQUEST_TYPE =  "actuator_request_type"
    STORAGE_ENCLOSURE =  "storage_enclosure"
    ENCLOSURE_REQUEST =  "enclosure_request"
    RESOURCE = "resource"
    COMMAND = "command"

# Timout = ACTUATOR_RESP_RETRY_COUNT * ACTUATOR_RESP_WAIT_TIME
ACTUATOR_RESP_RETRY_COUNT = 30
ACTUATOR_RESP_WAIT_TIME = 2
ACTUATOR_MSG_WAIT_TIME = 2

# Health event attribute constants
class EVENT_ATTRIBUTES:
    EVENT_ID = "event_id"
    EVENT_TYPE = "event_type"
    SEVERITY = "severity"
    SITE_ID = "site_id"
    RACK_ID = "rack_id"
    CLUSTER_ID = "cluster_id"
    STORAGESET_ID = "storageset_id"
    NODE_ID = "node_id"
    HOST_ID = "host_id"
    RESOURCE_TYPE = "resource_type"
    TIMESTAMP = "timestamp"
    RESOURCE_ID = "resource_id"
    SPECIFIC_INFO = "specific_info"

# Alert constants
class AlertEventConstants(Enum):
    ALERT_FILTER_TYPE = f"alert{_DELIM}filter_type"
    IEM_FILTER_TYPE = f"iem{_DELIM}filter_type"
    ALERT_RESOURCE_TYPE = f"alert{_DELIM}resource_type"
    IEM_COMPONENTS = f"iem{_DELIM}components"
    IEM_MODULES = f"iem{_DELIM}modules"


class CLUSTER_STATUS(Enum):
    OFFLINE = "offline"
    STANDBY = "standby"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    ONLINE = "online"

class SERVER_POWER_STATUS(Enum, metaclass=EnumListMeta):
    ON = "on"
    OFF = "off"
    UNKNOWN = "unknown"