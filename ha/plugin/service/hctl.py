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
 Description:       hctl Wrapper interface
****************************************************************************
"""


'''Wrapper module which provides hctl interface'''


from eos.utils.log import Log
from ha.utility.execute import Execute


class HctlWrapper(ServicePlugin):
    '''Wrapper class for hctl interface
       implementation'''

    HCTL_WRAPPER_INTERFACE = 'hctl '
    HCTL_WRAPPER_START = HCTL_WRAPPER_INTERFACE + 'start'
    HCTL_WRAPPER_STOP = HCTL_WRAPPER_INTERFACE + 'stop'
    HCTL_WRAPPER_STOP = HCTL_WRAPPER_INTERFACE + 'status'

    def __init__(self):
        ''''Init method'''
        try:
            self._execute = Execute()
        except Exception as e:
            raise(f'Error in instantiating Execute(): {e}')

    def start(self):
        '''starts the service using hctl'''
        _output, _err, _rc = self._execute.run_cmd(self.HCTL_WRAPPER_START)

    def stop(self):
        '''stops the service using hctl'''
        _output, _err, _rc = self._execute.run_cmd(self.HCTL_WRAPPER_STOP)

    def status(self):
        '''Returns the status of the service using
           hctl interface'''
        _output, _err, _rc = self._execute.run_cmd(self.HCTL_WRAPPER_STATUS)
        return _output
