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
import time
import uuid

from cortx.utils.conf_store import Conf
from cortx.utils.log import Log
from cortx.utils.validator.v_pkg import PkgV
from cortx.utils.security.cipher import Cipher
from ha.core.system_health.const import NODE_MAP_ATTRIBUTES
from ha.core.system_health.const import CONFSTORE_KEY_ATTRIBUTES

from ha.execute import SimpleCommand
from ha import const
from ha.const import STATUSES
from ha.setup.create_pacemaker_resources import create_all_resources, configure_stonith
from ha.setup.pcs_config.alert_config import AlertConfig
from ha.setup.post_disruptive_upgrade import perform_post_upgrade
from ha.setup.pre_disruptive_upgrade import (backup_configuration,
                                             delete_resources)
from ha.core.cluster.cluster_manager import CortxClusterManager
from ha.core.config.config_manager import ConfigManager
from ha.remote_execution.ssh_communicator import SSHRemoteExecutor
from ha.core.error import HaPrerequisiteException
from ha.core.error import HaConfigException
from ha.core.error import HaInitException
from ha.core.error import HaCleanupException
from ha.core.error import HaResetException
from ha.core.error import SetupError
from ha.setup.cluster_validator.cluster_test import TestExecutor
from ha.core.system_health.system_health import SystemHealth
from ha.core.system_health.const import CLUSTER_ELEMENTS, HEALTH_EVENTS, EVENT_SEVERITIES
from ha.core.system_health.model.health_event import HealthEvent
from ha.const import _DELIM
from ha.util.ipmi_fencing_agent import IpmiFencingAgent


