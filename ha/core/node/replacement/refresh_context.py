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

from cortx.utils.log import Log
from cortx.utils.schema.conf import Conf
from cortx.utils.ha.dm.actions import Action

from ha import const
from ha.execute import SimpleCommand
from ha.core.error import HAUnimplemented, HAInvalidCommand

class Cleanup:
    def __init__(self, decision_monitor):
        """
        Description: Cleanup Event
        """
        self._decision_monitor = decision_monitor
        self._execute = SimpleCommand()

    def cleanup_db(self, node, data_only):
        """
        Args:
            node ([string]): Node name.
            data_only ([boolean]): Remove data only.

        Action:
            consul data:
                {'entity': 'enclosure', 'entity_id': '0',
                'component': 'controller', 'component_id': 'node1'}
            if data_only is True then remove data else remove
            data and perform cleanup.
        """
        resources = Conf.get(const.RESOURCE_GLOBAL_INDEX, "resources")
        node = "all" if node is None else node
        Log.debug(f"Performing cleanup for {node} node")
        for key in resources.keys():
            if node == "all":
                self._decision_monitor.acknowledge_resource(key, data_only)
            elif node in key:
                self._decision_monitor.acknowledge_resource(key, data_only)
            else:
                pass
        if not data_only:
            Log.info(f"Reseting HA decision event for {node}")
            self.reset_failover(node)

    def is_cleanup_required(self, node=None):
        """
        Check if all alert resolved

        Args:
            node ([type]): [description]
        """
        node = "all" if node is None else node
        Log.debug(f"Performing failback on {node}")
        resource_list = Conf.get(const.RESOURCE_GLOBAL_INDEX, "resources")
        status_list = []
        for resource in resource_list:
            if node == "all":
                status_list.append(self._decision_monitor.get_resource_status(resource))
            elif node in resource:
                status_list.append(self._decision_monitor.get_resource_status(resource))
            else:
                pass
            Log.debug(f"For {resource} status is {status_list[-1]}")
        if Action.FAILED in status_list:
            Log.debug("Some component are not yet recovered skipping failback")
        elif Action.RESOLVED in status_list:
            Log.info("Failback is required as some of alert are resolved.")
            return True
        else:
            Log.debug(f"{node} node already in good state no need for failback")
        return False

    def reset_failover(self, node=None, soft_cleanup=False):
        """
        Cleanup pacemaker failcount to allow failback.
        """
        node = "all" if node is None else node
        cmd = const.PCS_CLEANUP if node == "all" else const.PCS_CLEANUP + f" --node {node}"
        if soft_cleanup:
            if self.is_cleanup_required(node):
                _output, _err, _rc = self._execute.run_cmd(const.PCS_FAILCOUNT_STATUS)
                Log.info(f"Resource failcount before Failback: {_output}, Error:{_err}, RC:{_rc}")
                _output, _err, _rc = self._execute.run_cmd(cmd)
                Log.info(f"Failback is happened, Output:{_output}, Error:{_err}, RC:{_rc}")
                _output, _err, _rc = self._execute.run_cmd(const.PCS_FAILCOUNT_STATUS)
                Log.info(f"Resource failcount after Failback: {_output}, Error:{_err}, RC:{_rc}")
            else:
                Log.debug("cleanup is not required alerts are not yet resolved.")
        else:
            self._execute.run_cmd(cmd)
        Log.debug(f"Status: {self._execute.run_cmd(const.PCS_STATUS)}")

class RefreshContex:
    def __init__(self, decision_monitor):
        pass

    def process_request(self, action, args):
        """
        Generic method to handle process request

        Args:
            action ([string]): Take cluster action for each request.
            args ([dict]): Parameter pass to request to process.
        """
        raise HAUnimplemented()

class PcsRefreshContex(RefreshContex):
    def __init__(self, decision_monitor):
        self._decision_monitor = decision_monitor
        self._cleanup = Cleanup(self._decision_monitor)

    def process_request(self, action, args):
        """
        Generic method to handle process request

        Args:
            action ([string]): Take cluster action for each request.
            args ([dict]): Parameter pass to request to process.

        Action:
            Cleanup resource history            : default
            Remove old consul keys              : --hard --data-only
            Remove old consul key and cleanup   : --hard
            Check Alert and perform cleanup     : --soft
        """
        if args.hard == False and args.soft == False and args.data_only == False:
            self._cleanup.reset_failover(args.node)
        elif args.hard == True and args.soft == True:
            raise HAInvalidCommand("Select one of hard or soft option only.")
        elif args.hard == True:
            self._cleanup.cleanup_db(args.node, args.data_only)
        elif args.soft == True:
            # Failback trigger
            self._cleanup.reset_failover(args.node, args.soft)
        else:
            raise HAUnimplemented()