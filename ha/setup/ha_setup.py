#!/bin/env python3

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

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from cortx.utils.validator.v_pkg import PkgV
from cortx.utils.security.cipher import Cipher
from ha.execute import SimpleCommand
from ha import const
from ha.setup.create_cluster import cluster_auth, cluster_create
from ha.setup.create_pacemaker_resources import create_all_resources

class HaPrerequisiteException(Exception):
    """
    Exception to indicate that some error happened during HA prerequisite checks.
    """
    pass

class HaConfigException(Exception):
    """
    Exception to indicate that config command failed during cluster config.
    """
    pass

class HaCleanupException(Exception):
    """
    Exception to indicate that cleanup command failed due to some error.
    """
    pass

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
            f"usage: {prog} [-h] <cmd> <--config url> [--plan <TYPE>] <args>...\n"
            f"where:\n"
            f"cmd   post_install, config, init, test, upgrade, reset, cleanup, backup, restore\n"
            f"--config   Config URL\n"
            f"--plan   Test plan")

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
        setup_arg_parser.add_argument('--plan', nargs="?", default=[], help='Test plan')
        setup_arg_parser.add_argument('args', nargs='*', default=[], help='args')
        setup_arg_parser.set_defaults(command=cls)

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
            # Create a directory and copy config file
            if os.path.exists(const.HA_CONFIG_FILE):
                os.remove(const.HA_CONFIG_FILE)
            os.makedirs(const.CONFIG_DIR, exist_ok=True)
            shutil.copyfile(const.SOURCE_CONFIG_FILE, const.HA_CONFIG_FILE)
            Log.info(f"{self.name}: Copied HA config file.")
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
        command = "cat /etc/machine-id"
        machine_id, err, rc = self._execute.run_cmd(command, check_error=True)
        Log.info(f"Read machine-id. Output: {machine_id}, Err: {err}, RC: {rc}")
        minion_name = Conf.get(self._index, f"cluster.server_nodes.{machine_id.strip()}")
        nodelist.append(minion_name)
        # The config step will be called from primary node alwasys,
        # see how to get and use the node name then.

        # Read cluster name and cluster user
        cluster_name = Conf.get(self._index, 'corosync-pacemaker.cluster_name')
        cluster_user = Conf.get(self._index, 'corosync-pacemaker.user')

        # Read cluster user password and decrypt the same
        cluster_id = Conf.get(self._index, 'cluster.cluster_id')
        cluster_secret = Conf.get(self._index, 'corosync-pacemaker.secret')
        key = Cipher.generate_key(cluster_id, 'corosync-pacemaker')
        cluster_secret = Cipher.decrypt(key, cluster_secret.encode('ascii')).decode()

        # Get s3 instance count
        s3_instances = Conf.get(self._index, f"cluster.{minion_name}.s3_instances")
        if int(s3_instances) < 1:
            Log.error("Found non positive s3 instance count.")
            raise HaConfigException("Found non positive s3 instance count.")

        # Check if the cluster exists already, if yes skip creating the cluster.
        output, err, rc = self._execute.run_cmd(const.PCS_CLUSTER_STATUS, check_error=False)
        Log.info(f"Cluster status. Output: {output}, Err: {err}, RC: {rc}")
        if rc != 0:
            if(err.find("No such file or directory: 'pcs'") != -1):
                Log.error("Cluster config failed; pcs not installed")
                raise HaConfigException("Cluster config failed; pcs not installed")
            # If cluster is not created; create a cluster.
            elif(err.find("cluster is not currently running on this node") != -1):
                try:
                    Log.info(f"Creating cluster: {cluster_name} with node: {minion_name}")
                    cluster_auth(cluster_user, cluster_secret, nodelist)
                    cluster_create(cluster_name, nodelist)
                    Log.info(f"Created cluster: {cluster_name} successfully")
                    Log.info("Creating pacemaker resources")
                    create_all_resources(s3_instances=s3_instances)
                    Log.info("Created pacemaker resources successfully")
                except Exception as e:
                    Log.error(f"Cluster creation failed; destroying the cluster. Error: {e}")
                    output = self._execute.run_cmd(const.PCS_CLUSTER_DESTROY, check_error=True)
                    Log.info(f"Cluster destroyed. Output: {output}")
                    raise HaConfigException("Cluster creation failed")
            else:
                pass # Nothing to do
        else:
            # Cluster exists already, check if it is a new node and add it to the existing cluster.
             Log.info("The cluster exists already, check and add new node")
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
        pass # TBD

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
        desc = "HA Setup command"
        command = Cmd.get_command(desc, argv[1:])
        command.process()

    except Exception:
        Log.error("%s\n" % traceback.format_exc())
        sys.stderr.write(f"Setup command:{argv[1]} failed for cortx-ha\n")
        return errno.EINVAL

if __name__ == '__main__':
    # TBD: Import and use config_manager.py
    Conf.init(delim='.')
    Conf.load(const.HA_GLOBAL_INDEX, f"yaml://{const.SOURCE_CONFIG_FILE}")
    log_path = Conf.get(const.HA_GLOBAL_INDEX, "LOG.path")
    log_level = Conf.get(const.HA_GLOBAL_INDEX, "LOG.level")
    Log.init(service_name='ha_setup', log_path=log_path, level=log_level)
    sys.exit(main(sys.argv))
