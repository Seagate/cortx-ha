#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
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

import sys
import errno
import argparse
import inspect
import traceback
import os
import shutil
import yaml
import time
import uuid
from urllib.parse import urlparse

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log

from ha.execute import SimpleCommand
from ha.k8s_setup import const
from ha.core.config.config_manager import ConfigManager
from ha.core.error import HaCleanupException
from ha.core.error import SetupError
from ha.k8s_setup.const import _DELIM, GconfKeys, CONSUL_TRANSACTIONS_LIMIT
from ha.core.event_manager.event_manager import EventManager
from ha.core.event_manager.subscribe_event import SubscribeEvent
from ha.core.event_manager.resources import NODE_FUNCTIONAL_TYPES
from ha.util.conf_store import ConftStoreSearch
from ha.core.system_health.const import CLUSTER_ELEMENTS, HEALTH_EVENTS, EVENT_SEVERITIES, NODE_MAP_ATTRIBUTES, SPECIFIC_INFO_ATTRIBUTES
from ha.const import EVENT_ATTRIBUTES
from ha.fault_tolerance.const import FAULT_TOLERANCE_KEYS, HEALTH_EVENT_SOURCES, NOT_DEFINED
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.system_health.system_health import SystemHealth

class Cmd:
    """
    Setup Command. This class provides methods for parsing arguments.
    """
    _index = "cortx"

    def __init__(self, args: dict):
        """
        Init method.
        """
        if args is not None:
            self._url = args.config
            self._service = args.services
            # self._url This file can be only loaded once
            Conf.load(self._index, self._url)
            self._args = args.args
        self._confstore = None
        self._execute = SimpleCommand()

    @property
    def args(self) -> str:
        return self._args

    @property
    def url(self) -> str:
        return self._url

    @staticmethod
    def usage(prog: str):
        """
        Print usage instructions
        """
        sys.stderr.write(
            f"usage: {prog} [-h] <cmd> <--config url> <args>...\n"
            f"where:\n"
            f"cmd   post_install, prepare, config, init, test, reset, cleanup, upgrade\n"
            f"--config   Config URL.\n"
            f"--services   Service name.\n")

    @staticmethod
    def get_command(desc: str, argv: dict):
        """
        Return the Command after parsing the command line.
        """
        parser = argparse.ArgumentParser(desc)
        subparsers = parser.add_subparsers()
        cmds = inspect.getmembers(sys.modules[__name__])
        cmds = [(x, y) for x, y in cmds
            if x.endswith("Cmd") and x != "Cmd"]
        for name, cmd in cmds:
            cmd.add_args(subparsers, cmd, name)
        args = parser.parse_args(argv)
        return args.command(args)

    @staticmethod
    def add_args(parser: str, cls: str, name: str):
        """
        Add Command args for parsing.
        """
        setup_arg_parser = parser.add_parser(cls.name, help='setup %s' % name)
        setup_arg_parser.add_argument('--config', help='Config URL', required=True)
        setup_arg_parser.add_argument('--services', help='service name', required=True)
        setup_arg_parser.add_argument('args', nargs='*', default=[], help='args')
        setup_arg_parser.set_defaults(command=cls)

    @staticmethod
    def remove_file(file: str):
        """
        Check if file exist and delete existing file.

        Args:
            file ([str]): File or Dir name to be deleted.
        """
        if os.path.exists(file):
            if os.path.isfile(file):
                os.remove(file)
            elif os.path.isdir(file):
                shutil.rmtree(file)
            else:
                raise SetupError(f"{file} is not dir and file, can not be deleted.")

    @staticmethod
    def copy_file(src: str, dest: str):
        """
        copy a file from source to destination.

        Args:
            src (str): source file path
            dest (str): destination path
        """
        shutil.copy(src, dest)


class PostInstallCmd(Cmd):
    """
    PostInstall Setup Cmd
    """
    name = "post_install"

    def __init__(self, args: dict):
        """
        Init method.
        """
        super().__init__(args)

    def process(self):
        """
        Process post_install command.
        """
        sys.stdout.write("All post install checks for HA are upto date.\n")

class PrepareCmd(Cmd):
    """
    Prepare Setup Cmd
    """
    name = "prepare"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)

    def process(self):
        """
        Process prepare command.
        """
        sys.stdout.write("HA is prepared for performing mini provisioning.\n")

