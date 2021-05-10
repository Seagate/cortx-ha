# coding: utf8

import os
from shutil import copystat
import sys

from cortx.utils.log import Log
from ha.execute import SimpleCommand
from ha.const import (BACKUP_DEST_DIR_CONF, CONFIG_DIR, RA_LOG_DIR, \
                        LIST_PCS_RESOURCES, CHECK_PCS_STANDBY_MODE, \
                        CLUSTER_STANDBY_UNSTANDBY_TIMEOUT, PCS_CLUSTER_STANDBY, \
                        PCS_CLUSTER_UNSTANDBY)
from ha.setup.create_pacemaker_resources import create_all_resources


def check_for_any_resource_presence() -> None:
    '''Check if any resources are already present in a cluster.
       if yes, means, pre-upgrade steps failed. hence exit'''

    Log.info('Check for any resource presence in a cluster')

    resource_list = SimpleCommand().run_cmd(LIST_PCS_RESOURCES)

    resource_list[0].split('\n')

    if resource_list:
        Log.error('Some resources are already present in the cluster. \
                    Perform pre-Upgrade process again')
        sys.exit()

def is_cluster_standby_on() -> None:
    '''Check if cluster is in standby mode. If not, make standby mode ON'''

    Log.info('Check cluster is in standby mode')
    value = SimpleCommand().run_cmd(CHECK_PCS_STANDBY_MODE)

    value = value[0].split(' ')[3].strip('\n').split('=')

    if value[1].lower() != 'on':
        Log.error('cluster is not in standby mode. Making standby mode ON')
        standby_cmd = PCS_CLUSTER_STANDBY + f' --wait={CLUSTER_STANDBY_UNSTANDBY_TIMEOUT}'
        SimpleCommand().run_cmd(standby_cmd)
        Log.info('cluster standby mode on success')
    else:
        Log.info('#### All post-upgrade prerequisites are in place ####')

def restore_consul_backup():

    Log.info('Restoring the consul backup')

def load_config() -> None:
    '''Restores the config taken at the pre-upgrade step'''

    # TODO: Merging of old and new config if required
    src_dir = BACKUP_DEST_DIR_CONF
    dest_dir = CONFIG_DIR

    try:
        if os.path.exists(src_dir) and os.listdir(src_dir):
            copystat(src_dir, dest_dir)
    except Exception as e:
        Log.error(f'post upgrade failed at config restore phase: {e}')

def create_resources(_s3instances=None) -> None:
    '''create required resources'''
    create_all_resources(s3_instances=_s3instances)

def _unstandby_cluster() -> None:
    '''Unstandby the cluster'''

    unstandby_cmd = PCS_CLUSTER_UNSTANDBY + f' --wait={CLUSTER_STANDBY_UNSTANDBY_TIMEOUT}'
    SimpleCommand().run_cmd(unstandby_cmd)
    Log.info('### cluster is up and running ###')

def perform_post_upgrade(s3_instances=None):
    Log.init(service_name="post_disruptive_upgrade", log_path=RA_LOG_DIR, level="INFO")
    check_for_any_resource_presence()
    is_cluster_standby_on()
    load_config()
    create_resources(s3_instances)
    _unstandby_cluster()
