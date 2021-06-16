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
import grp, pwd
from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from cortx.utils.validator.v_pkg import PkgV
from cortx.utils.security.cipher import Cipher

from ha.execute import SimpleCommand
from ha import const
from ha.const import STATUSES
from ha.setup.create_pacemaker_resources import create_all_resources
from ha.setup.post_disruptive_upgrade import perform_post_upgrade
from ha.core.cluster.cluster_manager import CortxClusterManager
from ha.core.config.config_manager import ConfigManager
from ha.remote_execution.ssh_communicator import SSHRemoteExecutor
from ha.core.error import HaPrerequisiteException
from ha.core.error import HaConfigException
from ha.core.error import HaInitException
from ha.core.error import HaCleanupException
from ha.core.error import SetupError
from ha.setup.cluster_validator.cluster_test import TestExecutor

class Cmd:
    """
    Setup Command. This class provides methods for parsing arguments.
    """
    _index = "conf"
    DEV_CHECK = False
    LOCAL_CHECK = False
    PROV_CONFSTORE = "provisioner"
    HA_CONFSTORE = "confstore"

    def __init__(self, args: dict):
        """
        Init method.
        """
        self._url = args.config
        Conf.load(self._index, self._url)
        self._args = args.args
        self._execute = SimpleCommand()
        self._confstore = ConfigManager._get_confstore()
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
            f"cmd   post_install, prepare, config, init, test, upgrade, reset, cleanup, backup, restore\n"
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
        Cmd.remove_file(dest)
        shutil.copyfile(source, dest)

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

    def get_nodelist(self, fetch_from: str = None) -> list:
        """
        Get nodelist from provisioner or confstore

        Args:
            fetch_from (str): Options from where to fetch.

        Returns:
            list: List of nodes.
        """
        nodelist: list = []
        fetch_from = Cmd.HA_CONFSTORE if fetch_from is None else fetch_from
        if fetch_from == Cmd.HA_CONFSTORE:
            cluster_nodes = self._confstore.get(const.CLUSTER_CONFSTORE_NODES_KEY)
            if cluster_nodes is None:
                return nodelist
            for key in cluster_nodes:
                nodelist.append(key.split('/')[-1])
        elif fetch_from == Cmd.PROV_CONFSTORE:
            nodes_schema = Conf.get(self._index, "server_node")
            machine_ids: list = list(nodes_schema.keys())
            for machine in machine_ids:
                nodelist.append(Conf.get(self._index, f"server_node.{machine}.network.data.private_fqdn"))
        else:
            raise SetupError(f"Failed to get nodelist, Invalid options {fetch_from}")
        Log.info(f"Found total Nodes: {len(nodelist)}, Nodes: {nodelist}, in {fetch_from}")
        return nodelist

    def get_installation_type(self):
        hw_type = ConfigManager.get_hw_env()
        if hw_type is not None:
            install_type = hw_type.lower()
        else:
            Log.error("Error: Can not fetch h/w env from Config.")
            raise HaConfigException("h/w env not present in config.")

        nodes = self.get_nodelist(fetch_from=Cmd.HA_CONFSTORE)
        if len(nodes) == 1 and install_type == const.INSTALLATION_TYPE.VM:
            install_type = const.INSTALLATION_TYPE.SINGLE_VM

        Log.info(f"Nodes count = {len(nodes)}, Install type = {install_type}")

        return install_type

    def standby_node(self, node_name: str) -> None:
        """
        Put node in standby

        Args:
            node_name (str): Node name.
        """
        standby_output: str = self._cluster_manager.node_controller.standby(node_name)
        Log.info(f"Put node in standby output: {standby_output}")
        if json.loads(standby_output).get("status") == STATUSES.FAILED.value:
            raise HaConfigException(f"Failed to put cluster in standby mode. Error: {standby_output}")

    @staticmethod
    def get_s3_instance(machine_id: str) -> int:
        """
        Return s3 instance

        Raises:
            HaConfigException: Raise exception for in-valide s3 count.

        Returns:
            [int]: Return s3 count.
        """
        try:
            s3_instances = Conf.get(Cmd._index, f"server_node.{machine_id}.s3_instances")
            if int(s3_instances) < 1:
                raise HaConfigException(f"Found {s3_instances} which is invalid s3 instance count.")
            return int(s3_instances)
        except Exception as e:
            Log.error(f"Found {s3_instances} which is invalid s3 instance count. Error: {e}")
            raise HaConfigException(f"Found {s3_instances} which is invalid s3 instance count.")

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
            if os.path.exists(const.CONFIG_DIR):
                shutil.rmtree(const.CONFIG_DIR)
            os.makedirs(const.CONFIG_DIR, exist_ok=True)
            # Create a directory and copy config file
            PostInstallCmd.copy_file(const.SOURCE_CONFIG_FILE, const.HA_CONFIG_FILE)
            PostInstallCmd.copy_file(f"{const.SOURCE_CONFIG_PATH}/{const.CM_CONTROLLER_INDEX}.json",
                            const.CM_CONTROLLER_SCHEMA)
            PostInstallCmd.copy_file(const.SOURCE_ALERT_FILTER_RULES_FILE, const.ALERT_FILTER_RULES_FILE)
            PostInstallCmd.copy_file(const.SOURCE_CLI_SCHEMA_FILE, const.CLI_SCHEMA_FILE)
            PostInstallCmd.copy_file(const.SOURCE_SERVICE_FILE, const.SYSTEM_SERVICE_FILE)
            self._execute.run_cmd("systemctl daemon-reload")
            Log.info(f"{self.name}: Copied HA configs file.")
            # Pre-requisite checks are done here.
            # Make sure that cortx necessary packages have been installed
            if PostInstallCmd.DEV_CHECK != True:
                PkgV().validate('rpms', const.CORTX_CLUSTER_PACKAGES)
            Log.info("Found required cluster packages installed.")
            # Check user and group
            groups = [g.gr_name for g in grp.getgrall() if const.CLUSTER_USER in g.gr_mem]
            gid = pwd.getpwnam(const.CLUSTER_USER).pw_gid
            groups.append(grp.getgrgid(gid).gr_name)
            if not const.USER_GROUP_HACLIENT in groups:
                Log.error("hacluster is not a part of the haclient group")
                raise HaPrerequisiteException("post_install command failed")
            else:
                Log.info("hacluster is a part of the haclient group")

        except Exception as e:
            Log.error(f"Failed prerequisite with Error: {e}")
            raise HaPrerequisiteException("post_install command failed")

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
        self._cluster_manager = CortxClusterManager(default_log_enable=False)

    def process(self):
        """
        Process config command.
        """
        Log.info("Processing config command")
        # Read machine-id and using machine-id read minion name from confstore
        # This minion name will be used for adding the node to the cluster.
        node_name: str = self.get_node_name()
        nodelist: list = self.get_nodelist(fetch_from=ConfigCmd.PROV_CONFSTORE)

        # Read cluster name and cluster user
        machine_id = self.get_machine_id()
        cluster_id = Conf.get(self._index, f"server_node.{machine_id}.cluster_id")
        cluster_name = Conf.get(self._index, f"cluster.{cluster_id}.name")
        cluster_user = Conf.get(self._index, f"cortx.software.{const.HA_CLUSTER_SOFTWARE}.user")
        node_type = Conf.get(self._index, f"server_node.{machine_id}.type").strip()

        # Read cluster user password and decrypt the same
        cluster_secret = Conf.get(self._index, f"cortx.software.{const.HA_CLUSTER_SOFTWARE}.secret")
        key = Cipher.generate_key(cluster_id, const.HACLUSTER_KEY)
        cluster_secret = Cipher.decrypt(key, cluster_secret.encode('ascii')).decode()
        mgmt_info: dict = self._get_mgmt_vip(machine_id, cluster_id)
        s3_instances = ConfigCmd.get_s3_instance(machine_id)

        self._update_env(node_name, node_type, const.HA_CLUSTER_SOFTWARE, s3_instances)
        self._fetch_fids()
        self._update_cluster_manager_config()

        # Update cluster and resources
        Log.info("Checking if cluster exists already")
        cluster_exists = bool(json.loads(self._cluster_manager.cluster_controller.cluster_exists()).get("msg"))
        Log.info(f"Cluster exists? {cluster_exists}")

        if not cluster_exists:
            node_count: int = len(self.get_nodelist(fetch_from=ConfigCmd.HA_CONFSTORE))
            if node_count == 0:
                Log.info(f"Creating cluster: {cluster_name} with node: {node_name}")
                # Create cluster
                try:
                    self._create_cluster(cluster_name, cluster_user, cluster_secret, node_name)
                    self._create_resource(s3_instances=s3_instances, mgmt_info=mgmt_info, node_count=len(nodelist))
                    self._confstore.set(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}")
                except Exception as e:
                    Log.error(f"Cluster creation failed; destroying the cluster. Error: {e}")
                    # output = self._execute.run_cmd(const.PCS_CLUSTER_DESTROY)
                    # Log.error(f"Cluster destroyed. Output: {output}")
                    self._cluster_manager.cluster_controller.destroy_cluster()
                    # Delete the node from nodelist if it was added in the store
                    if self._confstore.key_exists(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}"):
                        self._confstore.delete(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}")
                    raise HaConfigException("Cluster creation failed")
                # Add Other Node
                for node in nodelist:
                    if node != node_name:
                        Log.info(f"Adding node {node} to Cluster {cluster_name}")
                        self._add_node(node, cluster_user, cluster_secret)
            else:
                # Add node with SSH
                self._add_node_remotely(node_name, cluster_user, cluster_secret)
        else:
            for node in nodelist:
                if node != node_name:
                    Log.info(f"Adding node {node} to Cluster {cluster_name}")
                    self._add_node(node, cluster_user, cluster_secret)
        self._execute.run_cmd(const.PCS_CLEANUP)
        Log.info("config command is successful")

    def _create_resource(self, s3_instances, mgmt_info, node_count):
        Log.info("Creating pacemaker resources")
        try:
            # TODO: create resource if not already exists.
            create_all_resources(s3_instances=s3_instances, mgmt_info=mgmt_info, node_count=node_count)
        except Exception as e:
            Log.info(f"Resource creation failed. Error {e}")
            raise HaConfigException("Resource creation failed.")
        Log.info("Created pacemaker resources successfully")

    def _create_cluster(self, cluster_name: str, cluster_user: str, cluster_secret: str, node_name: str):
        """
        Create cluster on first node.

        Args:
            cluster_name (str): Cluster Name
            cluster_user (str): Cluster User
            cluster_secret (str): Cluster Secret
            node_name (str): Node name
        """
        try:
            cluster_exists = self._confstore.key_exists(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}")
            if cluster_exists:
                Log.info(f"Cluster already created on node {node_name}")
                return
            cluster_output: str = self._cluster_manager.cluster_controller.create_cluster(
                            cluster_name, cluster_user, cluster_secret, node_name)
            Log.info(f"Cluster creation output: {cluster_output}")
            if json.loads(cluster_output).get("status") != STATUSES.SUCCEEDED.value:
                raise HaConfigException(f"Cluster creation failed. Error: {cluster_output}")
            self.standby_node(node_name)
        except Exception as e:
            raise HaConfigException(f"Failed to create cluster. Error: {e}")

    def _add_node(self, node_name: str, cluster_user: str, cluster_secret: str) -> None:
        """
        Add Node

        Args:
            node_name (str): Node name
            cluster_user (str): HA user
            cluster_secret (str): Ha user password
        """
        try:
            if self._confstore.key_exists(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}"):
                Log.info(f"The node already {node_name} present in the cluster.")
                return
            add_node_cli = const.CORTX_CLUSTER_NODE_ADD.replace("<node>", node_name)\
                .replace("<user>", cluster_user).replace("<secret>", cluster_secret)
            self._execute.run_cmd(add_node_cli, check_error=False, secret=cluster_secret)
            self.standby_node(node_name)
            self._confstore.set(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}")
            Log.info(f"The node {node_name} added in the existing cluster.")
        except Exception as e:
            Log.error(f"Adding {node_name} failed; destroying the cluster. Error: {e}")
            output = self._execute.run_cmd(const.PCS_CLUSTER_NODE_REMOVE.replace("<node>", node_name), check_error=False)
            Log.error(f"Node Removed. Output: {output}")
            # Delete the node from nodelist if it was added in the store
            if self._confstore.key_exists(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}"):
                self._confstore.delete(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}")
            raise HaConfigException(f"Adding {node_name} failed")

    def _add_node_remotely(self, node_name: str, cluster_user: str, cluster_secret: str):
        try:
            if self._confstore.key_exists(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}"):
                Log.info(f"The node already {node_name} present in the cluster.")
                return
            Log.info(f"The cluster exists already, adding new node: {node_name}")
            nodelist: list = self.get_nodelist(fetch_from=ConfigCmd.HA_CONFSTORE)

            for remote_node in nodelist:
                try:
                    Log.info(f"Adding {node_name} using remote node: {remote_node}")
                    remote_executor = SSHRemoteExecutor(remote_node)
                    remote_executor.execute(const.CORTX_CLUSTER_NODE_ADD.replace("<node>", node_name)
                        .replace("<user>", cluster_user).replace("<secret>", "'" + cluster_secret + "'"),
                        secret=cluster_secret)
                    self.standby_node(node_name)
                    self._confstore.set(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}")
                    Log.info(f"Added new node: {node_name} using {remote_node}")
                    break
                except Exception as e:
                    Log.error(f"Adding {node_name} using remote node {remote_node} failed with error: {e}, \
                            if available, will try with other node")
                    # Try removing the node, it might be partially added.
                    try:
                        # TODO: Change following PCS command to CLI when available.
                        remote_executor.execute(const.PCS_CLUSTER_NODE_REMOVE.replace("<node>", node_name))
                    except Exception as e:
                        Log.error(f"Node remove failed with Error: {e}")
                    # Delete the node from nodelist if it was added in the store
                    if self._confstore.key_exists(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}"):
                        self._confstore.delete(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}")
        except Exception as e:
            raise HaConfigException(f"Failed to add node {node_name} remotely. Error: {e}")

    def _get_mgmt_vip(self, machine_id: str, cluster_id: str) -> dict:
        """
        Get Mgmt info.

        Args:
            machine_id (str): Get machine ID.
            cluster_id (str): Get Cluster ID.

        Raises:
            HaConfigException: Raise exception.

        Returns:
            dict: Mgmt info.
        """
        mgmt_info: dict = {}
        try:
            node_count: int = len(Conf.get(self._index, "server_node"))
            if ConfigCmd.DEV_CHECK == True or node_count < 2:
                return mgmt_info
            mgmt_info["mgmt_vip"] = Conf.get(self._index, f"cluster.{cluster_id}.network.management.virtual_host")
            netmask = Conf.get(self._index, f"server_node.{machine_id}.network.management.netmask")
            if netmask is None:
                raise HaConfigException("Detected invalid netmask, It should not be empty.")
            mgmt_info["mgmt_netmask"] = sum(bin(int(x)).count('1') for x in netmask.split('.'))
            mgmt_info["mgmt_iface"] = Conf.get(self._index, f"server_node.{machine_id}.network.management.interfaces")[0]
            Log.info(f"Mgmt vip configuration: {str(mgmt_info)}")
            return mgmt_info
        except Exception as e:
            Log.error(f"Failed to get mgmt ip address. Error: {e}")
            raise HaConfigException(f"Failed to get mgmt ip address. Error: {e}.")

    def _update_env(self, node_name: str, node_type: str, cluster_type: str, s3_instances: int) -> None:
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
        Conf.set(const.HA_GLOBAL_INDEX, "SERVICE_INSTANCE_COUNTER[1].instances", s3_instances)
        Log.info("CONFIG: Update ha configuration files")
        Conf.save(const.HA_GLOBAL_INDEX)

    def _fetch_fids(self) -> None:
        """
        Fetch fids from hare and store in a config file
        """
        try:
            Log.info("Fetch fids from hare and store in a conf file")
            fids_output, err, rc = self._execute.run_cmd(const.HCTL_FETCH_FIDS, check_error=True)
            Log.info(f"Fetched fids: {fids_output}, Error: {err}, RC: {rc}")
            with open(const.FIDS_CONFIG_FILE, 'w') as fi:
                json.dump(json.loads(fids_output), fi, indent=4)
        except Exception as e:
            Log.error(f"Failed fetching fids from hare. Error: {e}")
            raise HaConfigException("Failed fetching fids from hare.")

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
        path_to_comp_config = const.SOURCE_CONFIG_PATH

        install_type = self.get_installation_type()
        nodes = self.get_nodelist(fetch_from=Cmd.HA_CONFSTORE)
        path_to_comp_config = path_to_comp_config + '/components/' + install_type

        rc = TestExecutor.validate_cluster(node_list=nodes, comp_files_dir=path_to_comp_config)
        Log.info(f"cluster validation rc = {rc}")

        if not rc:
            raise HaConfigException("Cluster is no healthy. Check HA logs for further information.")

