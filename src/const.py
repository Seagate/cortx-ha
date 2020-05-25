HA_INIT_DIR='/var/cortx/ha/'
RA_LOG_DIR='/var/log/seagate/cortx/ha'
RESOURCE_SCHEMA='/etc/cortx/ha/decision_monitor_conf.json'

CURRENT_NODE_STATUS='self_node_status'
OTHER_NODE_STATUS='other_node_status'
CURRENT_NODE='self_node'
NODE_LIST='nodes'
LOCALHOST_KEY='local'

FILENAME_KEY='filename'
OCF_FILENAME='OCF_RESKEY_{}'.format(FILENAME_KEY)
PATH_KEY='path'
OCF_PATH='OCF_RESKEY_{}'.format(PATH_KEY)
OCF_NODE='OCF_RESKEY_node'
SERVICE_KEY='service'
OCF_SERVICE='OCF_RESKEY_{}'.format(SERVICE_KEY)

OCF_SUCCESS=0
OCF_ERR_GENERIC=1
OCF_ERR_ARGS=2
OCF_ERR_UNIMPLEMENTED=3
OCF_ERR_PERM=4
OCF_ERR_INSTALLED=5
OCF_ERR_CONFIGURED=6
OCF_NOT_RUNNING=7

S3_IEM_KEY="node_iem_s3"
S3_IEM_ACTION=["pcs resource restart ldap-clone",
               "pcs resource restart s3auth-clone"]