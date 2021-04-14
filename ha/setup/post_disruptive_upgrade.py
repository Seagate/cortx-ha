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
# abcheck_for_any_resource_presenceout this software or licensing, please email opensource@seagate.com or
# cortx-questions@seagate.com.

"""Module to do post-upgrade routines in scope of Disruptive Upgrade feature."""

from cortx.utils.log import Log
from ha.execute import SimpleCommand
from ha.const import (BACKUP_DEST_DIR_CONF, CONFIG_DIR)
from ha.setup.create_pacemaker_resources import create_all_resources


def check_for_any_resource_presence() -> None:
    '''Check if any resources are already present in a cluster.
       if yes, means, pre-upgrade steps failes hence exit.'''

    Log.info('Check for any resource presence in a cluster')

    list_pcs_resources = 'crm_resource --list-raw'
    resource_list = SimpleCommand().run_cmd(list_pcs_resources)

    resource_list.split('\n')

    if resource_list:
        Log.error('Some resources are already present. \
                    Perform Post-Upgrade again')
        return

def is_cluster_standby_on() -> None:
    '''Check if cluster is in standby mode. If not, make standby mode ON'''

    Log.info('Check cluster is in standby mode')
    check_standby_mode = 'crm_standby --query | awk '{print $3}' | cut -d '=' -f 2'
    value = SimpleCommand().run_cmd(check_standby_mode)

    if value.lower() != 'on':
        Log.error('cluster is not in standby mode. Making standby mode ON')
        standby_cmd = "pcs node standby --all --wait=600"
        SimpleCommand().run_cmd(check_standby_mode)
        Log.info('cluster standby mode on success')

def restore_consul_backup():

    Log.info('Restoring the consul backup')

   # TODO

def restore_config(src_dir: str = BACKUP_DEST_DIR_CONF, dest_dir: str = CONFIG_DIR) -> None:
    '''Restores the config taken at the pre-upgrade step'''

    # TODO: Merging of old and new config if required
    try:
        if os.path.exists(src_dir) and os.listdir(src_dir):
            copytree(src_dir, dest_dir)
    except Exception as e:
        Log.error(f'post upgrade failed at config restore phase: {e}')

def create_resources() -> None:
    '''create required resources'''
    Log.info('Creating the resources in the cluster')
    create_all_resources()

def _unstandby_cluster() -> None:
    '''Unstandby the cluster'''

    unstandby_cmd = "pcs node unstandby --all --wait=600"
    SimpleCommand().run_cmd(unstandby_cmd)

if __name__ == '__main__':
    check_for_any_resource_presence()
    is_cluster_standby_on()
    restore_config()
