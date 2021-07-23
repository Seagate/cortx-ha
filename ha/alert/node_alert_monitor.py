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

import xml.etree.ElementTree as ET
from cortx.utils.log import Log
from ha.alert.alert_monitor import AlertMonitor
from ha.alert.iem import IemGenerator
from ha.execute import SimpleCommand


class NodeAlertMonitor(AlertMonitor):

    def __init__(self):
        """
        Init node alert monitor
        """
        super(NodeAlertMonitor, self).__init__()
        self.process = SimpleCommand()

    def _get_online_nodes(self):
        """
        Get list of online nodes ids.
        """
        online_nodes_xml, err, rc = self.process.run_cmd("crm_mon --as-xml")
        # saving the xml file
        with open('nodes.xml', 'w+') as f:
            f.write(online_nodes_xml)
        # create element tree object
        tree = ET.parse('nodes.xml')
        # get root element
        root = tree.getroot()
        nodes_ids = []
        # iterate news items
        for item in root.findall('nodes'):
            # iterate child elements of item
            for child in item:
                if child.attrib['online'] == 'true':
                    nodes_ids.append(child.attrib['id'])
        Log.info(f"List of online nodes ids in cluster in sorted ascending order: {sorted(nodes_ids)}")
        # file cleanup
        if os.path.exists("nodes.xml"):
            os.remove("nodes.xml")
        return sorted(nodes_ids)

    def _get_local_node(self):
        """
        Get Local node name and id.
        """
        local_node_id, err, rc = self.process.run_cmd("crm_node -i")
        local_node_name, err, rc = self.process.run_cmd("crm_node -n")
        Log.info(f"Local node name: {local_node_name} \n Local node id: {local_node_id}")
        return local_node_id, local_node_name

    def process_alert(self):
        Log.debug("Processing event for NodeAlertMonitor")
        # Environment variable are available in self.crm_env
        self.iem = IemGenerator()
        # Get online nodeids from corosync.
        nodes_ids = self._get_online_nodes()
        local_node_id, local_node_name = self._get_local_node()
        # Generate and send IEM only through the highest online node in cluster.
        if nodes_ids[-1].strip() == local_node_id.strip():
            self.iem.generate_iem(self.crm_env["CRM_alert_node"], self.alert_event_module, self.alert_event_type)
            Log.info(f"Sent IEM alert from the node - name: {local_node_name}, id: {local_node_id}")
        else:
            Log.debug(
                f"This node does not have highest id. Local node id : {local_node_id}, all nodes: {nodes_ids.sort()}.")
