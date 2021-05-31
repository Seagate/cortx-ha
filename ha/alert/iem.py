#!/usr/bin/env python3

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

import json

from cortx.utils.log import Log
from ha.const import IEM_SCHAMA, ALERT_ATTRIBUTES, RA_LOG_DIR
from ha.execute import SimpleCommand

class IemGenerator:
    def __init__(self):
        """
        Init IEM generator
        """
        self._execute = SimpleCommand()
        with open(IEM_SCHAMA, 'r') as iem_schema_file:
            self.iem_alert_data = json.load(iem_schema_file)

    def generate_iem(self, module: str, node: str, event_type: str) -> None:
        '''
           Forms an IEC based on diffrent values such as module:<node/resource>
           and event_type<lost/member for a node scenario>

           Required parameters
           node : Node name
           module : Module type (ex 'node' or 'resource' )
           event_type : Type of event based on module ( ex 'member' / 'lost' when module is 'node' )
        '''
        severity = self.iem_alert_data.get(module).get('severity').get(event_type)
        source = self.iem_alert_data.get(module).get('source')
        component = self.iem_alert_data.get(module).get('component')
        module = self.iem_alert_data.get(module).get('module')
        event_id = self.iem_alert_data.get(module).get('event').get(event_type).get('ID')
        desc = self.iem_alert_data.get(module).get('event').get(event_type).get('desc')

        iec_string = f'"IEC:{severity}{source}{component}{module}{event_id}:{desc}"'
        iec_command = ALERT_ATTRIBUTES.logger_utility_iec_cmd + ' ' + iec_string
        Log.info(f'Sending an IEC: {iec_string} to syslog')
        _output, _err, _rc = self._execute.run_cmd(iec_command, check_error=False)

        if _rc != 0 or _err:
            raise Exception(f'Failed to populate an IEC to syslog: {_err}')

Log.init(service_name="alert_monitor", log_path=RA_LOG_DIR, level="INFO")