class Cmd:
    """
    Setup Command. This class provides methods for parsing arguments.
    """
    _index = "conf"
    DEV_CHECK = False
    LOCAL_CHECK = False
    PRE_FACTORY_CHECK = False
    PROV_CONFSTORE = "provisioner"
    HA_CONFSTORE = "confstore"

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
            f"cmd   post_install, prepare, config, init, test, upgrade, reset, cleanup, backup, restore, pre_upgrade, post_upgrade\n"
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

    def get_machine_id(self):
        command = "cat /etc/machine-id"
        machine_id, err, rc = self._execute.run_cmd(command, check_error=True)
        Log.info(f"Read machine-id. Output: {machine_id}, Err: {err}, RC: {rc}")
        return machine_id.strip()

    def get_node_name(self):
        machine_id = self.get_machine_id()
        node_name = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}network{_DELIM}data{_DELIM}private_fqdn")
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
                nodelist.append(Conf.get(self._index, f"server_node{_DELIM}{machine}{_DELIM}network{_DELIM}data{_DELIM}private_fqdn"))
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
    def get_ios_instance(machine_id: str) -> int:
        """
        Return ios instance
        Raises:
            HaConfigException: Raise exception for invalid ios count.
        Returns:
            [int]: Return ios count.
        """
        ios_instances = None
        try:
            ios_instances = Conf.get(Cmd._index, f"server_node{_DELIM}{machine_id}{_DELIM}storage{_DELIM}cvg_count")
            if int(ios_instances) < 1:
                raise HaConfigException(f"Found {ios_instances} which is invalid ios instance count.")
            return int(ios_instances)
        except Exception as e:
            Log.error(f"Found {ios_instances} which is invalid ios instance count. Error: {e}")
            raise HaConfigException(f"Found {ios_instances} which is invalid ios instance count.")

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
            s3_instances = Conf.get(Cmd._index, f"server_node{_DELIM}{machine_id}{_DELIM}s3_instances")
            if int(s3_instances) < 1:
                raise HaConfigException(f"Found {s3_instances} which is invalid s3 instance count.")
            return int(s3_instances)
        except Exception as e:
            Log.error(f"Found {s3_instances} which is invalid s3 instance count. Error: {e}")
            raise HaConfigException(f"Found {s3_instances} which is invalid s3 instance count.")

    @staticmethod
    def get_stonith_config() -> dict:
        """
        Return stonith config

        Raises:
            HaConfigException: Raise exception for invalid stonith configuration

        Returns:
            [dict]: Return stonith configuraitons
            resource_id = "Id to create the stonith resource"
            ipaddr of IPMI device = "IP of IPMI device"
            login = "username"
            passwd = "passwd"
            pcmk_host_list = ["pcmk_host_list"]
            auth = "PASSWORD"
        """
        stonith_config = dict()
        try:
            nodes_schema = Conf.get(Cmd._index, "server_node")
            machine_ids: list = list(nodes_schema.keys())
            for machine in machine_ids:
                node_name = nodes_schema.get(machine).get('network').get('data').get('private_fqdn')
                node_type = nodes_schema.get(machine).get('type')
                ipmi_ipaddr = nodes_schema.get(machine).get('bmc').get('ip')
                ipmi_user = nodes_schema.get(machine).get('bmc').get('user')
                ipmi_password_encrypted = nodes_schema.get(machine).get('bmc').get('secret')
                key = Cipher.generate_key(machine, const.SERVER_NODE_KEY)
                ipmi_password = Cipher.decrypt(key, ipmi_password_encrypted.encode('ascii')).decode()

                # setup BMC Credentials for ipmi_fencing_agent
                ipmi_fencing_agent = IpmiFencingAgent()
                ipmi_fencing_agent.setup_ipmi_credentials(ipmi_ipaddr=ipmi_ipaddr, ipmi_user=ipmi_user, ipmi_password=ipmi_password, node_name=node_name)

                stonith_config[node_name] = {
                    "resource_id": f"stonith-{node_name}",
                    "pcmk_host_list": node_name,
                    "auth": const.STONITH_AUTH_TYPE,
                    "ipaddr": ipmi_ipaddr,
                    "login": ipmi_user,
                    "passwd": ipmi_password,
                    "node_type": node_type,
                }
            return stonith_config
        except Exception as e:
            Log.error(f"Not found stonith config, Error: {e}")
            raise HaConfigException(f"Not found stonith config, Error: {e}")


    def get_mgmt_vip(self, machine_id: str, cluster_id: str) -> dict:
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
            mgmt_info["mgmt_vip"] = Conf.get(self._index, f"cluster{_DELIM}{cluster_id}{_DELIM}network{_DELIM}management{_DELIM}virtual_host")
            netmask = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}network{_DELIM}management{_DELIM}netmask")
            if netmask is None:
                raise HaConfigException("Detected invalid netmask, It should not be empty.")
            mgmt_info["mgmt_netmask"] = sum(bin(int(x)).count('1') for x in netmask.split('.'))
            mgmt_info["mgmt_iface"] = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}network{_DELIM}management{_DELIM}interfaces")[0]
            Log.info(f"Mgmt vip configuration: {str(mgmt_info)}")
            return mgmt_info
        except Exception as e:
            Log.error(f"Failed to get mgmt ip address. Error: {e}")
            raise HaConfigException(f"Failed to get mgmt ip address. Error: {e}.")


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
            PostInstallCmd.copy_file(const.SOURCE_ALERT_EVENT_RULES_FILE, const.ALERT_EVENT_RULES_FILE)
            PostInstallCmd.copy_file(const.SOURCE_CLI_SCHEMA_FILE, const.CLI_SCHEMA_FILE)
            PostInstallCmd.copy_file(const.SOURCE_SERVICE_FILE, const.SYSTEM_SERVICE_FILE)
            PostInstallCmd.copy_file(const.SOURCE_HEALTH_HIERARCHY_FILE, const.HEALTH_HIERARCHY_FILE)
            PostInstallCmd.copy_file(const.SOURCE_IEM_SCHEMA_PATH, const.IEM_SCHEMA)
            PostInstallCmd.copy_file(const.SOURCE_LOGROTATE_CONF_FILE, const.LOGROTATE_CONF_DIR)
            PostInstallCmd.copy_file(const.SOURCE_ACTUATOR_SCHEMA, const.ACTUATOR_SCHEMA)
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
            self._execute.run_cmd(f"setfacl -R -m g:{const.USER_GROUP_HACLIENT}:rwx {const.RA_LOG_DIR}")
            self._execute.run_cmd(f"setfacl -R -m g:{const.USER_GROUP_ROOT}:rwx {const.RA_LOG_DIR}")
            self._execute.run_cmd(f"setfacl -R -m g:{const.USER_GROUP_HACLIENT}:r-x {const.CONFIG_DIR}")
            self._execute.run_cmd(f"setfacl -R -m g:{const.USER_GROUP_ROOT}:rwx {const.CONFIG_DIR}")
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
        self._alert_config = AlertConfig()

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
        cluster_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}cluster_id")
        cluster_name = Conf.get(self._index, f"cluster{_DELIM}{cluster_id}{_DELIM}name")
        cluster_user = Conf.get(self._index, f"cortx{_DELIM}software{_DELIM}{const.HA_CLUSTER_SOFTWARE}{_DELIM}user")
        node_type = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}type").strip()

        # Read cluster user password and decrypt the same
        cluster_secret = Conf.get(self._index, f"cortx{_DELIM}software{_DELIM}{const.HA_CLUSTER_SOFTWARE}{_DELIM}secret")
        key = Cipher.generate_key(cluster_id, const.HACLUSTER_KEY)
        cluster_secret = Cipher.decrypt(key, cluster_secret.encode('ascii')).decode()
        mgmt_info: dict = self.get_mgmt_vip(machine_id, cluster_id)
        s3_instances = ConfigCmd.get_s3_instance(machine_id)
        ios_instances = ConfigCmd.get_ios_instance(machine_id)

        self._update_env(node_name, node_type, const.HA_CLUSTER_SOFTWARE, s3_instances, ios_instances)
        self._fetch_fids()
        self._update_cluster_manager_config()

        # fetch all nodes stonith config
        all_nodes_stonith_config: dict = {}
        enable_stonith = False
        env_type = self.get_installation_type().lower()
        if env_type == const.INSTALLATION_TYPE.HW.value.lower():
            all_nodes_stonith_config = ConfigCmd.get_stonith_config()
            enable_stonith = True
        elif env_type == const.INSTALLATION_TYPE.VM.value.lower():
            Log.warn("Stonith configuration not available, detected VM env")
        else:
            raise HaConfigException(f"Invalid env detected, {env_type}")

        # Push node name mapping to store
        if not self._confstore.key_exists(f"{const.PVTFQDN_TO_NODEID_KEY}/{node_name}"):
            node_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}node_id")
            self._confstore.set(f"{const.PVTFQDN_TO_NODEID_KEY}/{node_name}", node_id)

        # Update node map
        self._update_node_map()
        self._add_node_health()

        # Update cluster and resources
        self._cluster_manager = CortxClusterManager(default_log_enable=False)
        Log.info("Checking if cluster exists already")
        cluster_exists = bool(json.loads(self._cluster_manager.cluster_controller.cluster_exists()).get("output"))
        Log.info(f"Cluster exists? {cluster_exists}")

        if not cluster_exists:
            node_count: int = len(self.get_nodelist(fetch_from=ConfigCmd.HA_CONFSTORE))
            if node_count == 0:
                Log.info(f"Creating cluster: {cluster_name} with node: {node_name}")
                # Create cluster
                try:
                    self._create_cluster(cluster_name, cluster_user, cluster_secret, node_name)
                    self._create_resource(s3_instances=s3_instances, mgmt_info=mgmt_info, node_count=len(nodelist),
                                          ios_instances=ios_instances, stonith_config=all_nodes_stonith_config.get(node_name))
                    # configure stonith for each node from that node only
                    self._configure_stonith(all_nodes_stonith_config, node_name, enable_stonith)
                    self._confstore.set(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}")
                except Exception as e:
                    Log.error(f"Cluster creation failed; destroying the cluster. Error: {e}")
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
                        self._configure_stonith(all_nodes_stonith_config, node, enable_stonith)
            else:
                # Add node with SSH
                self._add_node_remotely(node_name, cluster_user, cluster_secret)
                # configure stonith for each node from that node only
                self._configure_stonith(all_nodes_stonith_config, node_name, enable_stonith)
        else:
            # configure stonith for each node from that node only
            self._configure_stonith(all_nodes_stonith_config, node_name, enable_stonith)
            for node in nodelist:
                if node != node_name:
                    Log.info(f"Adding node {node} to Cluster {cluster_name}")
                    self._add_node(node, cluster_user, cluster_secret)
                    self._configure_stonith(all_nodes_stonith_config, node, enable_stonith)
        self._execute.run_cmd(const.PCS_CLEANUP)
        # Create Alert if not exists
        self._alert_config.create_alert()
        Log.info("config command is successful")

    def _configure_stonith(self, all_nodes_stonith_config: dict, node_name: str, enable_stonith : bool = False) -> None:
        """
        configure stonith
        Args:
            all_nodes_stonith_config: required config stonith for each node
            node_name: node name to get stonith config from all nodes stonith config
            enable_stonith: default value is False

        Returns:
            None

        """
        if enable_stonith:
            self._execute.run_cmd(const.PCS_CLEANUP)
            configure_stonith(push=True, stonith_config=all_nodes_stonith_config.get(node_name))

    def _create_resource(self, ios_instances, s3_instances, mgmt_info, node_count, stonith_config=None):
        Log.info("Creating pacemaker resources")
        try:
            # TODO: create resource if not already exists.
            create_all_resources(ios_instances=ios_instances, s3_instances=s3_instances, mgmt_info=mgmt_info, node_count=node_count, stonith_config=stonith_config)
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
            node_status =  self._cluster_manager.cluster_controller.wait_for_node_online(node_name)
            # Nodes are added to the cluster during cluster creation
            # Node is expected to be Online when it is added
            if node_status != True:
                raise HaConfigException(f"Node {node_name} did not come online; Add node failed")

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
                    node_status =  self._cluster_manager.cluster_controller.wait_for_node_online(node_name)
                    # Nodes are added to the cluster during cluster creation
                    # Node is expected to be Online when it is added
                    if node_status != True:
                        raise HaConfigException(f"Node {node_name} did not come online; Add node failed")

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

    def _update_env(self, node_name: str, node_type: str, cluster_type: str, s3_instances: int, ios_instances: int) -> None:
        """
        Update env like VM, HW
        """
        Log.info(f"Detected {node_type} env and cluster_type {cluster_type}.")
        if "VM" == node_type.upper():
            Conf.set(const.HA_GLOBAL_INDEX, f"CLUSTER_MANAGER{_DELIM}env", node_type.upper())
        else:
            # TODO: check if any env available other than vm, hw
            Conf.set(const.HA_GLOBAL_INDEX, f"CLUSTER_MANAGER{_DELIM}env", "HW")
        Conf.set(const.HA_GLOBAL_INDEX, f"CLUSTER_MANAGER{_DELIM}cluster_type", cluster_type)
        Conf.set(const.HA_GLOBAL_INDEX, f"CLUSTER_MANAGER{_DELIM}local_node", node_name)
        Conf.set(const.HA_GLOBAL_INDEX, f"SERVICE_INSTANCE_COUNTER[1]{_DELIM}instances", s3_instances)
        Conf.set(const.HA_GLOBAL_INDEX, f"SERVICE_INSTANCE_COUNTER[2]{_DELIM}instances", ios_instances)
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

    def _update_node_map(self) -> None:
        """
        Update node map
        """
        # TODO: update node map should failed if any key is missing
        machine_id = self.get_machine_id()
        node_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}node_id")
        cluster_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}{NODE_MAP_ATTRIBUTES.CLUSTER_ID.value}")
        site_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}{NODE_MAP_ATTRIBUTES.SITE_ID.value}")
        rack_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}{NODE_MAP_ATTRIBUTES.RACK_ID.value}")
        storageset_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}{CONFSTORE_KEY_ATTRIBUTES.STORAGE_SET_ID.value}")
        host_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}network{_DELIM}management{_DELIM}public_fqdn")
        node_map = {NODE_MAP_ATTRIBUTES.CLUSTER_ID.value: cluster_id, NODE_MAP_ATTRIBUTES.SITE_ID.value: site_id,
                    NODE_MAP_ATTRIBUTES.RACK_ID.value: rack_id, NODE_MAP_ATTRIBUTES.STORAGESET_ID.value: storageset_id,
                    NODE_MAP_ATTRIBUTES.HOST_ID.value: host_id}
        system_health = SystemHealth(self._confstore)
        key = system_health._prepare_key(const.COMPONENTS.NODE_MAP.value, node_id=node_id)
        # Check key is already exist if not, store the node map.
        node_map_val = self._confstore.get(key)
        if node_map_val is None:
            self._confstore.set(key, json.dumps(node_map))

    # TBD: Temporary code till EOS-17892 is implemented
    def _add_node_health(self) -> None:
        """
        Add node health
        """
        try:
            machine_id = self.get_machine_id()
            node_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}node_id")
            cluster_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}{NODE_MAP_ATTRIBUTES.CLUSTER_ID.value}")
            site_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}{NODE_MAP_ATTRIBUTES.SITE_ID.value}")
            rack_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}{NODE_MAP_ATTRIBUTES.RACK_ID.value}")
            storageset_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}{CONFSTORE_KEY_ATTRIBUTES.STORAGE_SET_ID.value}")
            host_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}network{_DELIM}management{_DELIM}public_fqdn")

            timestamp = str(int(time.time()))
            event_id = timestamp + str(uuid.uuid4().hex)
            initial_event = {
                const.EVENT_ATTRIBUTES.EVENT_ID : event_id,
                const.EVENT_ATTRIBUTES.EVENT_TYPE : HEALTH_EVENTS.INSERTION.value,
                const.EVENT_ATTRIBUTES.SEVERITY : EVENT_SEVERITIES.INFORMATIONAL.value,
                const.EVENT_ATTRIBUTES.SITE_ID : site_id,
                const.EVENT_ATTRIBUTES.RACK_ID : rack_id,
                const.EVENT_ATTRIBUTES.CLUSTER_ID : cluster_id,
                const.EVENT_ATTRIBUTES.STORAGESET_ID : storageset_id,
                const.EVENT_ATTRIBUTES.NODE_ID : node_id,
                const.EVENT_ATTRIBUTES.HOST_ID : host_id,
                const.EVENT_ATTRIBUTES.RESOURCE_TYPE : CLUSTER_ELEMENTS.NODE.value,
                const.EVENT_ATTRIBUTES.TIMESTAMP : timestamp,
                const.EVENT_ATTRIBUTES.RESOURCE_ID : node_id,
                const.EVENT_ATTRIBUTES.SPECIFIC_INFO : None
            }

            Log.debug(f"Adding initial health {initial_event} for node {node_id}")
            health_event = HealthEvent.dict_to_object(initial_event)
            system_health = SystemHealth(self._confstore)
            system_health.process_event(health_event)
        except Exception as e:
            Log.error(f"Failed adding node health. Error: {e}")
            raise HaConfigException("Failed adding node health.")

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
        path_to_comp_config = const.SOURCE_CONFIG_PATH

        install_type = self.get_installation_type()
        nodes = self.get_nodelist(fetch_from=Cmd.HA_CONFSTORE)
        path_to_comp_config = path_to_comp_config + '/components/' + install_type

        rc = TestExecutor.validate_cluster(node_list=nodes, comp_files_dir=path_to_comp_config)
        Log.info(f"cluster validation rc = {rc}")

        if not rc:
            raise HaConfigException("Cluster is no healthy. Check HA logs for further information.")
        Log.info("test command is successful")

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

    def process(self):
        """
        Process upgrade command.
        """

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
            services = ["pcsd", "corosync", "cortx_ha_log.conf", "pacemaker"]
            for service in services:
                self._execute.run_cmd(f"logrotate --force /etc/logrotate.d/{service}")

            older_logs = []
            log_dirs = [const.COROSYNC_LOG, const.RA_LOG_DIR, const.PCSD_DIR]
            for log_dir in log_dirs:
                log_list = [file for file in os.listdir(log_dir) if file.split(".")[-1] not in ["log", "xml"]]
                for log_file in log_list:
                    older_logs.append(os.path.join(log_dir, log_file))

            pacemaker_log_list = [file for file in os.listdir(const.LOG_DIR) if file
                                  .split(".")[-1] not in ["log"] and file.startswith("pacemaker")]
            for log_file in pacemaker_log_list:
                older_logs.append(os.path.join(const.LOG_DIR, log_file))

            self._remove_logs(older_logs)
        except Exception as e:
            Log.error(f"Cluster reset command failed. Error: {e}")
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
        # TODO: cluster_manager fails if cleanup run multiple time EOS-20947
        self._cluster_manager = CortxClusterManager(default_log_enable=False)
        self._post_install_cmd = PostInstallCmd(args=None)

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
            standby_output: str = self._cluster_manager.node_controller.standby(node_name)
            if json.loads(standby_output).get("status") == STATUSES.FAILED.value:
                Log.warn(f"Standby for {node_name} failed with output: {standby_output}."
                        "Cluster will be destroyed forcefully")
            if CleanupCmd.LOCAL_CHECK and node_count > 1:
                node_id = Conf.get(self._index, f"server_node{_DELIM}{self.get_machine_id()}{_DELIM}node_id")
                node_map_key = SystemHealth(self._confstore)._prepare_key(const.COMPONENTS.NODE_MAP.value, node_id=node_id)
                # TODO: Update cluster kill for --local option also
                self._remove_node(node_name)
                self._confstore.delete(node_map_key)
                self._confstore.delete(f"{const.CLUSTER_CONFSTORE_NODES_KEY}/{node_name}")
                self._confstore.delete(f"{const.PVTFQDN_TO_NODEID_KEY}/{node_name}")
            else:
                # Destroy
                self._cluster_manager.cluster_controller.destroy_cluster()
                self._confstore.delete(recurse=True)

            # Delete the config file
            self.remove_config_files()
            if CleanupCmd.PRE_FACTORY_CHECK is not True:
                Log.info("Post_install being called from cleanup command")
                self._post_install_cmd.process()

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

    def remove_config_files(self):
        """
        Remove file created by ha.
        """
        files = [const.CONFIG_DIR]
        for pcsd_file in os.listdir(const.AUTH_DIR):
            files.append(os.path.join(const.AUTH_DIR, pcsd_file))

        for file in files:
            CleanupCmd.remove_file(file)

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


