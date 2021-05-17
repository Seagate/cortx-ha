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
# about this software or licensing, please email opensource@seagate.com or
# cortx-questions@seagate.com.

"""Module which performs post-upgrade routines for the Disruptive Upgrade feature."""

import os
from shutil import copystat, copyfile
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from cortx.utils.log import Log
import yaml
from ha.core.error import UpgradeError
from ha.execute import SimpleCommand
from ha.const import (BACKUP_DEST_DIR_CONF, CONFIG_DIR, SOURCE_CONFIG_PATH,
                        RA_LOG_DIR, CHECK_PCS_STANDBY_MODE, SOURCE_CONFIG_FILE, \
                        CLUSTER_STANDBY_UNSTANDBY_TIMEOUT, PCS_CLUSTER_STANDBY, \
                        PCS_CLUSTER_UNSTANDBY)
from ha.setup.create_pacemaker_resources import create_all_resources


def _get_cib_xml() -> Element:
    """Call `pcs cluster cib` and return XML object for further parsing."""
    output, _, _ = SimpleCommand().run_cmd("pcs cluster cib")
    return ElementTree.fromstring(output)

def _check_for_any_resource_presence() -> None:
    '''Check if any resources are already present in a cluster.
       if yes, means, pre-upgrade steps failed. hence exit'''

    Log.info('Check for any resource presence in a cluster')

    root = _get_cib_xml()
    resource_list = [e.attrib["id"] for e in root.findall(".//lrm_resource")
                if "id" in e.attrib]

    if resource_list:
        raise UpgradeError('Some resources are already present in the cluster. \
                            Perform Upgrade process again')


def _is_cluster_standby_on() -> None:
    '''Check if cluster is in standby mode. If not, make standby mode ON'''

    Log.info('Check cluster is in standby mode')
    value = SimpleCommand().run_cmd(CHECK_PCS_STANDBY_MODE)

    standby_value = value[0].split(' ')[3].strip('\n').split('=')

    if standby_value[1].lower() != 'on':
        Log.warn('cluster is not in standby mode.')
        Log.info('switching the cluster in standby mode for performing post upgrade routines')
        _switch_cluster_mode(PCS_CLUSTER_STANDBY)
    Log.info('#### All post-upgrade prerequisites are in place ####')

def _restore_consul_backup():

    Log.info('Restoring the consul backup')

def _yaml_to_dict(yaml_file=None):
    '''
       Convert yaml format key value info i the form of
       python dictionary key value
    '''
    if yaml_file is None:
        raise UpgradeError('yaml file path can not be None. Please provide the \
                 HA yaml conf file path for conversion')
    with open(yaml_file, 'r') as conf_file:
        file_as_dict = yaml.safe_load(conf_file)
    return file_as_dict

def _load_config(ha_source_conf: str = SOURCE_CONFIG_FILE, \
                 ha_backup_conf: str = BACKUP_DEST_DIR_CONF) -> None:
    '''
       Load the new config at proper location after the
       RPM upgrade as part of post-upgrade process
    '''

    dest_dir = CONFIG_DIR
    new_src_dir = SOURCE_CONFIG_PATH

    # Convert yaml to dictionary
    old_backup_conf_dict = _yaml_to_dict(ha_backup_conf)
    new_conf_dict = _yaml_to_dict(ha_source_conf)

    # convert dictionary to set data structure
    old_conf_set = set(old_backup_conf_dict)
    new_conf_set = set(new_conf_dict)

    # Get the new conf added after upgrade using the set operation
    new_conf_keys_set = new_conf_set - old_conf_set

    Log.info(f"##### new conf key set : {new_conf_keys_set}")
    upgraded_conf= {}
    # Iterate over the new set of keys and add it to the dictionary
    for new_conf_key in new_conf_keys_set:
        upgraded_conf[new_conf_key] = new_conf_dict[new_conf_key]

    Log.info(f"##### upgraded conf: {upgraded_conf}")
    # append the new conf keys to backup_conf file
    with open(ha_backup_conf, 'a') as outfile:
        yaml.dump(upgraded_conf, outfile, default_flow_style=False)

    try:
        # Finally copy the updated backup conf file to a source
        copyfile(ha_backup_conf, ha_source_conf)

        # At last, copy the whole source directory which has updated
        # conf to a desired location
        if os.path.exists(new_src_dir) and os.listdir(new_src_dir):
            copystat(new_src_dir, dest_dir)
    except Exception as err:
        raise UpgradeError('Failed to load the new config after \
                       upgrading the RPM. Please retry Upgrade process again') \
                       from err

def _create_resources(_s3instances=None) -> None:
    '''create required resources'''
    create_all_resources(s3_instances=_s3instances)

def _switch_cluster_mode(cluster_mode, retry_count=0) -> None:
    '''
       Perform cluster operation to change the mode such as standby or
       unstandby and also retries the operation
    '''
    try:
        cluster_switch_mode_command = cluster_mode + f' --wait={CLUSTER_STANDBY_UNSTANDBY_TIMEOUT}'
        SimpleCommand().run_cmd(cluster_switch_mode_command)
    except Exception as err:
        if retry_count != 3:
            retry_count += 1
            _switch_cluster_mode(cluster_mode, retry_count)
        raise UpgradeError('Failed to switch the mode of the cluster. \
                            Retry upgrade again') from err

def _unstandby_cluster() -> None:
    '''Unstandby the cluster'''

    _switch_cluster_mode(PCS_CLUSTER_UNSTANDBY)
    Log.info('### cluster is up and running ###')

def perform_post_upgrade(s3_instances=None):
    '''Starting routine for post-upgrade process'''
    Log.init(service_name="post_disruptive_upgrade", log_path=RA_LOG_DIR, level="INFO")
    _check_for_any_resource_presence()
    _is_cluster_standby_on()
    _load_config()
    _create_resources(s3_instances)
    _unstandby_cluster()
