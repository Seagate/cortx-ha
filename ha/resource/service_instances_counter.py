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

"""
 **************************************************************************************
 Description:       Generic resource agent for counting running instances of resources.
 **************************************************************************************
"""

import sys
import re
from cortx.utils.log import Log
from cortx.utils.conf_store import Conf

from ha.core.config.config_manager import ConfigManager
from ha.resource.resource_agent import CortxServiceRA
from ha.execute import SimpleCommand
from ha import const


class AttribScope:
    CLUSTER = "cluster"
    NODE = "node"


class AttribUpdater:
    @staticmethod
    def _get_count_from_output(output: str, node_name: str) -> int:
        """
        Parses output of attrd_updater query command -
            name="motr-confd-1" host="srvnode-1" value="1"
            name="motr-confd-1" host="srvnode-2" value=""
            name="motr-confd-1" host="srvnode-3" value="1"
        if node_name is none, then instances are counted cluster wide,
        otherwise it's counted for just that node.
        """
        count = -1
        if output is None:
            return count

        count = 0
        lines = output.split('\n')
        if len(lines) > 0:
            for a_line in lines:
                info = re.split(r'\s+', a_line)
                if len(info) >= 3:
                    node_found = True
                    if node_name is not None and info[1].split('=')[1].strip('""') != node_name:
                        node_found = False
                    if node_found and info[2].split('=')[1].strip('""') == "1":
                        count += 1
        return count

    @staticmethod
    def get_count(resource: str, instances_per_node: int, node_name: str = None):
        count = 0
        try:
            executor = SimpleCommand()
            for instance in range(1, instances_per_node+1):
                service = resource + "-" + str(instance)
                out, _, _ = executor.run_cmd(f"attrd_updater -Q -A -n {service}", check_error=False)
                count += AttribUpdater._get_count_from_output(out, node_name)
        except Exception as e:
            Log.error(f"Problem in fetching attr. resource: {resource}. Error: {e}")
            count = -1

        return count

    @staticmethod
    def update_attr(scope: str, resource: str, instances_per_node: int, node_name:str = None):
        if scope == AttribScope.CLUSTER:
            node_name = None

        try:
            count: int = AttribUpdater.get_count(resource, instances_per_node, node_name)
            if count >= 0:
                attrib_name: str = resource + "-count"
                executor = SimpleCommand()
                executor.run_cmd(f"attrd_updater -U {count} -n {attrib_name}", check_error=False)
        except Exception as e:
            Log.error(f"Problem in updating attr - count of resource: {resource}. Error: {e}")


class ServiceInstancesCounter(CortxServiceRA):
    """
        Updates count of instances of a resource running on
        a node which can be used by other resources in
        constraint rules.
        The name of attribute would be service_count.
        Expects input in list of following information -
        services : [
            { "resource": "motr-confd", #resource name without instance in it.
              "instances": "1", #instances per node.
              "scope": "cluster" #update the count of services in cluster or node.
            }
        ]
        Prerequisite: Corresponding RA or systemd must be updating the attribute
        with name as resource name.
    """
    def __init__(self):
        """
        Initialize the class.
        """
        super(ServiceInstancesCounter, self).__init__()
        self._local_node = None
        self._resources = Conf.get(const.HA_GLOBAL_INDEX, 'SERVICE_INSTANCE_COUNTER')
        Log.info(f"Resource configured: {self._resources}")

    def metadata(self) -> int:
        """
        Provide meta data for resource agent and parameter
        """
        env: str =r"""<?xml version="1.0"?>
        <!DOCTYPE resource-agent SYSTEM "ra-api-1.dtd">
        <resource-agent name="service_instances_counter">
        <version>1.0</version>

        <longdesc lang="en">
            Updates count of instances of a resource running on
            a node which can be used by other resources in
            constraint rules.
            The name of attribute would be service_count.
            Expects input in list of following information -
            services : [
                {   "name": "motr-confd", #resource name without instance in it.
                    "instances": "1", #instances per node.
                    "scope": "cluster" #update the count of services in cluster or node.
                }
            ]
            Prerequisite: Corresponding RA or systemd must be updating the attribute
            with name as resource name.
        </longdesc>
        <shortdesc lang="en">Service instance counter agent</shortdesc>
        <parameters>
        </parameters>
        <actions>
        <action name="start"        timeout="40s" />
        <action name="stop"         timeout="40s" />
        <action name="monitor"      timeout="40s" interval="60s" depth="0" />
        <action name="meta-data"    timeout="4s" />
        </actions>
        </resource-agent>
        """
        sys.stdout.write(env)
        return const.OCF_SUCCESS

    def start(self) -> int:
        """
        Updates the count. Same as monitor.
        """
        self.monitor()
        return const.OCF_SUCCESS

    def stop(self) -> int:
        """
        Updates the count. Same as monitor.
        """
        self.monitor()
        return const.OCF_SUCCESS

    def monitor(self) -> int:
        """
        Monitor - updates the count of every
        service present in ha.conf
        """
        if self._local_node is None:
            res_param = self.get_env()
            self._local_node = res_param["OCF_RESKEY_CRM_meta_on_node"]

        for a_resource in self._resources:
            AttribUpdater.update_attr(a_resource['scope'], a_resource['resource'], a_resource['instances'], self._local_node)
        return const.OCF_SUCCESS


def main(resource: ServiceInstancesCounter, action: str ='') -> int:
    """
    Main function acts as switch case for ServiceInstancesCounter resource agent.

    Args:
        resource (ServiceInstancesCounter): Resource agent
        action (str): Resource agent action called by Pacemaker. Defaults to ''.

    Returns:
        int: Provide output as int code provided by pacemaker.
    """
    try:
        if action == "meta-data":
            return resource.metadata()
        Log.debug(f"{resource} initialized for action {action}")
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
        Log.error(f"service_instances_counter failed to perform {action}. Error: {e}")
        return const.OCF_ERR_GENERIC


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    ConfigManager.init("resource_agent")
    resource_agent = ServiceInstancesCounter()
    sys.exit(main(resource_agent, action))