class PreUpgradeCmd(Cmd):
    """
    Pre-Upgrade Cmd
    """
    name = "pre_upgrade"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)

    def process(self):
        """
        Process command.

        NOTE: Consul is not expected to be upgraded, so no need to backup
        consul config
        Configuration backup is performed for every node while pacemaker setup
        only on one node (cluster level).
        """
        try:
            if os.environ['PRVSNR_MINI_LEVEL'] == 'cluster':
                Log.info("Performing pre disruptive upgrade routines on cluster \
                         level")
                delete_resources()
            else:
                Log.info("Performing pre disruptive upgrade routines on node \
                         level")
                backup_configuration()
        except Exception as err:
            raise SetupError("Pre-upgrade routines failed") from err


class PostUpgradeCmd(Cmd):
    """
    Post-Upgrade Cmd
    """
    name = "post_upgrade"

    def __init__(self, args):
        """
        Init method.
        """
        super().__init__(args)
        machine_id = self.get_machine_id()
        self.s3_instance = UpgradeCmd.get_s3_instance(machine_id)

    def process(self):
        """
        Process command.
        """
        try:
            if os.environ['PRVSNR_MINI_LEVEL'] == 'cluster':
                machine_id = self.get_machine_id()
                cluster_id = Conf.get(self._index, f"server_node{_DELIM}{machine_id}{_DELIM}cluster_id")
                mgmt_info: dict = self.get_mgmt_vip(machine_id, cluster_id)
                ios_instances = self.get_ios_instance(machine_id)
                node_count: int = len(self.get_nodelist(fetch_from=UpgradeCmd.HA_CONFSTORE))

                Log.info(f"Performing post disruptive upgrade routines on cluster \
                        level. cluster_id: {cluster_id}, mgmt_info: {mgmt_info}, node_count: {node_count}")
                perform_post_upgrade(ios_instances=ios_instances, s3_instances=self.s3_instance, do_unstandby=False,
                                     mgmt_info=mgmt_info, node_count=node_count)
        except Exception as err:
            raise SetupError("Post-upgrade routines failed") from err


def main(argv: list):
    try:
        if sys.argv[1] == "post_install":
            Conf.init()
            Conf.load(const.HA_GLOBAL_INDEX, f"yaml://{const.SOURCE_CONFIG_FILE}")
            log_path = Conf.get(const.HA_GLOBAL_INDEX, f"LOG{_DELIM}path")
            log_level = Conf.get(const.HA_GLOBAL_INDEX, f"LOG{_DELIM}level")
            Log.init(service_name='ha_setup', log_path=log_path, level=log_level)
        elif sys.argv[1] == "cleanup":
            if not os.path.exists(const.HA_CONFIG_FILE):
                a_str = f'Cleanup can not be proceed as \
                           HA config file: {const.HA_CONFIG_FILE} \
                           is missing. Either cleanup is already done or there \
                           is some other problem'
                sys.stdout.write(a_str)
                return 0
            ConfigManager.init("ha_setup")
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
