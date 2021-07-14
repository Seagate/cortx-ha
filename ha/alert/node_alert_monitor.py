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

import subprocess
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

    def get_online_nodes(self):
        """
        Get list of online nodes ids.
        """
        # Using subprocess because SimpleCommand is not handling pipe "|" output for corosync status command.
        nodes_ids = subprocess.getoutput("sudo pcs status corosync | awk '{print $1}' | tail -n+5")
        nodes_ids_list = sorted(nodes_ids.split())
        Log.info(f"List of online nodes ids in cluster in sorted ascending order: {nodes_ids_list}")
        return nodes_ids_list

    def get_local_node(self):
        """
        Get Local node name and id.
        """
        self.process = SimpleCommand()
        local_node_id, err, rc = self.process.run_cmd("crm_node -i")
        local_node_name, err, rc = self.process.run_cmd("crm_node -n")
        Log.info(f"Local node name: {local_node_name} \n Local node id: {local_node_id}")
        return local_node_id, local_node_name

    def process_alert(self):
        Log.debug("Processing event for NodeAlertMonitor")
        # Environment variable are avilable in self.crm_env
        self.iem = IemGenerator()
        # Get online nodeids from corosync. 
        nodes_ids = self.get_online_nodes()
        local_node_id, local_node_name = self.get_local_node()
        # Generate and send IEM only through the highest online node in cluster.
        if nodes_ids[-1].strip() == local_node_id.strip():
            self.iem.generate_iem(self.crm_env["CRM_alert_node"], self.alert_event_module, self.alert_event_type)
            Log.info(f"Sent IEM alert from the node - name: {local_node_name}, id: {local_node_id}")
        else:
            Log.debug(f"This node does not have highest id. Local node id : {local_node_id}, all nodes: {nodes_ids.sort()}.")
