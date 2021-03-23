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

import time

from cortx.utils.log import Log
from ha.execute import SimpleCommand
from ha import const
from ha.cli.exec.commandExecutor import CommandExecutor
from ha.core.error import HAClusterStart

class ClusterStartExecutor(CommandExecutor):

    def __init__(self):

        # To be removed once the "cortx cluster start" user story [EOS-16248] is started
        self._execute = SimpleCommand()

    def validate(self):
        print("Placeholder: validate for ", self.__class__.__name__)

    def get_nodes_status(self):
        """
        Sample output of the const.PCS_STATUS_NODES command

        Pacemaker Nodes:
         Online: node1 node2
         Standby:
         Standby with resource(s) running:
         Maintenance:
         Offline:
        Pacemaker Remote Nodes:
         Online:
         Standby:
         Standby with resource(s) running:
         Maintenance:
         Offline:
        """
        _output, _err, _rc = self._execute.run_cmd(const.PCS_STATUS_NODES, check_error=False)

        self.active_nodes = self.standby_nodes = self.offline_nodes = False

        for status in _output.split("\n"):
            nodes = status.split(":", 1)
            # This break should be removed if pacemaker remote is also used in the cluster
            if nodes[0] == "Pacemaker Remote Nodes":
                break
            elif nodes[0] == " Online" and len(nodes[1].split()) > 0:
                self.active_nodes = True
            elif nodes[0] == " Standby" and len(nodes[1].split()) > 0:
                self.standby_nodes = True
            elif nodes[0] == " Standby with resource(s) running" and len(nodes[1].split()) > 0:
                self.active_nodes = True
            elif nodes[0] == " Maintenance" and len(nodes[1].split()) > 0:
                self.active_nodes = True
            elif nodes[0] == "  Offline" and len(nodes[1].split()) > 0:
                self.offline_nodes = True


    def execute(self):

        # This is temporary code, copied from M0
        # To be removed once the "cortx cluster start" user story [EOS-16248] is started
        Log.info("Executing cortxha cluster start")
        print("Executing cortxha cluster start")

        _output, _err, _rc = self._execute.run_cmd(const.PCS_CLUSTER_STATUS, check_error=False)
        if _rc != 0:
            if(_err.find("No such file or directory: 'pcs'") != -1):
                Log.error("Cluster failed to start; pcs not installed")
                #print("Cluster failed to start; pcs not installed")
                raise HAClusterStart("Cluster failed to start; pcs not installed")
            # if cluster is not running; start cluster
            elif(_err.find("cluster is not currently running on this node") != -1):
                self._execute.run_cmd(const.PCS_CLUSTER_START, check_error=False)
                Log.info("cluster started ; waiting for nodes to come online ")
                # It takes nodes 30 seconds to come to their original state after cluster is started
                # observation on a 2 node cluster
                # wait for upto 100 sec for nodes to come to active states (online / maintenance mode)
                time.sleep(10)
                self.get_nodes_status()
                retries = 18
                while  self.active_nodes == False and retries > 0:
                    time.sleep(5)
                    self.get_nodes_status()
                    retries -= 1

        else:
            #If cluster is running, but all nodes are  in Standby mode;
            #start the nodes
            self.get_nodes_status()
            if self.active_nodes == False:
                if self.standby_nodes == True:
                    # issue pcs cluster unstandby
                    _output, _err, _rc = self._execute.run_cmd(const.PCS_CLUSTER_UNSTANDBY, check_error=False)

        # check cluster and node status
        _output, _err, _rc = self._execute.run_cmd(const.PCS_CLUSTER_STATUS, check_error=False)
        if _rc != 0:
            # cluster could not be started.
            Log.error("Cluster failed to start")
            raise HAClusterStart("Cluster failed to start")
        else:
            # confirm that at least one node is active
            self.get_nodes_status()
            if self.active_nodes == False:
                # wait for 5 seconds and retry
                time.sleep(5)
                self.get_nodes_status()
                if self.active_nodes == False:
                    Log.info("Cluster started; nodes not online")
                    raise HAClusterStart("Cluster started; nodes not online")

        Log.info("Cluster started successfully")


class ClusterStopExecutor(CommandExecutor):
    def validate(self):
        print("Placeholder: validate for ", self.__class__.__name__)

    def execute(self):
        print("Placeholder:  execute for ", self.__class__.__name__)

class ClusterRestartExecutor(CommandExecutor):
    def validate(self):
        print("Placeholder: validate for ", self.__class__.__name__)

    def execute(self):
        print("Placeholder:  execute for ", self.__class__.__name__)

class ClusterStandbyExecutor(CommandExecutor):
    def validate(self):
        print("Placeholder: validate for ", self.__class__.__name__)

    def execute(self):
        print("Placeholder:  execute for ", self.__class__.__name__)

class ClusterActiveExecutor(CommandExecutor):
    def validate(self):
        print("Placeholder: validate for ", self.__class__.__name__)

    def execute(self):
        print("Placeholder:  execute for ", self.__class__.__name__)

class ClusterListExecutor(CommandExecutor):
    def validate(self):
        print("Placeholder: validate for ", self.__class__.__name__)

    def execute(self):
        print("Placeholder:  execute for ", self.__class__.__name__)

class ClusterStatusExecutor(CommandExecutor):
    def validate(self):
        print("Placeholder: validate for ", self.__class__.__name__)

    def execute(self):
        print("Placeholder:  execute for ", self.__class__.__name__)

class ClusterAddExecutor(CommandExecutor):
    def validate(self):
        print("Placeholder: validate for ", self.__class__.__name__)

    def execute(self):
        print("Placeholder:  execute for ", self.__class__.__name__)