class ConfigCmd(Cmd):
    """
    Setup Config Cmd
    """
    name = "config"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)

    def _get_endpoints(self, num_endpoints_key: str, endpoint_key: str, scheme: str) -> str:
        """Get endpoints"""
        ep = None
        num_endpoints = Conf.get(self._index, num_endpoints_key.format(_DELIM=_DELIM))
        if num_endpoints is None:
            Log.error(f"Could not fetch configured number of endpoints: {num_endpoints}")
            raise SetupError(f"could not fetch configured number of endpoints: {num_endpoints}")
        try:
            for num in range(int(num_endpoints)):
                endpoint = Conf.get(self._index, endpoint_key.format(_DELIM=_DELIM, endpoint_index=num))
                if endpoint is None:
                    continue
                ep = ' '.join((filter(lambda x: isinstance(x, str) and \
                        urlparse(x).scheme == scheme, endpoint.split())))
                if ep: break
            if ep is None:
                Log.error("No endpoints are configured")
                raise SetupError("No endpoints are configured")
        except Exception as err:
            Log.error(f"Problem occured while fetcting the endpoint for consul or \
                        kakfa service: {err}")
            raise SetupError(f"Problem occured while fecting the endpoint for consul or \
                        fakfa service: {err}")
        return ep

    def process(self):
        """
        Process config command.
        """
        try:
            # Get log path from cluster.conf.
            log_path = Conf.get(self._index, f'cortx{_DELIM}common{_DELIM}storage{_DELIM}log')
            machine_id = Conf.machine_id
            ha_log_path = os.path.join(log_path, f'ha/{machine_id}')

            ConfigManager.init("ha_setup", log_path=ha_log_path, level="INFO", skip_load=True)
            # With new changes in GConf, consul http endpoint will be available at
            # cortx>external>consul>endpoints[1] key
            consul_endpoint = self._get_endpoints(GconfKeys.CONSUL_ENDPOINTS_NUM_KEY.value, \
                                GconfKeys.CONSUL_ENDPOINT_KEY.value, const.consul_scheme)
            #========================================================#
            # consul Service endpoints from cluster.conf             #
            #____________________ cluster.conf ______________________#
            # endpoints:                                             #
            # - tcp://consul-server.default.svc.cluster.local:8301   #
            # - http://consul-server.default.svc.cluster.local:8500  #
            #========================================================#
            if not consul_endpoint:
                sys.stderr.write(f'Failed to get consul config. consul_config: {consul_endpoint}. \n')
                sys.exit(1)
            # discussed and confirmed to select the http endpoint

            kafka_endpoints = []
            # With new changes in GConf, kafka endpoint will be available at
            # cortx>external>kafka>endpoints[0] key
            kafka_endpoint = self._get_endpoints(GconfKeys.KAFKA_ENDPOINTS_NUM_KEY.value, \
                                GconfKeys.KAFKA_ENDPOINT_KEY.value, const.kafka_scheme)
            if not kafka_endpoint:
                sys.stderr.write(f'Failed to get kafka config. kafka_config: {kafka_endpoint}. \n')
                sys.exit(1)
            kafka_endpoints.append(kafka_endpoint)

            health_comm_msg_type = FAULT_TOLERANCE_KEYS.MONITOR_HA_MESSAGE_TYPE.value

            conf_file_dict = {'LOG' : {'path' : ha_log_path, 'level' : const.HA_LOG_LEVEL},
                         'consul_config' : {'endpoint' : consul_endpoint},
                         'kafka_config' : {'endpoints': kafka_endpoints},
                         'event_topic' : 'hare',
                         'MONITOR' : {'message_type' : health_comm_msg_type, 'producer_id' : 'cluster_monitor'},
                         'EVENT_MANAGER' : {'message_type' : 'health_events', 'producer_id' : 'system_health',
                                            'consumer_group' : 'health_monitor', 'consumer_id' : '1'},
                         'FAULT_TOLERANCE' : {'message_type' : health_comm_msg_type, 'consumer_group' : 'event_listener',
                                              'consumer_id' : '1'},
                         'CLUSTER_STOP_MON' : {'message_type' : 'cluster_stop', 'consumer_group' : 'cluster_mon',
                                              'consumer_id' : '2'},
                         'CLUSTER': {'resource_type': ['node', 'disk', 'cvg', 'cluster']},
                         'SYSTEM_HEALTH' : {'num_entity_health_events' : 2}
                         }

            if not os.path.isdir(const.CONFIG_DIR):
                os.mkdir(const.CONFIG_DIR)

            # Open config file and dump yaml data from conf_file_dict
            with open(const.HA_CONFIG_FILE, 'w+') as conf_file:
                yaml.dump(conf_file_dict, conf_file, default_flow_style=False)

            Cmd.copy_file(const.SOURCE_HEALTH_HIERARCHY_FILE, const.HEALTH_HIERARCHY_FILE)
            # First populate the ha.conf and then do init. Because, in the init, this file will
            # be stored in the confstore as key values
            ConfigManager.init("ha_setup", initialize_log=False)

            # Inside cluster.conf, cluster_id will be present under
            # "node".<actual POD machind id>."cluster_id". So,
            # in the similar way, confstore will have this key when
            # the cluster.conf load will taked place.
            # So, to get the cluster_id field from Confstore, we need machine_id
            self._cluster_id = Conf.get(self._index, f'node{_DELIM}{machine_id}{_DELIM}cluster_id')
            # site_id = Conf.get(self._index, f'node{_DELIM}{machine_id}{_DELIM}site_id')
            self._site_id = NOT_DEFINED
            # rack_id = Conf.get(self._index, f'node{_DELIM}{machine_id}{_DELIM}rack_id')
            self._rack_id = NOT_DEFINED
            self._storageset_id = NOT_DEFINED
            conf_file_dict.update({'COMMON_CONFIG': {'cluster_id': self._cluster_id, 'rack_id': self._rack_id, 'site_id': self._site_id}})
            # TODO: Verify whether these newly added config is avilable in the confstore or not
            with open(const.HA_CONFIG_FILE, 'w+') as conf_file:
                yaml.dump(conf_file_dict, conf_file, default_flow_style=False)
            # Note: kv_enable_batch is setting True to commit all the kv keys in 1 time for time optimization.
            # if kv_enable_batch set to true then commit operation needs to run to put all the key values in store.
            kv_enable_batch_put = True
            self._confstore = ConfigManager.get_confstore(kv_enable_batch=kv_enable_batch_put)

            Log.info(f'Populating the ha config file with consul and kafka endpoint: \
                     {consul_endpoint}, {kafka_endpoints}')

            Log.info('Performing event_manager subscription')
            event_manager = EventManager.get_instance()
            event_manager.subscribe(const.EVENT_COMPONENT,
                                    [SubscribeEvent(const.POD_EVENT, ["online", "offline", "failed"], [
                                        NODE_FUNCTIONAL_TYPES.SERVER.value, NODE_FUNCTIONAL_TYPES.DATA.value])])

            Log.info(f'event_manager subscription for {const.EVENT_COMPONENT}\
                       is successful for the event {const.POD_EVENT}')
            # Stopped disk event subscribption to reduce consul accesses
            # till CORTX-29667 gets resolved
            #event_manager.subscribe(const.EVENT_COMPONENT, [SubscribeEvent(const.DISK_EVENT, ["online", "failed"])])
            #Log.info(f'event_manager subscription for {const.EVENT_COMPONENT}\
            #           is successful for the event {const.DISK_EVENT}')


            Log.info('Creating cluster cardinality')
            self._confStoreAPI = ConftStoreSearch()
            data_pods, server_pods, control_pods, _, _ = self._confStoreAPI.set_cluster_cardinality(self._index)

            # Init cluster,site,rack health
            self._add_cluster_component_health()

            # Note: if batch put is enabled needs to commit
            # to push all the local cashed values to consul server
            if kv_enable_batch_put:
                Log.debug(f"Pushing event manager subscription and cluster/site/rack health transactions to store")
                self._confstore.commit()

            # Init node health
            self._add_node_health(data_pods, server_pods, control_pods, kv_enable_batch_put)
            # Init cvg and disk health
            # Stopped disk, cvg resource key addition to consul to reduce consul accesses
            # till CORTX-29667 gets resolved
            # self._add_cvg_and_disk_health()

            # Note: if batch put is enabled needs to commit
            # to push all the local cashed values to consul server
            # if kv_enable_batch_put:
            #    self._confstore.commit()

            Log.info("config command is successful")
            sys.stdout.write("config command is successful.\n")
        except TypeError as type_err:
            Log.error(f'HA config command failed: Type mismatch: {type_err}.\n')
            sys.stderr.write(f'HA config command failed: Type mismatch: {type_err}.\n')
            raise
        except yaml.YAMLError as exc:
            Log.error(f'HA config command failed: Invalid yaml configuration: {exc}.\n')
            sys.stderr.write(f'Ha config failed. Invalid yaml configuration: {exc}.\n')
            raise
        except OSError as os_err:
            Log.error(f'HA config command failed: OS_error: {os_err}.\n')
            sys.stderr.write(f'HA Config failed. OS_error: {os_err}.\n')
            raise
        except Exception as c_err:
            Log.error(f'HA config command failed: {c_err}.\n')
            sys.stderr.write(f'HA config command failed: {c_err}.\n')
            raise

    def _add_cluster_component_health(self) -> None:
        """
        Add cluster, site ,rack health
        """
        specific_info={}
        self._add_health_event(node_id="",
                                   resource_type=CLUSTER_ELEMENTS.CLUSTER.value,
                                   resource_id=self._cluster_id,
                                   specific_info=specific_info)
        self._add_health_event(node_id="",
                                   resource_type=CLUSTER_ELEMENTS.SITE.value,
                                   resource_id=self._site_id,
                                   specific_info=specific_info)
        self._add_health_event(node_id="",
                                   resource_type=CLUSTER_ELEMENTS.RACK.value,
                                   resource_id=self._rack_id,
                                   specific_info=specific_info)


    def _add_node_health(self, data_node_ids, server_node_ids, control_node_ids, kv_enable_batch_put: bool = True) -> None:
        """
        Add node health
        """
        _, _, node_mapping = self._confStoreAPI.get_cluster_cardinality()
        node_id_list = []
        node_id_len = len(node_mapping)
        # cluster cardinality node_to_name mapping will have actual machine-ids
        # If that is part of one of the list from data, server or control node
        # list, then mark the respective functional type and update the specific info
        for node_id in node_mapping.values():
            node_id_list.append(node_id)
            if len(node_id_list) > CONSUL_TRANSACTIONS_LIMIT:
                # Note: if batch put is enabled needs to commit
                # to push all the local cashed values to consul server
                if kv_enable_batch_put:
                    Log.debug(f"pushing {CONSUL_TRANSACTIONS_LIMIT} node health transactions to store")
                    self._confstore.commit()
                node_id_list.clear()
                node_id_list.append(node_id)
            functional_type = None
            if node_id in data_node_ids:
                functional_type = NODE_FUNCTIONAL_TYPES.DATA.value
            elif node_id in server_node_ids:
                functional_type = NODE_FUNCTIONAL_TYPES.SERVER.value
            elif node_id in control_node_ids:
                functional_type = NODE_FUNCTIONAL_TYPES.CONTROL.value
            specific_info = {SPECIFIC_INFO_ATTRIBUTES.FUNCTIONAL_TYPE.value: functional_type}
            self._add_health_event(node_id=node_id,
                                   resource_type=CLUSTER_ELEMENTS.NODE.value,
                                   resource_id=node_id,
                                   specific_info=specific_info)
        if node_id_list:
            # Note: if batch put is enabled needs to commit
            # to push all the local cashed values to consul server
            if kv_enable_batch_put:
                Log.debug(f"pushing node health transactions to store")
                self._confstore.commit()

    def _add_cvg_and_disk_health(self) -> None:
        """
        Add CVG and disk health
        """
        _, _, node_mapping = self._confStoreAPI.get_cluster_cardinality()
        # Actual machine-ids will be part of node map. Hence iterate over the values
        # of that dictionary
        for node_id in node_mapping.values():
            cvg_list = ConftStoreSearch.get_cvg_list(self._index, node_id)
            if cvg_list:
                for cvg in cvg_list:
                    self._add_health_event(node_id=node_id,
                                           resource_type=CLUSTER_ELEMENTS.CVG.value,
                                           resource_id=cvg)
                    self._add_disk_health(node_id, cvg)

    def _add_disk_health(self, node_id, cvg_id) -> None:
        disk_list = ConftStoreSearch.get_disk_list_for_cvg(self._index, node_id, cvg_id)
        if disk_list:
            for disk in disk_list:
                self._add_health_event(node_id=node_id,
                                       resource_type=CLUSTER_ELEMENTS.DISK.value,
                                       resource_id=disk,
                                       specific_info={NODE_MAP_ATTRIBUTES.CVG_ID.value: cvg_id})

    def _add_health_event(self, node_id: str, resource_type: str,
                          resource_id: str, specific_info: dict=None) -> None:
        """
        Add health events for multiple resources (e.g. Node, CVG, disk)
        Args:
            node_id (str): node id
            resource_type (str): Resource type will be Node, CVG, disk, etc.
            resource_id (str): Resource id
            specific_info(dict): Ex. cvg_id for resource Disk
        """
        timestamp = str(int(time.time()))
        event_id = timestamp + str(uuid.uuid4().hex)
        health_event = {
            EVENT_ATTRIBUTES.SOURCE : HEALTH_EVENT_SOURCES.HA.value,
            EVENT_ATTRIBUTES.EVENT_ID : event_id,
            EVENT_ATTRIBUTES.EVENT_TYPE : HEALTH_EVENTS.UNKNOWN.value,
            EVENT_ATTRIBUTES.SEVERITY : EVENT_SEVERITIES.INFORMATIONAL.value,
            EVENT_ATTRIBUTES.SITE_ID : self._site_id,
            EVENT_ATTRIBUTES.RACK_ID : self._rack_id,
            EVENT_ATTRIBUTES.CLUSTER_ID : self._cluster_id,
            EVENT_ATTRIBUTES.STORAGESET_ID : self._storageset_id,
            EVENT_ATTRIBUTES.NODE_ID : node_id,
            EVENT_ATTRIBUTES.HOST_ID : None,
            EVENT_ATTRIBUTES.RESOURCE_TYPE : resource_type,
            EVENT_ATTRIBUTES.TIMESTAMP : timestamp,
            EVENT_ATTRIBUTES.RESOURCE_ID : resource_id,
            EVENT_ATTRIBUTES.SPECIFIC_INFO : specific_info
        }
        Log.debug(f"Adding initial health {health_event} for {resource_type} : {resource_id}")
        health_event = HealthEvent.dict_to_object(health_event)
        system_health = SystemHealth(self._confstore)
        system_health.process_event(health_event)


