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

"""
 ****************************************************************************
 Description:       Service Manager
 ****************************************************************************
"""
from service import ServiceRegistry
from ha.utility.error import HAUnimplemented, HACommandTerminated

from eos.utils.log import Log
from ha import const


class ServiceManager:
    def __init__(self):
        """
        init service manager
        """
        ServiceRegistryList = ServiceRegistry()
        ServiceRegistryList.register_services()

    def process_request(self, action, args):
        """
        Process requested service
        """
        if action == const.SERVICE_COMMAND:
            if args.command =="start":
                self.start(args.node, args.service)
            elif args.command == "stop":
                self.stop(args.node, args.service)
            elif args.command == "monitor":
                self.monitor(args.node, args.service)
            else:
                raise HAUnimplemented()

        elif action == const.CLEANUP_COMMAND:
            pass

        else:
            raise HAUnimplemented()

    def start(self, node_id, service_name):
        """
        Starts specific service on the requested node
        """
        pass

    def stop(self, node_id, service_name):
        """
        Stops specific service on the requested node
        """
        pass

    def monitor(self, node_id, service_name):
        """
        Monitors specific service on the requested node
        """
        pass
    