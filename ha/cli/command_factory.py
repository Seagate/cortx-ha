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
#from cortx.utils.log import Log
from ha.cli.exec.nodeExecutor import *
from ha.cli.exec.clusterExecutor import *
from ha.cli.exec.commandExecutor import *
from ha.cli.exec.serviceExecutor import *
from ha.cli.exec.storagesetExecutor import *

class cmdFactory:
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
                "start": ClusterStartExecutor,
                "stop": ClusterStopExecutor,
                "restart": ClusterRestartExecutor,
                "standby": ClusterStandbyExecutor,
                "active": ClusterActiveExecutor,
                "list": ClusterListExecutor,
                "status": ClusterStatusExecutor,
                "add": ClusterAddExecutor,
                "-h": ClusterCLIUsage,
                "--help": ClusterCLIUsage
            },
            "node": {
                "start": NodeStartExecutor,
                "stop": NodeStopExecutor,
                "standby": NodeStandbyExecutor,
                "active": NodeActiveExecutor,
                "status": NodeStatusExecutor,
                "-h": NodeCLIUsage,
                "--help": NodeCLIUsage
            },
            "storageset": {
                "start": StoragesetStartExecutor,
                "stop": StoragesetStopExecutor,
                "standby": StoragesetStandbyExecutor,
                "active": StoragesetActiveExecutor,
                "status": StoragesetStatusExecutor,
                "-h": StoragesetCLIUsage,
                "--help": StoragesetCLIUsage
            },
            "service": {
                "start": ServiceStartExecutor,
                "stop": ServiceStopExecutor,
                "status": ServiceStatusExecutor,
                "-h": ServiceCLIUsage,
                "--help": ServiceCLIUsage
            },
            "-h": CLIUsage,
            "--help": CLIUsage
        }

    def get_executor(self, module_name, operation_name):
        """ return the appropriate class name from the dictionary"""

        try:
            executor = self.cmd_dict.get(module_name).get(operation_name)
        except Exception:
            return None
        return executor
