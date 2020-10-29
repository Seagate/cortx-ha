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

from cortx.utils.log import Log

from ha import const
from ha.core.service.service_registry import ServiceRegistry
from ha.core.error import HAUnimplemented


class ServiceManager:
    """
    Service Manager
    """
    def __init__(self):
        """
        init service manager
        """
        pass

    def process_request(self, action, args, output):
        """
        Process requested service
        """
        raise HAUnimplemented()

    def start(self, node_id, service_name):
        """
        Starts specific service on the requested node
        """
        raise HAUnimplemented()

    def start_all(self, node_id):
        """
        Starts all the registered services on the requested node
        """
        raise HAUnimplemented()

    def stop(self, node_id, service_name):
        """
        Stops specific service on the requested node
        """
        raise HAUnimplemented()

    def stop_all(self, node_id):
        """
        Stops all the registered services on the requested node
        """
        raise HAUnimplemented()

    def status(self, node_id, service_name):
        """
        Returns status of the specific service on the requested node
        """
        raise HAUnimplemented()

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

    def process_request(self, action, args, output):
        """
        Process requested service
        """

        self._output = output
        _action_status = "Failure"
        _return_code = 1

        if action == const.SERVICE_COMMAND:
            if args.service_action == "start":
                _action_status, _return_code = self.start(args.node, args.service_name)

            elif args.service_action == "start all":
                _action_status, _return_code = self.start_all(args.node)

            elif args.service_action == "stop":
                _action_status, _return_code = self.stop(args.node, args.service_name)

            elif args.service_action == "stop all":
                _action_status, _return_code = self.stop_all(args.node)

            elif args.service_action == "status":
                _action_status, _return_code = self.status(args.node, args.service_name)

            else:
                raise HAUnimplemented()
        else:
            raise HAUnimplemented()

        self._output.output(_action_status)
        self._output.rc(_return_code)

    def start(self, node_id, service_name):
        """
        Starts specific service on the requested node
        """
        _action_status = "Failure"
        _return_code = 1
        service = self._service_registry.get_service(node_id, service_name)

        if service is not None:
            _action_status, _return_code = service.start()
        else:
            Log.error("service instance not found in the service registry")

        return _action_status, _return_code

    def start_all(self, node_id):
        """
        Starts all the registered services on the requested node
        """
        _action_status = "Failure"
        _return_code = 1
        service_list = self._service_registry.get_service_list(node_id)

        for service in service_list:
            _action_status, _return_code = service.start()
            if _return_code != 0:
                break

        return _action_status, _return_code

    def stop(self, node_id, service_name):
        """
        Stops specific service on the requested node
        """
        _action_status = "Failure"
        _return_code = 1
        service = self._service_registry.get_service(node_id, service_name)

        if service is not None:
            _action_status, _return_code = service.stop()
        else:
            Log.error("service instance not found in the service registry")

        return _action_status, _return_code

    def stop_all(self, node_id):
        """
        Stops all the registered services on the requested node
        """
        _action_status = "Failure"
        _return_code = 1
        service_list = self._service_registry.get_service_list(node_id)

        for service in service_list:
            _action_status, _return_code = service.stop()
            if _return_code != 0:
                break

        return _action_status, _return_code

    def status(self, node_id, service_name):
        """
        Returns status of the specific service on the requested node
        """
        _action_status = "Failure"
        _return_code = 1
        service = self._service_registry.get_service( node_id, service_name)

        if service is not None:
            _action_status, _return_code = service.status()

        return _action_status, _return_code

class PcsServiceManager(ServiceManager):
    """
    Pcs Service Manager
    """
    def __init__(self):
        """
        init service manager
        """
        pass

    def process_request(self, action, args, output):
        """
        Process requested service
        """
        pass

    def start(self, node_id, service_name):
        """
        Starts specific service on the requested node
        """
        pass

    def start_all(self, node_id):
        """
        Starts all the registered services on the requested node
        """
        pass

    def stop(self, node_id, service_name):
        """
        Stops specific service on the requested node
        """
        pass

    def stop_all(self, node_id):
        """
        Stops all the registered services on the requested node
        """
        pass

    def status(self, node_id, service_name):
        """
        Returns status of the specific service on the requested node
        """
        pass
