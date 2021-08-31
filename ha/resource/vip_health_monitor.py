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

import sys
import traceback
from cortx.utils.log import Log

from ha.core.config.config_manager import ConfigManager
from ha.resource.resource_agent import CortxServiceRA
from ha.execute import SimpleCommand
from ha import const

class VipHealthMonitor(CortxServiceRA):
    """
    Check VIP health check up and failover if unhealthy.
    """
    def __init__(self):
        """
        Initialize the class.
        """
        super(VipHealthMonitor, self).__init__()
        self._execute = SimpleCommand()

    @staticmethod
    def metadata() -> int:
        """
        Provide meta data for resource agent and parameter
        """
        env: str =r"""<?xml version="1.0"?>
        <!DOCTYPE resource-agent SYSTEM "ra-api-1.dtd">
        <resource-agent name="vip_health_check">
        <version>1.0</version>

        <longdesc lang="en">
            Check health of vip.
        </longdesc>
        <shortdesc lang="en">Health Check</shortdesc>
        <parameters>
        <parameter name="vip" required="1">
        <longdesc lang="en"> VIP that need monitor </longdesc>
        <shortdesc lang="en"> VIP </shortdesc>
        <content type="string"/>
        </parameter>
        <parameter name="nic" required="1">
        <longdesc lang="en"> NIC interface </longdesc>
        <shortdesc lang="en"> NIC interface </shortdesc>
        <content type="string"/>
        </parameter>
        </parameters>
        <actions>
        <action name="start"        timeout="3s" />
        <action name="stop"         timeout="3s" />
        <action name="monitor"      timeout="3s" interval="60s" depth="0" />
        <action name="meta-data"    timeout="4s" />
        </actions>
        </resource-agent>
        """
        sys.stdout.write(env)
        return const.OCF_SUCCESS

    def start(self) -> int:
        """
        Start monitoring.
        """
        rc: int = self.monitor()
        Log.info(f"start action on vip monitoring with rc: {rc}")
        return rc

    def stop(self) -> int:
        """
        Stop Vip.
        """
        return const.OCF_SUCCESS

    def monitor(self) -> int:
        """
        Monitor vip
        """
        res_param = self.get_env()
        vip: str = res_param["OCF_RESKEY_vip"]
        nic: str = res_param["OCF_RESKEY_nic"]
        output, error, rc = self._execute.run_cmd(f"ip a s {nic}")
        if rc != 0:
            Log.error(f"Failed to get ip address for {nic} with error {error}")
            return const.OCF_ERR_GENERIC
        status_str = output.split("\n")[0].split(" ")
        status = status_str[status_str.index("state") + 1]
        if status != "UP":
            Log.error(f"VIP Health failed, {nic} is down")
            return const.OCF_ERR_GENERIC
        ip_list = []
        for line in output.split("\n"):
            if len(line.split()) > 0 and "inet" in line.split()[0] and vip not in line.split():
                ip = line.split()[1].split("/")[0]
                ip_list.append(str(ip))
        if len(ip_list) < 1:
            Log.error(f"VIP Health failed, {nic} is down")
            return const.OCF_ERR_GENERIC
        return const.OCF_SUCCESS

def main(action: str ='') -> int:
    """
    Main function acts as switch case for IPHealthChecker resource agent.

    Args:
        action (str): Resource agent action called by Pacemaker. Defaults to ''.

    Returns:
        int: Provide output as int code provided by pacemaker.
    """
    try:
        if action == "meta-data":
            return VipHealthMonitor.metadata()
        ConfigManager.init("resource_agent")
        resource_agent = VipHealthMonitor()
        Log.debug(f"{resource_agent} initialized for action {action}")
        if action == "monitor":
            return resource_agent.monitor()
        elif action == "start":
            return resource_agent.start()
        elif action == "stop":
            return resource_agent.stop()
        else:
            print(f"Usage {sys.argv[0]} [monitor] [start] [stop] [meta-data]")
            exit(0)
    except Exception as e:
        Log.error(f"vip health check failed to perform {action}. Error: {traceback.format_exc()} {e}")
        return const.OCF_ERR_GENERIC

if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit(main(action))
