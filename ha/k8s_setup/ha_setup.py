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

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log

from ha.execute import SimpleCommand
from ha import const
from ha.k8s_setup import const
from ha.core.config.config_manager import ConfigManager
from ha.core.error import HaPrerequisiteException
from ha.core.error import HaConfigException
from ha.core.error import HaInitException
from ha.core.error import HaCleanupException
from ha.core.error import HaResetException
from ha.core.error import SetupError
from ha.k8s_setup.const import _DELIM
from ha.core.event_manager.event_manager import EventManager
from ha.core.event_manager.subscribe_event import SubscribeEvent


class Cmd:
    """
    Setup Command. This class provides methods for parsing arguments.
    """
    _index = "cortx"
    DEV_CHECK = False
    LOCAL_CHECK = False
    PRE_FACTORY_CHECK = False

    def __init__(self, args: dict):
        """
        Init method.
        """
        if args is not None:
            self._url = args.config
            Conf.load(self._index, self._url)
            self._args = args.args
        self._execute = SimpleCommand()
        self._confstore = ConfigManager.get_confstore()
        self._cluster_manager = None

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
            f"cmd   post_install, prepare, config, init, test, reset, cleanup\n"
            f"--config   Config URL")

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
        Cmd.DEV_CHECK = args.dev
        Cmd.LOCAL_CHECK = args.local
        Cmd.PRE_FACTORY_CHECK = args.pre_factory
        return args.command(args)

    @staticmethod
    def add_args(parser: str, cls: str, name: str):
        """
        Add Command args for parsing.
        """
        setup_arg_parser = parser.add_parser(cls.name, help='setup %s' % name)
        setup_arg_parser.add_argument('--config', help='Config URL')
        setup_arg_parser.add_argument('--dev', action='store_true', help='Dev check')
        setup_arg_parser.add_argument('--local', action='store_true', help='Local check')
        setup_arg_parser.add_argument('--pre-factory', action='store_true', help='Pre-factory check')
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
    def copy_file(source: str, dest: str):
        """
        Move file source to destination.

        Args:
            source (str): [description]
            dest (str): [description]
        """
        shutil.copy(source, dest)



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

        Log.info("Processing post_install command")
        Log.info("post_install command is successful")

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
        Log.info("Processing prepare command")
        Log.info("prepare command is successful")

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
        # Log.info("Processing config command")
        consul_endpoint = Conf.get(self._index, f'cortx{_DELIM}external{_DELIM}consul{_DELIM}endpoints[0]')
        # TODO: Uncomment whenever prometheus config will be available
        # Conf.get('cortx', 'cortx.external.prometheus.endpoints[0]')
        conf_file_dict = {'LOG' : {'path' : const.HA_LOG_DIR, 'level' : const.HA_LOG_LEVEL},
                         'consul_config' : {'endpoint' : consul_endpoint},
                         'prometheus_config' : {'endpoint' : None},
                         'event_topic' : 'hare'}
        with open(const.HA_CONFIG_FILE, 'w') as conf_file:
            yaml.dump(conf_file_dict, conf_file)

        # First populate the ha.conf and then do init. Because, in the init, this file will
        # be stored in the confstore as key values
        ConfigManager.init("ha_setup")
        Log.info(f'Populating the ha config file with consul_endpoint: {consul_endpoint}, \
                   prometheus_endpoint:')

        Log.info(f'Performing event_manager subscription for hare component with event as: ')
        event_manager = EventManager.get_instance()
        # TODO: For testing purpose, event list is hardcoded with below value
        # Change accordingly.
        event_list = SubscribeEvent("enclosure:hw:controller", ["online", "failed"])
        event_manager.subscribe("hare",[event_list])
        Log.info(f'subscription is successful')
        Log.info("config command is successful")


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
        Log.info("Processing init command")
        Log.info("init command is successful")

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
        Log.info("Processing test command")
        Log.info("test command is successful")


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
        Log.info("Processing reset command")
        try:
            # create new version of log file
            services = ["cortx_ha_log.conf"]
            for service in services:
                self._execute.run_cmd(f"logrotate --force /etc/logrotate.d/{service}")

            older_logs = []
            log_dirs = [const.HA_LOG_DIR]
            for log_dir in log_dirs:
                log_list = [file for file in os.listdir(log_dir) if file.split(".")[-1] not in ["log", "xml"]]
                for log_file in log_list:
                    older_logs.append(os.path.join(log_dir, log_file))

            self._remove_logs(older_logs)
        except Exception as e:
            sys.stderr.write(f"Cluster reset command failed. {traceback.format_exc()}, Error: {e}\n")
            raise HaResetException("Cluster reset failed")

    def _remove_logs(self, logs: list):
        """
        Remove logs.
        """
        for log in logs:
            ResetCmd.remove_file(log)

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

        except Exception as e:
            Log.error(f"Cluster cleanup command failed. Error: {e}")
            sys.stderr.write(f"Cluster cleanup command failed. {traceback.format_exc()}, Error: {e}\n")
            raise HaCleanupException("Cluster cleanup failed")
        Log.info("cleanup command is successful")


    def remove_config_files(self):
        """
        Remove file created by ha.
        """
        files = [const.CONFIG_DIR]

        for file in files:
            CleanupCmd.remove_file(file)

def main(argv: list):
    try:
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

        sys.stdout.write(f"Mini Provisioning {sys.argv[1]} configured successfully.\n")
    except Exception as err:
        Log.error("%s\n" % traceback.format_exc())
        sys.stderr.write(f"Setup command:{argv[1]} failed for cortx-ha. Error: {err}\n")
        return errno.EINVAL

if __name__ == '__main__':
    sys.exit(main(sys.argv))
