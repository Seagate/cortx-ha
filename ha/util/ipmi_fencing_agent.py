#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
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

# Note: This class is used to bind different type of controller together.
# Other controller like node, cluster, storageset, service inheriting
# from this class.

import ast
import json
from ha.core.config.config_manager import ConfigManager
from ha.execute import SimpleCommand
from ha.util.fencing_agent import FencingAgent


class IpmiFencingAgent(FencingAgent):
    """ Tool to manage IPMI-enabled devices """

    NODE_BMC_INFO_KEY = "node_bmc_info"
    IPMI_IPADDR = "ipmi_ipaddr"
    IPMI_USER = "ipmi_user"
    IPMI_AUTH_KEY = "ipmi_auth_key"

    def __init__(self):
        """
        Initialize IPMI Fencing Agent class.
        """
        super(IpmiFencingAgent, self).__init__()
        self._confstore = ConfigManager.get_confstore()
        self._execute = SimpleCommand()

    def power_off(self, nodeid: str):
        """
        Power OFF node with nodeid

        Args:
            nodeid (str): private fqdn define in conf store.
        """
        try:
            bmc_info = self._confstore.get(f"{IpmiFencingAgent.NODE_BMC_INFO_KEY}/node/{nodeid}")
            if bmc_info is not None:
                _, value = bmc_info.popitem()
                bmc_info_dict = ast.literal_eval(value)
                self._execute.run_cmd(f"ipmitool -I lanplus -H {bmc_info_dict[IpmiFencingAgent.IPMI_IPADDR]} "
                                      f"-U {bmc_info_dict[IpmiFencingAgent.IPMI_USER]} "
                                      f"-P {bmc_info_dict[IpmiFencingAgent.IPMI_AUTH_KEY]} chassis power off")
        except Exception as e:
            raise Exception(f"Failed to run IPMItool Command. Error : {e}")

    def power_on(self, nodeid: str):
        """
        Power ON node with nodeid

        Args:
            nodeid (str): Node ID from cluster nodes.
        """
        pass

    def setup_ipmi_credentials(self, ipmi_ipaddr: str, ipmi_user: str, ipmi_password: str, node_name: str):
        """
        Get the BMC credentials & store it in confstore

        """
        bmc_info_keys = {IpmiFencingAgent.IPMI_IPADDR: ipmi_ipaddr, IpmiFencingAgent.IPMI_USER: ipmi_user,
                            IpmiFencingAgent.IPMI_AUTH_KEY: ipmi_password}
        if not self._confstore.key_exists(f"{IpmiFencingAgent.NODE_BMC_INFO_KEY}/node/{node_name}"):
            self._confstore.set(f"{IpmiFencingAgent.NODE_BMC_INFO_KEY}/node/{node_name}", json.dumps(bmc_info_keys))

