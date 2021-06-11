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
 ****************************************************************************
 Description:       Generic resource agent used to map fid to cloneids.
 ****************************************************************************
"""

import os
import sys
import time

from cortx.utils.log import Log

from ha.core.config.config_manager import ConfigManager
from ha.resource.resource_agent import CortxServiceRA
from ha.execute import SimpleCommand
from ha.plugin.hare.hare import Hare
from ha import const

class FidManager:
    """
    Manage Fid for different services.
    """

    @staticmethod
    def get_fid(service: str, node_id: str, instance_id: int) -> str:
        """
        Get Fid from hare mapping file for given services.

        Args:
            service ([str]): Service name.
            node_id ([str]): Node name for fid instance.
            instance_id ([int]): Instance id for service.

        Returns:
            str: Return fid of given service.
        """
        try:
            return Hare.get_fid(service, node_id, instance_id)
        except Exception as e:
            Log.error(f"Failed to get fid for ({service}, {node_id}, \
                {instance_id}). Error: {e}")
            return None


class AttribUpdater:
    @staticmethod
    def set_attr(resource: str):
        try:
            executor = SimpleCommand()
            executor.run_cmd(f"attrd_updater -U 1 -n {resource}", check_error=False)
        except Exception as e:
            Log.error(f"Problem in updating attr - resource: {resource}. Error: {e}")

    @staticmethod
    def del_attr(resource: str):
        try:
            executor = SimpleCommand()
            executor.run_cmd(f"attrd_updater -D -n {resource}", check_error=False)
        except Exception as e:
            Log.error(f"Problem in deleting attr - resource: {resource}, Error: {e}")


class DynamicFidServiceRA(CortxServiceRA):
    """
    This class is used to provide wrapper around systemd resource agent.
    This class manage fid mapping to (serviceName, NodeId, InstanceId).
    Resource name: (Used to get instance)
        like motr-ios-1, s3server-1, ...
        Here, resource name is used to get instance.
    Service name: (Used for systemd service)
        like s3server, m0d, ...
    Fid service name: (Used for service name in mapping)
        like s3service, ios, confd
    """
    def __init__(self):
        """
        Initialize DynamicFidServiceRA class.
        """
        super(DynamicFidServiceRA, self).__init__()
        self._execute = SimpleCommand()
        self._status_list: list = ["failed", "active", "unknown"]

    def _get_update_attrib_info(self) -> None:
        res_param = self.get_env()
        self._resource = res_param["OCF_RESOURCE_INSTANCE"]
        self._update_attrib = res_param["OCF_RESKEY_update_attrib"]

    def _get_systemd_service(self) -> str:
        """
        Get Service name.

        Returns:
            str: Service name with fid mapping like service@fid
        """
        res_param = self.get_env()
        service: str = res_param["OCF_RESKEY_service"]
        fid_service_name: str = res_param["OCF_RESKEY_fid_service_name"]
        local_node: str = res_param["OCF_RESKEY_CRM_meta_on_node"]
        resource: str = res_param["OCF_RESOURCE_INSTANCE"]
        resource_instance: str = str(resource.split('-')[-1])
        if not resource_instance.isdigit():
            Log.error(f"Invalid resource name {resource}, missing fid")
            sys.exit(const.OCF_ERR_CONFIGURED)
        instance_id: int = int(resource_instance)
        fid = FidManager.get_fid(fid_service_name, local_node, instance_id)
        if fid is None:
            Log.error(f"Invalid config for fid for resource {resource}")
            sys.exit(const.OCF_ERR_CONFIGURED)
        return f"{service}@{fid}"

    def _get_service_status(self, service: str) -> str:
        """
        Monitor service and provide status.
        Command to monitor:
            $ systemctl is-active <service_name>
        Args:
            service (str): Service name

        Returns:
            str: Return service status.
                Service status are one of failed, active, unknown, activating
        """
        output, _, _ = self._execute.run_cmd(f"systemctl is-active {service}",
                                                check_error=False)
        return output

    def metadata(self) -> int:
        """
        Provide meta data for resource agent and parameter
        """
        env: str =r"""<?xml version="1.0"?>
        <!DOCTYPE resource-agent SYSTEM "ra-api-1.dtd">
        <resource-agent name="dynamic_fid_service_ra">
        <version>1.0</version>

        <longdesc lang="en">
        This is resource agent, wrapper around systemd service.
        It map clone to service instance on node.
        Note:
        Only valid resource name accepted with format 'resource_name'-'instance-id'.
        Here instance-id always start with 1 which going to map fid of services.
        Example: s3server-2
        </longdesc>
        <shortdesc lang="en">Systemd wrapper agent</shortdesc>
        <parameters>
        <parameter name="service" required="1">
        <longdesc lang="en"> Service name to manage systemd </longdesc>
        <shortdesc lang="en"> Systemd service </shortdesc>
        <content type="string"/>
        </parameter>
        <parameter name="fid_service_name" required="1">
        <longdesc lang="en"> Fid service name used in mapping </longdesc>
        <shortdesc lang="en"> Systemd service </shortdesc>
        <content type="string"/>
        </parameter>
        <parameter name="update_attrib" required="0">
        <longdesc lang="en"> If true, updates the node attribute for resource. </longdesc>
        <shortdesc lang="en"> Update attribute. </shortdesc>
        <content type="boolean" default="false"/>
        </parameter>
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
        Start service and provide output.

        Command to start service:
            $ systemctl reset-failed service
            $ systemctl start service

        Returns:
            int: Return as per service status.
                active: return const.OCF_SUCCESS.
                unknown: Wait till timeout.
                failed or timeout will cause failover or moved to Stopped state.
        """
        service = self._get_systemd_service()
        Log.debug(f"Start: Start {service} service")
        self._execute.run_cmd(f"systemctl reset-failed {service}", check_error=False)
        self._execute.run_cmd(f"systemctl start {service}", check_error=False)
        while True:
            Log.debug(f"Start: Starting {service} service")
            status: str = self._get_service_status(service).strip()
            if status == "active":
                break
            elif status == "failed":
                Log.info(f"Start: Failed to start {service} and may cause failover or Stop.")
                return const.OCF_ERR_GENERIC
            else:
                time.sleep(1)
                continue
        Log.info(f"Start: Started {service} service")
        self._get_update_attrib_info()
        if self._update_attrib:
            AttribUpdater.set_attr(self._resource)
        return const.OCF_SUCCESS

    def stop(self) -> int:
        """
        Stop service. If stop failed it will cause stonith.

        Returns:
            int: Return as per service status.
                if unknown or failed then return success.
                timeout of stop will cause stonith.
        """
        service = self._get_systemd_service()
        Log.debug(f"Stop: Stopping {service} service")
        self._execute.run_cmd(f"systemctl stop {service}", check_error=False)
        while True:
            status: str = self._get_service_status(service).strip()
            time.sleep(1)
            if status in ["failed", "unknown"]:
                break
        Log.info(f"Stop: Stopped {service} service")
        self._get_update_attrib_info()
        if self._update_attrib:
            AttribUpdater.del_attr(self._resource)
        return const.OCF_SUCCESS

    def monitor(self) -> int:
        """
        It monitor service with help of pacemaker and return result.

        Args:
            service_name (str): Systemd service name. Defaults to None.

        Returns:
            int: Return service status to pacemaker.
                const.OCF_NOT_RUNNING: Service not running.
                const.OCF_ERR_GENERIC: Service is failed.
                const.OCF_SUCCESS: Service is running.
                Monitor timeout will cause restart.
        """
        service: str = self._get_systemd_service()
        Log.debug(f"Monitor: Monitoring of service: {service}")
        while True:
            status: str = self._get_service_status(service).strip()
            if status == "active":
                break
            elif status == "failed":
                Log.debug(f"Monitor: failed to monitor {service}")
                self._get_update_attrib_info()
                if self._update_attrib:
                    AttribUpdater.del_attr(self._resource)
                return const.OCF_ERR_GENERIC
            elif status == "unknown":
                Log.debug(f"Monitor: Service {service} is not started yet...")
                self._get_update_attrib_info()
                if self._update_attrib:
                    AttribUpdater.del_attr(self._resource)
                return const.OCF_NOT_RUNNING
            else:
                # wait if there is unstable status like activating, deactivating
                time.sleep(1)
                continue
        return const.OCF_SUCCESS

def main(resource: DynamicFidServiceRA, action: str ='') -> int:
    """
    Main function acts as switch case for DynamicFidServiceRA resource agent.

    Args:
        resource (DynamicFidServiceRA): Resource agent
        action (str): Resource agent action called by Pacemaker. Defaults to ''.

    Returns:
        int: Provide output as int code provided by pacemaker.
    """
    try:
        if action == "meta-data":
            return resource.metadata()
        ConfigManager.init("resource_agent")
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
        Log.error(f"systemd_fid_wrapper_ra failed to perform {action}. Error: {e}")
        return const.OCF_ERR_GENERIC

if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    resource_agent = DynamicFidServiceRA()
    sys.exit(main(resource_agent, action))