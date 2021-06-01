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

'''
   Routine which helps for constructing and sending an IEC to syslog for major
   system level events
'''

import json

from cortx.utils.log import Log
from ha.const import IEM_SCHEMA
from ha.alert.const import ALERTS
from ha.execute import SimpleCommand


class IemGenerator:
    '''
    Module responsible for constrcting an IEC and sending it to syslog
    '''
    def __init__(self):
        """
        Init IEM generator
        """
        self._execute = SimpleCommand()
        with open(IEM_SCHEMA, 'r') as iem_schema_file:
            self.iem_alert_data = json.load(iem_schema_file)

    def generate_iem(self, node: str, module: str, event_type: str) -> None:
        '''
           Forms an IEC based on diffrent values such as module:<node/resource>
           and event_type<lost/member for a node scenario>
           IEC code:
           IEC:{severity}{source}{component}{module_id}{event_id}:{desciption}
           severity of the event.
           source (Hardware or Software) of the event
           component who is generating an IEM
           event_id: unique identification of the event (like node lost or node now became member)
           module: sub-component of the module who generated an IEM

           Required parameters
           node : Node name
           module : Module type (ex 'node' or 'resource' )
           event_type : Type of event based on module ( ex 'member' / 'lost' when module is 'node' )
        '''
        try:
            module_type = self.iem_alert_data.get(module)
            severity = module_type.get('severity').get(event_type)
            source = module_type.get('source')
            component = module_type.get('component')
            module_id = module_type.get('module')
            event_id = module_type.get('event').get(event_type).get('ID')
            desc = module_type.get('event').get(event_type).get('desc')
            desciption = desc.format(node)

            iec_string = f'"IEC:{severity}{source}{component}{module_id}{event_id}:{desciption}"'
            iec_command = ALERTS.logger_utility_iec_cmd + ' ' + iec_string
            Log.info(f'Sending an IEC: {iec_string} to syslog')

            _output, _err, _rc = self._execute.run_cmd(iec_command, check_error=False)
            if _rc != 0 or _err:
                raise Exception(f'Failed to populate an IEC to syslog: {_err}')
        except KeyError as kerr:
            Log.error(f'Key Error occured while parsing the IEM data while generating \
                        an IEC for {module} for the event {event_type}: {kerr}')
        except Exception as err:
            Log.error(f'Problem occured while generating an IEC for {module} \
                        for the event {event_type}: {err}')

ig = IemGenerator()
ig.generate_iem('ssc-vm', 'node', 'lost')
