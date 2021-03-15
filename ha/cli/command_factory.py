#!/usr/bin/env python3

# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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

import inspect

from ha.cli import commands
from ha.core.config.config_manager import ConfigManager

class CmdFactory:
    def __init__(self):
        """
        init of command factory
        """
        # Initialize logging.
        # Prefix of the log file name "cortxcli" is passed to the init function;
        # So the generated log file will be cortxcli.log
        ConfigManager.init("cortxcli")

        # This dictionary contains the classes used by all HA CLIs
        # In case of any modifications to the CLI,
        # this dictionary should be updated.
        self.cmd_dict = {
            "cluster": {
                "start": "ha.cli.exec.clusterExecutor.ClusterStartExecutor",
                "stop": "ha.cli.exec.clusterExecutor.ClusterStopExecutor",
                "restart": "ha.cli.exec.clusterExecutor.ClusterRestartExecutor",
                "standby": "ha.cli.exec.clusterExecutor.ClusterStandbyExecutor",
                "active": "ha.cli.exec.clusterExecutor.ClusterActiveExecutor",
                "list": "ha.cli.exec.clusterExecutor.ClusterListExecutor",
                "status": "ha.cli.exec.clusterExecutor.ClusterStatusExecutor",
                "add": "ha.cli.exec.clusterExecutor.ClusterAddExecutor",
                "-h": "ha.cli.exec.commandExecutor.ClusterCLIUsage",
                "--help": "ha.cli.exec.commandExecutor.ClusterCLIUsage"
            },
            "node": {
                "start": "ha.cli.exec.nodeExecutor.NodeStartExecutor",
                "stop": "ha.cli.exec.nodeExecutor.NodeStopExecutor",
                "standby": "ha.cli.exec.nodeExecutor.NodeStandbyExecutor",
                "active": "ha.cli.exec.nodeExecutor.NodeActiveExecutor",
                "status": "ha.cli.exec.nodeExecutor.NodeStatusExecutor",
                "-h": "ha.cli.exec.commandExecutor.NodeCLIUsage",
                "--help": "ha.cli.exec.commandExecutor.NodeCLIUsage"
            },
            "storageset": {
                "start": "ha.cli.exec.storagesetExecutor.StoragesetStartExecutor",
                "stop": "ha.cli.exec.storagesetExecutor.StoragesetStopExecutor",
                "standby": "ha.cli.exec.storagesetExecutor.StoragesetStandbyExecutor",
                "active": "ha.cli.exec.storagesetExecutor.StoragesetActiveExecutor",
                "status": "ha.cli.exec.storagesetExecutor.StoragesetStatusExecutor",
                "-h": "ha.cli.exec.commandExecutor.StoragesetCLIUsage",
                "--help": "ha.cli.exec.commandExecutor.StoragesetCLIUsage"
            },
            "service": {
                "start": "ha.cli.exec.serviceExecutor.ServiceStartExecutor",
                "stop": "ha.cli.exec.serviceExecutor.ServiceStopExecutor",
                "status": "ha.cli.exec.serviceExecutor.ServiceStatusExecutor",
                "-h": "ha.cli.exec.commandExecutor.ServiceCLIUsage",
                "--help": "ha.cli.exec.commandExecutor.ServiceCLIUsage"
            },
            "-h": "ha.cli.exec.commandExecutor.CLIUsage",
            "--help": "ha.cli.exec.commandExecutor.CLIUsage"
        }

    def get_executor(self, module_name, operation_name):
        """ return the appropriate class name from the dictionary"""

        try:
            executor = self.cmd_dict.get(module_name).get(operation_name)
        except Exception:
            return None
        return executor
