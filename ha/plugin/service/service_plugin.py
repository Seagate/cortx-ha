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
 Description:       Service Plugin Base Framework
****************************************************************************
"""


'''Module which provides template for a plugin'''


from abc import abc, ABC
import abc

from ha.utility.error import HAUnimplemented


class ServicePlugin(ABC):
    '''Abstract Base class for all service plugin
       implementation'''

    def __init__(self):
        '''Init method'''
        pass

    @abc.abstractmethod
    def start(self):
        ''''Abstract method to start the service'''
        raise HAUnimplemented()

    @abc.abstractmethod
    def stop(self):
        ''''Abstract method to stop the service'''
        raise HAUnimplemented()

    @abc.abstractmethod
    def status(self):
        ''''Abstract method to get the status of the service'''
        raise HAUnimplemented()