class UpgradeCmd(Cmd):
    """
    Upgrade Cmd
    """
    name = "upgrade"

    def __init__(self, args=None):
        """
        Init method.
        """
        super().__init__(args)
        machine_id = self.get_machine_id()
        self.s3_instance = UpgradeCmd.get_s3_instance(machine_id)

    def process(self):
        """
        Process upgrade command.
        """
        perform_post_upgrade(self.s3_instance)

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
        # TODO: cluster_manager fails if cleanup run multiple time EOS-20947
        self._cluster_manager = CortxClusterManager(default_log_enable=False)

    def process(self):
        """
        Process cleanup command.
        """
        Log.info("Processing cleanup command")
        try:
            nodes = self._confstore.get(const.CLUSTER_CONFSTORE_NODES_KEY)
            node_count: int = 0 if nodes is None else len(nodes)
            node_name = self.get_node_name()
            # Standby
            # TODO: handle multiple case for standby EOS-20855
            standby_output: str = self._cluster_manager.node_controller.standby(node_name)
            if json.loads(standby_output).get("status") == STATUSES.FAILED.value:
                Log.warn(f"Standby for {node_name} failed with output: {standby_output}."
                        "Cluster will be destroyed forcefully")
            if CleanupCmd.LOCAL_CHECK and node_count > 1:
                # TODO: Update cluster kill for --local option also
                # Remove SSH
                self._remove_node(node_name)
            else:
                # Destroy
                self._destroy_cluster(node_name)

            if self._confstore.key_exists(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}"):
                self._confstore.delete(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}")
            # Delete the config file
            self.remove_config_files()
        except Exception as e:
            Log.error(f"Cluster cleanup command failed. Error: {e}")
            raise HaCleanupException("Cluster cleanup failed")
        Log.info("cleanup command is successful")

    def _remove_node(self, node_name: str):
        """
        Remove node remotely.

        Args:
            node_name (str): Node Name.
        """
        nodelist: list = self.get_nodelist(fetch_from=CleanupCmd.HA_CONFSTORE)
        for remote_node in nodelist:
            if remote_node == node_name:
                continue
            Log.error(f"Removing {node_name} using remote node {remote_node}")
            # Try removing the node, it might be partially added.
            try:
                # TODO: Change following PCS command to CLI when available.
                remote_executor = SSHRemoteExecutor(node_name)
                remote_executor.execute(const.PCS_CLUSTER_NODE_REMOVE.replace("<node>", node_name))
                break
            except Exception as e:
                Log.error(f"Node remove failed with Error: {e}, Trying with other node.")

    def _destroy_cluster(self, node_name: str):
        """
        Destroy Cluster on current node.

        Args:
            node_name (str): Node name
        """
        Log.info(f"Destroying the cluster on {node_name}.")
        output = self._execute.run_cmd(const.PCS_CLUSTER_KILL)
        output = self._execute.run_cmd(const.PCS_CLUSTER_DESTROY)
        Log.info(f"Cluster destroyed. Output: {output}")

    def remove_config_files(self):
        """
        Remove file created by ha.
        """
        CleanupCmd.remove_file(const.CONFIG_DIR)

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

def main(argv: list):
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

        sys.stdout.write(f"Mini Provisioning {sys.argv[1]} configured successfully.\n")
    except Exception as err:
        Log.error("%s\n" % traceback.format_exc())
        sys.stderr.write(f"Setup command:{argv[1]} failed for cortx-ha. Error: {err}\n")
        return errno.EINVAL

if __name__ == '__main__':
    sys.exit(main(sys.argv))
