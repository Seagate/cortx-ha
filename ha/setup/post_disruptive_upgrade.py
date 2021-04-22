# coding: utf8

import os
from shutil import copytree, copystat

from cortx.utils.log import Log
from ha.execute import SimpleCommand
from ha.const import (BACKUP_DEST_DIR_CONF, CONFIG_DIR, RA_LOG_DIR, \
                        LIST_PCS_RESOURCES, CHECK_PCS_STANDBY_MODE, \
                        CLUSTER_STANDBY_UNSTANDBY_TIMEOUT, PCS_CLUSTER_STANDBY)
from ha.setup.create_pacemaker_resources import create_all_resources


def check_for_any_resource_presence() -> None:
    '''Check if any resources are already present in a cluster.
       if yes, means, pre-upgrade steps failed. hence exit'''

    Log.info('Check for any resource presence in a cluster')

    resource_list = SimpleCommand().run_cmd(LIST_PCS_RESOURCES)

    resource_list[0].split('\n')

    if resource_list:
        Log.error('Some resources are already present. \
                    Perform Upgrade again')
        return

def is_cluster_standby_on() -> None:
    '''Check if cluster is in standby mode. If not, make standby mode ON'''

    Log.info('Check cluster is in standby mode')
    value = SimpleCommand().run_cmd(CHECK_PCS_STANDBY_MODE)

    value = value[0].split(' ')[3].strip('\n').split('=')

    if value[1].lower() != 'on':
        Log.error('cluster is not in standby mode. Making standby mode ON')
        standby_cmd = PCS_CLUSTER_STANDBY + f' --wait={CLUSTER_STANDBY_UNSTANDBY_TIMEOUT}'
        SimpleCommand().run_cmd(check_standby_mode)
        Log.info('cluster standby mode on success')

def restore_consul_backup():

    Log.info('Restoring the consul backup')

def restore_config(src_dir: str = BACKUP_DEST_DIR_CONF, dest_dir: str = CONFIG_DIR) -> None:
    '''Restores the config taken at the pre-upgrade step'''

    # TODO: Merging of old and new config if required
    try:
        if os.path.exists(src_dir) and os.listdir(src_dir):
            copystat(src_dir, dest_dir)
    except Exception as e:
        Log.error(f'post upgrade failed at config restore phase: {e}')

def create_resources() -> None:
    '''create required resources'''
    Log.info('Creating the resources in the cluster')
    create_all_resources()

def _unstandby_cluster() -> None:
    '''Unstandby the cluster'''

    unstandby_cmd = PCS_CLUSTER_UNSTANDBY + f' --wait={CLUSTER_STANDBY_UNSTANDBY_TIMEOUT}'
    SimpleCommand().run_cmd(unstandby_cmd)

def perform_post_upgrade(s3instance=None):
    Log.init(service_name="post_disruptive_upgrade", log_path=RA_LOG_DIR, level="INFO")
    check_for_any_resource_presence()
    is_cluster_standby_on()
    restore_config()
    create_resources(s3instance)
