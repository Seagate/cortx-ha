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
 Description:       Hare Service Opeartions
****************************************************************************
"""

'''Module which provides Hare service class'''


from eos.utils.log import Log


class HareService(Service):
    '''
       All Hare service oprations implementation which uses
       Hctl wrapper
    '''

    def __init__(self):
        '''Init method'''
        try:
            # Uses plugin to perform service wrapper
            self._service_plugin = HctlWrapper()
        except Exception as e:
            Log.error(f'Failed to instantiate the HctlWrapper: {e}')

    def start(self, *args, **kwargs):
        '''Method to start the Hare service'''

        Log.debug('Starting the Hare service')
        self._service_plugin.start()

    def stop(self, *args, **kwargs):
        '''Method to stop the Hare service'''

        Log.debug('Stopping the Hare service')
        self._service_plugin.stop()

    def status(self, *args, **kwargs):
        '''Method to get the Hare service status'''

        Log.debug('Getting the status of the Hare service')
        self._service_plugin.status()
