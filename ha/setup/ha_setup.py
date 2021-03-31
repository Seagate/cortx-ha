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
import json

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from cortx.utils.validator.v_pkg import PkgV
from cortx.utils.security.cipher import Cipher

from ha.execute import SimpleCommand
from ha import const
from ha.const import STATUSES
from ha.setup.create_pacemaker_resources import create_all_resources
from ha.core.cluster.cluster_manager import CortxClusterManager
from ha.core.config.config_manager import ConfigManager
from ha.core.error import HaPrerequisiteException
from ha.core.error import HaConfigException
from ha.core.error import HaInitException
from ha.core.error import HaCleanupException

class Cmd:
    """
    Setup Command. This class provides methods for parsing arguments.
    """
    _index = "conf"

    def __init__(self, args: dict):
        """
        Init method.
        """
        self._url = args.config
        Conf.load(self._index, self._url)
        self._args = args.args
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
            f"cmd   post_install, config, init, test, upgrade, reset, cleanup, backup, restore\n"
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
        return args.command(args)

    @staticmethod
    def add_args(parser: str, cls: str, name: str):
        """
        Add Command args for parsing.
        """
        setup_arg_parser = parser.add_parser(cls.name, help='setup %s' % name)
        setup_arg_parser.add_argument('--config', help='Config URL')
        setup_arg_parser.add_argument('args', nargs='*', default=[], help='args')
        setup_arg_parser.set_defaults(command=cls)

    @staticmethod
    def remove_file(file: str):
        """
        Check if file exist and delete existing file.

        Args:
            file ([str]): File name to be deleted.
        """
        if os.path.exists(file):
            os.remove(file)

    def get_machine_id(self):
        command = "cat /etc/machine-id"
        machine_id, err, rc = self._execute.run_cmd(command, check_error=True)
        Log.info(f"Read machine-id. Output: {machine_id}, Err: {err}, RC: {rc}")
        return machine_id.strip()

    def get_node_name(self):
        machine_id = self.get_machine_id()
        node_name = Conf.get(self._index, f"server_node.{machine_id}.network.data.private_fqdn")
        Log.info(f"Read node name: {node_name}")
        return node_name

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
        try:
            os.makedirs(const.CONFIG_DIR, exist_ok=True)
            # Create a directory and copy config file
            PostInstallCmd.remove_file(const.HA_CONFIG_FILE)
            shutil.copyfile(const.SOURCE_CONFIG_FILE, const.HA_CONFIG_FILE)
            PostInstallCmd.remove_file(const.CM_CONTROLLER_SCHEMA)
            shutil.copyfile(f"{const.SOURCE_CONFIG_PATH}/{const.CM_CONTROLLER_INDEX}.json",
                            const.CM_CONTROLLER_SCHEMA)
            Log.info(f"{self.name}: Copied HA configs file.")
            # Pre-requisite checks are done here.
            # Make sure the pacemaker, corosync and pcs packages have been installed
            PkgV().validate('rpms', const.PCS_CLUSTER_PACKAGES)
            Log.info("Found required cluster packages installed.")
        except Exception as e:
            Log.error(f"Failed prerequisite with Error: {e}")
            raise HaPrerequisiteException("post_install command failed")
        Log.info("post_install command is successful")

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
        Log.info("Processing config command")
        # Read machine-id and using machine-id read minion name from confstore
        # This minion name will be used for adding the node to the cluster.
        nodelist = []
        node_name = self.get_node_name()
        nodelist.append(node_name)

        # Read cluster name and cluster user
        machine_id = self.get_machine_id()
        cluster_id = Conf.get(self._index, f"server_node.{machine_id}.cluster_id")
        cluster_name = Conf.get(self._index, f"cluster.{cluster_id}.name")
        cluster_user = Conf.get(self._index, f"cortx.software.{const.HA_CLUSTER_SOFTWARE}.user")
        node_type = Conf.get(self._index, f"server_node.{machine_id}.type").strip()
        self._update_env(node_name, node_type, const.HA_CLUSTER_SOFTWARE)
        self._update_cluster_manager_config()

        # Read cluster user password and decrypt the same
        cluster_secret = Conf.get(self._index, f"cortx.software.{const.HA_CLUSTER_SOFTWARE}.secret")
        key = Cipher.generate_key(cluster_id, const.HACLUSTER_KEY)
        cluster_secret = Cipher.decrypt(key, cluster_secret.encode('ascii')).decode()
        s3_instances = self._get_s3_instance(machine_id)

        try:
            self._cluster_manager = CortxClusterManager()
            # Create cluster
            Log.info(f"Creating cluster: {cluster_name} with node: {node_name}")
            cluster_output: str = self._cluster_manager.cluster_controller.create_cluster(
                cluster_name, cluster_user, cluster_secret, node_name)
            Log.info(f"Cluster creation output: {cluster_output}")
            # TODO: Handle race condition cluster and resource create with global check.
            if json.loads(cluster_output).get("status") == STATUSES.SUCCEEDED.value:
                # Put cluster in standby mode
                standby_output: str = self._cluster_manager.node_controller.standby(node_name)
                Log.info(f"Put node in standby output: {standby_output}")
                if json.loads(standby_output).get("status") != STATUSES.FAILED.value:
                    Log.info("Creating pacemaker resources")
                    create_all_resources(s3_instances=s3_instances)
                    Log.info("Created pacemaker resources successfully")
                else:
                    raise HaConfigException(f"Failed to put cluster in standby mode. Error: {standby_output}")
            else:
                raise HaConfigException(f"Cluster creation failed. Error: {cluster_output}")
        except Exception as e:
            Log.error(f"Cluster creation failed; destroying the cluster. Error: {e}")
            output = self._execute.run_cmd(const.PCS_CLUSTER_DESTROY, check_error=True)
            Log.info(f"Cluster destroyed. Output: {output}")
            raise HaConfigException("Cluster creation failed")

    def _get_s3_instance(self, machine_id: str) -> int:
        """
        Return s3 instance

        Raises:
            HaConfigException: Raise exception for in-valide s3 count.

        Returns:
            [int]: Return s3 count.
        """
        try:
            s3_instances = Conf.get(self._index, f"server_node.{machine_id}.s3_instances")
            if int(s3_instances) < 1:
                raise HaConfigException(f"Found {s3_instances} which is invalid s3 instance count.")
            return int(s3_instances)
        except Exception as e:
            Log.error(f"Found {s3_instances} which is invalid s3 instance count. Error: {e}")
            raise HaConfigException(f"Found {s3_instances} which is invalid s3 instance count.")

    def _update_env(self, node_name: str, node_type: str, cluster_type: str) -> None:
        """
        Update env like VM, HW
        """
        Log.info(f"Detected {node_type} env and cluster_type {cluster_type}.")
        if "VM" == node_type.upper():
            Conf.set(const.HA_GLOBAL_INDEX, "CLUSTER_MANAGER.env", node_type.upper())
        else:
            # TODO: check if any env available other than vm, hw
            Conf.set(const.HA_GLOBAL_INDEX, "CLUSTER_MANAGER.env", "HW")
        Conf.set(const.HA_GLOBAL_INDEX, "CLUSTER_MANAGER.cluster_type", cluster_type)
        Conf.set(const.HA_GLOBAL_INDEX, "CLUSTER_MANAGER.local_node", node_name)
        Log.info("CONFIG: Update ha configuration files")
        Conf.save(const.HA_GLOBAL_INDEX)

    def _update_cluster_manager_config(self) -> None:
        """
        Update HA_CLUSTER_SOFTWARE
        """
        Log.info(f"Update {const.CM_CONTROLLER_SCHEMA}")
        with open(const.CM_CONTROLLER_SCHEMA, 'r') as fi:
            controller_schema = json.load(fi)
            for env in controller_schema:
                for ha_tool in controller_schema[env]:
                    if "<HA_CLUSTER_SOFTWARE>" == ha_tool:
                        controller_schema[env][const.HA_CLUSTER_SOFTWARE] = controller_schema[env][ha_tool]
                        del controller_schema[env]["<HA_CLUSTER_SOFTWARE>"]
            with open(const.CM_CONTROLLER_SCHEMA, 'w') as fi:
                json.dump(controller_schema, fi, indent=4)

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
        pass # TBD: Write code here to check that all resources have been configured.

