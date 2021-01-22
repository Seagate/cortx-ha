#!/bin/env python3

# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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
import pathlib
import os

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from cortx.utils.validator.v_pkg import PkgV
from cortx.utils.security.cipher import Cipher, CipherInvalidToken
sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))
from ha.execute import SimpleCommand
from ha import const

class Cmd:
    """Setup Command"""
    _index = "conf"

    def __init__(self, args: dict):
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
        """Print usage instructions"""

        sys.stderr.write(
            f"usage: {prog} [-h] <cmd> <--config url> [--plan <TYPE>] <args>...\n"
            f"where:\n"
            f"cmd   post_install, config, init, test, upgrade, reset, cleanup, backup, restore\n"
            f"--config   Config URL\n"
            f"--plan   Test plan")

    @staticmethod
    def get_command(desc: str, argv: dict):
        """Return the Command after parsing the command line."""

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
        """Add Command args for parsing."""

        parser1 = parser.add_parser(cls.name, help='setup %s' % name)
        parser1.add_argument('--config', help='Config URL')
        parser1.add_argument('--plan', nargs="?", default=[], help='Test plan')
        parser1.add_argument('args', nargs='*', default=[], help='args')
        parser1.set_defaults(command=cls)

class PostInstallCmd(Cmd):
    """PostInstall Setup Cmd"""
    name = "post_install"
    packages = ["pacemaker", "corosync", "pcs"]

    def __init__(self, args: dict):
        super().__init__(args)

    def process(self):
        # Pre-requisite checks are done here.
        # Make sure the pacemaker, corosync and pcs packages have been installed
        PkgV().validate('rpms', self.packages)

class ConfigCmd(Cmd):
    """Setup Config Cmd"""
    name = "config"

    def __init__(self, args):
        super().__init__(args)

    def process(self):
        # Read machine-id and using machine-id read node name from confstore
        # This node name will be used for adding the node to the cluster.
        command = "cat /etc/machine-id"
        machine_id, err, rc = self._execute.run_cmd(command, check_error=True)
        node_name = Conf.get(self._index, f"cluster.server_nodes.{machine_id.strip()}")

        # Read cluster name and cluster user
        cluster_name = Conf.get(self._index, 'corosync-pacemaker.cluster_name')
        cluster_user = Conf.get(self._index, 'corosync-pacemaker.user')
        
        # Read cluster user password and decrypt the same
        cluster_id = Conf.get(self._index, 'cluster.cluster_id')
        cluster_secret = Conf.get(self._index, 'corosync-pacemaker.secret')
        key = Cipher.generate_key(cluster_id, cluster_user)
        cluster_secret = Cipher.decrypt(key, cluster_secret.encode('ascii')).decode()

        # TBD: Call script for creating and configuring the cluster
        # TBD: Check if the cluster exists already

class InitCmd(Cmd):
    """Init Setup Cmd"""
    name = "init"

    def __init__(self, args):
        super().__init__(args)

    def process(self):
        pass # TBD

class TestCmd(Cmd):
    """Test Cmd"""
    name = "test"

    def __init__(self, args):
        super().__init__(args)

    def process(self):
        pass # TBD: Call script to check that all resources have been configured

class UpgradeCmd(Cmd):
    """Upgrade Cmd"""
    name = "upgrade"

    def __init__(self, args):
        super().__init__(args)

    def process(self):
        pass # TBD

class ResetCmd(Cmd):
    """Reset Cmd"""
    name = "reset"

    def __init__(self, args):
        super().__init__(args)

    def process(self):
        pass # TBD

class CleanupCmd(Cmd):
    """Cleanup Cmd"""
    name = "cleanup"

    def __init__(self, args):
        super().__init__(args)

    def process(self):
        pass # TBD: Call cluster destroy script here

class BackupCmd(Cmd):
    """Backup Cmd"""
    name = "backup"

    def __init__(self, args):
        super().__init__(args)

    def process(self):
        pass # TBD

class RestoreCmd(Cmd):
    """Restore Cmd"""
    name = "restore"

    def __init__(self, args):
        super().__init__(args)

    def process(self):
        pass # TBD

def main(argv: dict):
    try:
        desc = "HA Setup command"
        command = Cmd.get_command(desc, argv[1:])
        command.process()

    except Exception as e:
        sys.stderr.write("error: %s\n\n" % str(e))
        sys.stderr.write("%s\n" % traceback.format_exc())
        Cmd.usage(argv[0])
        return errno.EINVAL

if __name__ == '__main__':
    Conf.init(delim='.')
    Conf.load(const.HA_GLOBAL_INDEX, f"yaml://{const.HA_CONFIG_FILE}")
    log_path = Conf.get(const.HA_GLOBAL_INDEX, "LOG.path")
    log_level = Conf.get(const.HA_GLOBAL_INDEX, "LOG.level")
    Log.init(service_name='ha_setup', log_path=log_path, level=log_level)
    sys.exit(main(sys.argv))
