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

'''Derived module in the Monitoring hierarchy which monitors node alert'''

from cortx.utils.log import Log
from ha.const import IEC, RA_LOG_DIR, IEC_MAPPING_DICT
from ha.execute import SimpleCommand


class NodeAlertMonitor():
    '''
    Module responsible for analyzing an alert information
    to generate an IEM and sending the IEM across.
    '''
    #TODO: Inherit this class from base AlertMonitor

    def __init__(self):
        ''''Init method'''
        self._execute = SimpleCommand()

        # Name of the node event. e.g. shutdown or poweron
        # Can be known from base class. Values may change
        self._event = None
        self._event_type = 'failure'

        # No need to initialize this here. It will be available from
        # base class. For now, initializing it to None for testing purpose.
        self.alert_desc = None

    def create_iem(self):
        '''Creates the structure required to send the information as IEC'''
        # From the base implementation, self.alert_desc value will be available
        # From which, actual event can be found. like shutdown or poweron

        severity = IEC_MAPPING_DICT['severity'][self._event]
        if self._event == 'poweron':
            self._event_type = 'recover'
        event = IEC_MAPPING_DICT['event'][self._event_type]

        # self.alert_desc will be available from Base class which can be
        # directly used to append the description to IEC string or we can
        # parse out the info and append
        iec_string = f'"IEC:{severity}{IEC_MAPPING_DICT["source"]}{IEC_MAPPING_DICT["component"]}{IEC_MAPPING_DICT["module"]}{event}:{self.alert_desc}"'
        iec_command = IEC + ' ' + iec_string
        Log.info(f'Sending an IEC: {iec_string} to syslog')
        _output, _err, _rc = self._execute.run_cmd(iec_command, check_error=False)

        if _rc != 0 or _err:
            raise Exception(f'Failed to populate an IEC to syslog')


if __name__ == '__main__':
    Log.init(service_name="alert_monitor", log_path=RA_LOG_DIR, level="INFO")
