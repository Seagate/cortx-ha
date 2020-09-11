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
 Description:       Service base class
 ****************************************************************************
"""

class Service:
    def __init__(self):
        pass

    def register(self, service_name):
        pass

    def start(self, node_id) :
        pass

    def status(self, node_id):
        pass

    def stop(self, node_id):
        pass

    def deregister(self, service_name):
        pass




class ServiceRegistry:
    def __init__(self):
        """
        """
        self.services_list = {}

    def register_services(self):
        """
        Register all necessary service on the current node
        """
        pass

    def deregister_services(self):
        """
        Deregister all the necessary service on the current node
        """
        pass

    def get_service_list(self):
        """
        """
        return self.services_list