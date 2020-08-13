#!/usr/bin/env python3

"""
**************************************************************************
 **filename:          cluster.py
 Description:       Cluster Management

 Creation Date:     07/09/2020
 Author:            Ajay Paratmandali

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2020 - $Date: 2020/08/13 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
****************************************************************************
"""

import time

from eos.utils.log import Log
from eos.utils.schema.conf import Conf
from eos.utils.ha.dm.actions import Action

from ha.utility.process import Process
from ha.core.cleanup import PcsCleanup
from ha.utility.error import HAInvalidNode, HAUnimplemented
from ha import const

class Cluster:
    def __init__(self, decision_monitor):
        """
        Manage cluster operation
        """
        self._decision_monitor = decision_monitor

    def node_status(self, node):
        raise HAUnimplemented()

    def remove_node(self, node):
        raise HAUnimplemented()

    def add_node(self, node):
        raise HAUnimplemented()

    def verify_node(self, node):
        raise HAUnimplemented()

    def get_node_list(self):
        raise HAUnimplemented()

class PcsCluster(Cluster):
    def __init__(self, decision_monitor):
        """
        PcsCluster manage pacemaker/corosync cluster
        """
        super(PcsCluster, self).__init__(decision_monitor)
        self._pcs_cleanup = PcsCleanup(decision_monitor)
        self._node_status = [ 'Online', 'Standby', 'Maintenance', 'Offline', 'Disconnected']

    def verify_node(self, node):
        """
        Check if node is part of cluster. Return false if not.
        """
        Log.debug(f"verify node:{node} from cluster nodes.")
        return node in self.get_node_list()

    def get_node_list(self):
        """
        Get list of node in cluster
        """
        return list(Conf.get(const.RESOURCE_GLOBAL_INDEX, "nodes").values())

    def failback(self, node=None):
        """
        Check alert and iem and perform failback
        Parameter:
            node: Node name which need failback.
        If all hw/iem alert resolved perform failback.
        If all are in ok state or some in failed state then ignore.
        """
        node = node if node != None else Conf.get(const.RESOURCE_GLOBAL_INDEX, "nodes.local")
        Log.debug(f"Performing failback on {node}")
        if not self.verify_node(node):
            raise HAInvalidNode(f"Invalid node {node}, not part of Cluster")
        resource_list = Conf.get(const.RESOURCE_GLOBAL_INDEX, "resources")
        status_list = []
        for resource in resource_list:
            if node in resource:
                status_list.append(self._decision_monitor.get_resource_status(resource))
                Log.debug(f"For {resource} status is {status_list[-1]}")
        if Action.FAILED in status_list:
            Log.debug("Some component are not yet recovered skipping failback")
        elif Action.RESOLVED in status_list:
            Log.debug(f"Starting failback from {node}")
            self._pcs_cleanup.resource_reset(node)
        else:
            Log.debug(f"{node} already in good state no need for failback")

    def node_status(self, node):
        """
        Check node status
        If node not detected return rc as 1 else 0
        Node status:
         Online:
         Standby:
         Maintenance:
         Offline:
        """
        Log.debug(f"Check {node} node status")
        if not self.verify_node(node):
            raise HAInvalidNode(f"Invalid node {node}, not part of Cluster")
        _output, _err, _rc = Process._run_cmd(const.PCS_NODE_STATUS)
        for status in _output.split("\n"):
            if node in status.split():
                node_rc = 0
                node_status = (status.split()[0])[:-1]
                Log.debug(f"For {node} node rc: {node_rc}, status: {node_status}")
                return node_rc, node_status
        Log.debug(f"{node} is not detected in cluster, treating as disconnected node")
        return 1, "Disconnected"

    def remove_node(self, node):
        """
        Remove node from pcs cluster
        """
        if not self.verify_node(node):
            raise HAInvalidNode(f"Invalid node {node}, not part of Cluster")
        _rc, status = self.node_status(node)
        if _rc != 1:
            Process._run_cmd(f"pcs cluster node remove {node} --force")
            _rc, status = self.node_status(node)
            Log.debug(f"For node {node} status: {status}, rc: {_rc}")
            if _rc != 1:
                Log.error(f"Failed to remove {node}")
                raise Exception(f"Failed to remove {node}")
            else:
                Log.info(f"Node {node} removed from cluster")
        else:
            Log.info(f"Node {node} already removed from cluster")

    def add_node(self, node):
        """
        Add new node to pcs cluster
        """
        if not self.verify_node(node):
            raise HAInvalidNode(f"Invalid node {node}, not part of Cluster")
        commands = [f"pcs cluster node add {node}",
                "pcs resource cleanup --all",
                f"pcs cluster enable {node}",
                f"pcs cluster start {node}"]
        _rc, status = self.node_status(node)
        if _rc != 0:
            for command in commands:
                Process._run_cmd(command)
            time.sleep(20)
            _rc, status = self.node_status(node)
            Log.debug(f"{node} status rc: {_rc}, status: {status}")
            if status != 'Online':
                Log.error(f"Failed to add {node}")
                raise Exception(f"Failed to add {node}")
            else:
                Log.info(f"Node {node} added to cluster")
        else:
            Log.info(f"Node {node} already added to cluster")