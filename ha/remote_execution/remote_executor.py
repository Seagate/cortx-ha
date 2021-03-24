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

"""Module for remote communication over SSH channel"""

import abc


class RemoteExecutor:
    '''An abstract Base class for all the remote node
       execution'''

    __metaclass__ = abc.ABCMeta

    def __init__(self, hostname, port):
        '''Init method'''
        self._hostname = hostname
        self._port = port

    @abc.abstractmethod
    def execute(self, command):
        '''Communicates to remote node by code execution'''
        raise NotImplementedError
