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
import re

from cortx.utils.log import Log
from ha.const import IEM_SCHEMA
from ha.alert.const import ALERTS
from ha.core.system_health.const import NODE_MAP_ATTRIBUTES
from cortx.utils.iem_framework import EventMessage
from cortx.utils.iem_framework.error import EventMessageError
from ha.core.system_health.get_system_attributes import NodeParams
from ha.const import PVTFQDN_TO_NODEID_KEY
from ha.core.config.config_manager import ConfigManager

class IemGenerator:
    '''
    Module responsible for constrcting an IEC and sending it to syslog
    '''
    def __init__(self):
        """
        Init IEM generator
        """
        with open(IEM_SCHEMA, 'r') as iem_schema_file:
            self.iem_alert_data = json.load(iem_schema_file)

    def _get_node_id(self, node: str) -> str:
        '''
        Temporary routine to get node id
        '''

        conf_store = ConfigManager.get_confstore()
        key_val  = conf_store.get(f"{PVTFQDN_TO_NODEID_KEY}/{node}")
        _, node_id = key_val.popitem()
        return node_id

    def generate_iem(self, node: str, module: str, event_type: str) -> None:
        '''
           Creates an IEM based on diffrent values such as module:<node/resource>
           and event_type<lost/member for a node scenario>

           severity : severity of the event.
           source : source (Hardware or Software) of the event
           component : component who is generating an IEM
           event_id: unique identification of the event (like node lost or node now became member)
           module: sub-component of the module who generated an IEM

           Required parameters
           node : Node name
           module : Module type (ex 'node' or 'resource' )
           event_type : Type of event based on module ( ex 'member' / 'lost' when module is 'node' )
        '''
        module_type = self.iem_alert_data.get(module)
        severity = module_type.get('severity').get(event_type)
        source = module_type.get('source')
        component = module_type.get('component')
        module = module_type.get('module')
        event_id = module_type.get('event').get(event_type).get('ID')
        desc = module_type.get('event').get(event_type).get('desc')
        description = re.sub("\$host", node, desc)
        description = re.sub("\$status", event_type, description)
        Log.info(f'Sending an IEM for: {component}-{module} to IEM framework. Description:  {description}')

        try:
            EventMessage.init(component, source)
        except EventMessageError as iemerror:
            Log.error(f"Event Message Initialization Error : {iemerror}")

        node_params = NodeParams.get_node_map(node)


        # TODO To be deleted once NODE_MAP_ATTRIBUTES.HOST_ID is avilable in this branch
        node_id = self._get_node_id(node)

        try:
            EventMessage.send(module=module, event_id=event_id, severity=severity, message_blob=description,
            problem_cluster_id=node_params[NODE_MAP_ATTRIBUTES.CLUSTER_ID.value], \
            problem_site_id=node_params[NODE_MAP_ATTRIBUTES.SITE_ID.value], \
            problem_rack_id=node_params[NODE_MAP_ATTRIBUTES.RACK_ID.value], \
            # TODO to be enabled once HOST_ID is avilable in NODE_MAP_ATTRIBUTES
            #problem_node_id=node_params[NODE_MAP_ATTRIBUTES.HOST_ID.value], \
            problem_node_id=node_id, \
            problem_host=node)

        except EventMessageError as iemerror:
            Log.error(f"Error in sending IEM.  Error : {iemerror}")
