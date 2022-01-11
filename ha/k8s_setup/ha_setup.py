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
from urllib.parse import urlparse

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log

from ha.execute import SimpleCommand
from ha.k8s_setup import const
from ha.core.config.config_manager import ConfigManager
from ha.core.error import HaCleanupException
from ha.core.error import SetupError
from ha.k8s_setup.const import _DELIM
from ha.core.event_manager.event_manager import EventManager
from ha.core.event_manager.subscribe_event import SubscribeEvent
from ha.util.conf_store import ConftStoreSearch

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

    def get_machine_id(self):
        command = "cat /etc/machine-id"
        machine_id, err, rc = self._execute.run_cmd(command, check_error=True)
        Log.info(f"Read machine-id. Output: {machine_id}, Err: {err}, RC: {rc}")
        return machine_id.strip()

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

    def process(self):
        """
        Process config command.
        """
        try:
            consul_endpoints = Conf.get(self._index, f'cortx{_DELIM}external{_DELIM}consul{_DELIM}endpoints')
            #========================================================#
            # consul Service endpoints from cluster.conf             #
            #____________________ cluster.conf ______________________#
            # endpoints:                                             #
            # - tcp://consul-server.default.svc.cluster.local:8301   #
            # - http://consul-server.default.svc.cluster.local:8500  #
            #========================================================#
            # search for supported consul endpoint url from list of configured consul endpoints
            filtered_consul_endpoints = list(filter(lambda x: isinstance(x, str) and urlparse(x).scheme == const.consul_scheme, consul_endpoints))
            if not filtered_consul_endpoints:
                sys.stderr.write(f'Failed to get consul config. consul_config: {filtered_consul_endpoints}. \n')
                sys.exit(1)
            # discussed and confirmed to select the first hhtp endpoint
            consul_endpoint = filtered_consul_endpoints[0]

            kafka_endpoint = Conf.get(self._index, f'cortx{_DELIM}external{_DELIM}kafka{_DELIM}endpoints')
            if not kafka_endpoint:
                sys.stderr.write(f'Failed to get kafka config. kafka_config: {kafka_endpoint}. \n')
                sys.exit(1)
            # Dummy value fetched for now. This will be replaced by the key/path for the pod label onces that is avilable in confstore
            # Ref ticket EOS-25694
            data_pod_label = Conf.get(self._index, f'cortx{_DELIM}common{_DELIM}product_release')
            # TBD delete once data_pod_label is avilable from confstore
            data_pod_label = ['cortx-data', 'cortx-server']

            conf_file_dict = {'LOG' : {'path' : const.HA_LOG_DIR, 'level' : const.HA_LOG_LEVEL},
                         'consul_config' : {'endpoint' : consul_endpoint},
                         'kafka_config' : {'endpoints': kafka_endpoint},
                         'event_topic' : 'hare',
                         'data_pod_label' : data_pod_label,
                         'MONITOR' : {'message_type' : 'cluster_event', 'producer_id' : 'cluster_monitor'},
                         'EVENT_MANAGER' : {'message_type' : 'health_events', 'producer_id' : 'system_health',
                                            'consumer_group' : 'health_monitor', 'consumer_id' : '1'},
                         'FAULT_TOLERANCE' : {'message_type' : 'cluster_event', 'consumer_group' : 'event_listener',
                                              'consumer_id' : '1'},
                         'CLUSTER_STOP_MON' : {'message_type' : 'cluster_stop', 'consumer_group' : 'cluster_mon',
                                              'consumer_id' : '2'},
                         'NODE': {'resource_type': 'node'},
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
            ConfigManager.init("ha_setup")

            # Inside cluster.conf, cluster_id will be present under
            # "node".<actual POD machind id>."cluster_id". So,
            # in the similar way, confstore will have this key when
            # the cluster.conf load will taked place.
            # So, to get the cluster_id field from Confstore, we need machine_id
            machine_id = self.get_machine_id()
            cluster_id = Conf.get(self._index, f'node{_DELIM}{machine_id}{_DELIM}cluster_id')
            # site_id = Conf.get(self._index, f'node{_DELIM}{machine_id}{_DELIM}site_id')
            site_id = '1'
            # rack_id = Conf.get(self._index, f'node{_DELIM}{machine_id}{_DELIM}rack_id')
            rack_id = '1'
            conf_file_dict.update({'COMMON_CONFIG': {'cluster_id': cluster_id, 'rack_id': rack_id, 'site_id': site_id}})
            # TODO: Verify whether these newly added config is avilable in the confstore or not
            with open(const.HA_CONFIG_FILE, 'w+') as conf_file:
                yaml.dump(conf_file_dict, conf_file, default_flow_style=False)
            self._confstore = ConfigManager.get_confstore()

            Log.info(f'Populating the ha config file with consul_endpoint: {consul_endpoint}, \
                       data_pod_label: {data_pod_label}')

            Log.info('Performing event_manager subscription')
            event_manager = EventManager.get_instance()
            event_manager.subscribe(const.EVENT_COMPONENT, [SubscribeEvent(const.POD_EVENT, ["online", "failed"])])
            Log.info(f'event_manager subscription for {const.EVENT_COMPONENT}\
                       is successful for the event {const.POD_EVENT}')

            Log.info('Creating cluster cardinality')
            confStoreAPI = ConftStoreSearch()
            confStoreAPI.set_cluster_cardinality(self._index)

            Log.info("config command is successful")
            sys.stdout.write("config command is successful.\n")
        except TypeError as type_err:
            sys.stderr.write(f'HA config command failed: Type mismatch: {type_err}.\n')
        except yaml.YAMLError as exc:
            sys.stderr.write(f'Ha config failed. Invalid yaml configuration: {exc}.\n')
        except OSError as os_err:
            sys.stderr.write(f'HA Config failed. OS_error: {os_err}.\n')
        except Exception as c_err:
            sys.stderr.write(f'HA config command failed: {c_err}.\n')

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
