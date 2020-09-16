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
**************************************************************************
 Description:       Service Base Framework
****************************************************************************
"""


'''Module which provides service class'''


from abc import ABC
import abc

from ha.utility.error import HAUnimplemented


class Service(ABC):
    '''Abstract base class which provides service related
       operations'''

    SERVICE_TYPE = None

    def __init__(self):
        '''Init method'''
        pass

    @abc.abstractmethod
    def start(self, *args, **kwargs):
        '''Generic method to start the service'''
        raise HAUnimplemented()

    @abc.abstractmethod
    def stop(self, *args, **kwargs):
        '''Generic method to stop the service'''
        raise HAUnimplemented()

    @abc.abstractmethod
    def status(self, service_name, node_id, service_type):
        '''Generic method to get the status of the service'''
        raise HAUnimplemented()


class ClusteredService(Service):
    '''Base class for all clustered service
       implementation'''

    SERVICE_TYPE = 'clustered'


class NodeService(Service):
    ''''Abstract Base class for all node service
        implementation'''

    SERVICE_TYPE = 'node'