class UpgradeCmd(Cmd):
    """
    Upgrade Cmd
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
        pass # TBD

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
        pass # TBD

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
            # Destroy the cluster
            output = self._execute.run_cmd(const.PCS_CLUSTER_DESTROY, check_error=True)
            Log.info(f"Cluster destroyed. Output: {output}")
            # Delete the config file
            if os.path.exists(const.HA_CONFIG_FILE):
                os.remove(const.HA_CONFIG_FILE)
            if os.path.exists(const.CM_CONTROLLER_SCHEMA):
                os.remove(const.CM_CONTROLLER_SCHEMA)
        except Exception as e:
            Log.error(f"Cluster cleanup command failed. Error: {e}")
            raise HaCleanupException("Cluster cleanup failed")
        Log.info("cleanup command is successful")

class BackupCmd(Cmd):
    """
    Backup Cmd
    """
    name = "backup"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)

    def process(self):
        """
        Process backup command.
        """
        pass # TBD

class RestoreCmd(Cmd):
    """
    Restore Cmd
    """
    name = "restore"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)

    def process(self):
        """
        Process restore command.
        """
        pass # TBD

def main(argv: dict):
    try:
        if sys.argv[1] == "post_install":
            Conf.init(delim='.')
            Conf.load(const.HA_GLOBAL_INDEX, f"yaml://{const.SOURCE_CONFIG_FILE}")
            log_path = Conf.get(const.HA_GLOBAL_INDEX, "LOG.path")
            log_level = Conf.get(const.HA_GLOBAL_INDEX, "LOG.level")
            Log.init(service_name='ha_setup', log_path=log_path, level=log_level)
        else:
            ConfigManager.init("ha_setup")

        desc = "HA Setup command"
        command = Cmd.get_command(desc, argv[1:])
        command.process()

        sys.stdout.write(f"Mini Provisioning {sys.argv[1]} configured sussesfully.\n")
    except Exception:
        Log.error("%s\n" % traceback.format_exc())
        sys.stderr.write(f"Setup command:{argv[1]} failed for cortx-ha.\n")
        return errno.EINVAL

if __name__ == '__main__':
    sys.exit(main(sys.argv))
