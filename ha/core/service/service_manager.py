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

from eos.utils.log import Log

from ha.core.service.service_registry import ServiceRegistry
from ha.utility.error import HAUnimplemented, HACommandTerminated
from ha import const


class ServiceManager:
    """
    Service Manager
    """
    def __init__(self):
        """
        init service manager
        """
        pass

    def process_request(self, action, args):
        """
        Process requested service
        """
        pass

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

class CortxServiceManager(ServiceManager):
    """
    Cortx Service Manager
    """
    def __init__(self):
        """
        init service manager
        """
        self._service_registry = ServiceRegistry()
        self._service_registry.register_services()

    def process_request(self, action, args):
        """
        Process requested service
        """
        if action == const.SERVICE_COMMAND:
            service = self._service_registry.get_service(args.service)

            if args.command =="start":
                service.start(args.node)

            elif args.command == "stop":
                service.stop(args.node)

            elif args.command == "monitor":
                service.monitor(args.node)
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

class PcsServiceManager(ServiceManager):
    """
    Pcs Service Manager
    """
    def __init__(self):
        """
        init service manager
        """
        pass

    def process_request(self, action, args):
        """
        Process requested service
        """
        pass

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