class InitCmd(Cmd):
    """
    Init Setup Cmd
    """
    name = "init"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)

    def process(self):
        """
        Process init command.
        """
        sys.stdout.write('HA initialization is done.\n')

class UpgradeCmd(Cmd):
    """
    Setup Upgrade Cmd
    """
    name = "upgrade"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)

    def process(self):
        """
        Process upgrade command.
        """
        sys.stdout.write("HA has been upgraded successfully\n")

class TestCmd(Cmd):
    """
    Test Cmd
    """
    name = "test"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)

    def process(self):
        """
        Process test command.
        """
        sys.stdout.write('Yet to be implemented...\n')

class ResetCmd(Cmd):
    """
    Reset Cmd
    """
    name = "reset"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)

    def process(self):
        """
        Process reset command.
        """
        sys.stdout.write('HA reset is yet to be implemented...\n')

class CleanupCmd(Cmd):
    """
    Cleanup Cmd
    """
    name = "cleanup"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)

    def process(self):
        """
        Process cleanup command.
        """
        Log.info("Processing cleanup command")
        try:
            # Delete the config file
            self.remove_config_files()
            if self._confstore is None:
                self._confstore = ConfigManager.get_confstore()
            self._confstore.delete(recurse=True)
            Log.info("consul keys are deleted")
            Log.info("cleanup command is successful")
            sys.stdout.write("cleanup command is successful.\n")
        except Exception as e:
            Log.error(f"cleanup command failed. Error: {e}")
            sys.stderr.write(f"cleanup command failed. {traceback.format_exc()}, Error: {e}\n")
            raise HaCleanupException("cleanup failed")


    def remove_config_files(self):
        """
        Remove file created by ha.
        """
        files = [const.CONFIG_DIR]

        for file in files:
            CleanupCmd.remove_file(file)
        Log.info("All the config files are removed")

def main(argv: list):
    try:
        if len(sys.argv) == 1:
            Cmd.usage("ha_setup")
            sys.exit(1)
        if sys.argv[1] == "cleanup":
            if not os.path.exists(const.HA_CONFIG_FILE):
                a_str = f'Cleanup can not be proceed as \
                           HA config file: {const.HA_CONFIG_FILE} \
                           is missing. Either cleanup is already done or there \
                           is some other problem'
                sys.stdout.write(a_str)
                return 0
            ConfigManager.init("ha_setup")

        desc = "HA Setup command"
        command = Cmd.get_command(desc, argv[1:])
        command.process()

    except Exception as err:
        Log.error("%s\n" % traceback.format_exc())
        sys.stderr.write(f"Setup command:{argv[1]} failed for cortx-ha. Error: {err}\n")
        return errno.EINVAL

if __name__ == '__main__':
    sys.exit(main(sys.argv))
