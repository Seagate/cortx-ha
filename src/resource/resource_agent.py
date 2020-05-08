#!/usr/bin/env python3

"""
 ****************************************************************************
 Filename:          resource_agent.py
 Description:       resource_agent resource agent

 Creation Date:     04/15/2020
 Author:            Ajay Paratmandali

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2001 - $Date: 2015/01/14 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 ****************************************************************************
"""

import time
import sys
import re
import os
import json
import traceback

from eos.utils.log import Log
from eos.utils.process import SimpleProcess
from eos.utils.ha.dm.decision_monitor import DecisionMonitor
from eos.utils.ha.dm.actions import Action
from ha import const

class ResourceAgent:
    """
    Base class resource agent to monitor services
    """
    def __init__(self, decision_monitor, resource_schema):
        self.decision_monitor = decision_monitor
        self.nodes = resource_schema[const.NODE_LIST]

    def monitor(self):
        """
        Monitor service
        """
        return const.OCF_ERR_UNIMPLEMENTED

    def start(self):
        """
        Start service
        """
        return const.OCF_ERR_UNIMPLEMENTED

    def stop(self):
        """
        Stop service
        """
        return const.OCF_ERR_UNIMPLEMENTED

    def metadata(self):
        pass

    def get_env(self):
        """
        Get env variable and parameter provided by pacemaker
        """
        try:
            key = None
            ocf_env = {}
            resource_name = None
            env = os.environ
            for key in env.keys():
                if key.startswith("OCF_"):
                    ocf_env[key] = env[key]
            return ocf_env
        except Exception as e:
            Log.error(e)
            return {}

    def _acknowledge_event_group(self, key):
        """
        Ack event
        """
        try:
            self.decision_monitor.acknowledge_resource_group(key)
            return const.OCF_SUCCESS
        except Exception as e:
            Log.error(f"Failed to delete key: {key}")
            return const.OCF_ERR_GENERIC

    def _acknowledge_event(self, key):
        """
        Ack event
        """
        try:
            self.decision_monitor.acknowledge_resource(key)
            return const.OCF_SUCCESS
        except Exception as e:
            Log.error(f"Failed to delete key: {key}")
            return const.OCF_ERR_GENERIC

    def _get_status(self, callback_status, path):
        """
        Handle failover status
        """
        self_node = self.nodes[const.LOCALHOST_KEY]
        nodes_list = list(set(self.nodes.values()))
        nodes_list.remove(self_node)
        other_node = nodes_list[0]
        self_node_status = callback_status(path+'_'+self_node)
        other_node_status = callback_status(path+'_'+other_node)
        Log.debug(f"Get status for {path}")
        return self_node, other_node, self_node_status, other_node_status

    def _monitor_action(self, callback_ack, state, **args):
        """
        Return action on status
        """
        Log.debug(str(args))
        if args[const.CURRENT_NODE_STATUS] == Action.FAILED and args[const.OTHER_NODE_STATUS] == Action.FAILED:
            return const.OCF_SUCCESS
        elif args[const.CURRENT_NODE_STATUS] == Action.FAILED:
            return const.OCF_ERR_GENERIC
        elif args[const.CURRENT_NODE_STATUS] == Action.OK:
            return const.OCF_SUCCESS
        elif args[const.CURRENT_NODE_STATUS] == Action.RESOLVED:
            Log.info(f"Ack for {args[const.FILENAME_KEY]} with key {args[const.PATH_KEY]}"
                     f" node {args[const.CURRENT_NODE]}")
            return callback_ack(args[const.PATH_KEY]+'_'+args[const.CURRENT_NODE])
        elif args[const.CURRENT_NODE_STATUS] == Action.RESTART:
            if state == const.STATE_START:
                return const.OCF_SUCCESS
            elif state == const.STATE_RUNNING:
                return const.OCF_ERR_GENERIC
            elif state == const.STATE_STOP:
                callback_ack(args[const.PATH_KEY]+'_'+args[const.CURRENT_NODE])
                Log.info(f"Ack for {args[const.FILENAME_KEY]} with key {args[const.PATH_KEY]} "
                         f" node {args[const.CURRENT_NODE]}")
                return Action.RESTART
            return const.OCF_SUCCESS
        else:
            Log.error(f"Unimplemented value for status {args[const.CURRENT_NODE_STATUS]}")
            return const.OCF_ERR_UNIMPLEMENTED

    def _get_status(self, callback_status, path):
        """
        Handle failover status
        """
        self_node = self.nodes['local']
        nodes_list = list(set(self.nodes.values()))
        nodes_list.remove(self_node)
        other_node = nodes_list[0]
        self_node_status = callback_status(path+'_'+self_node)
        other_node_status = callback_status(path+'_'+other_node)
        Log.debug("Get status for %s " %path)
        return self_node, other_node, self_node_status, other_node_status

    def _monitor_action(self, callback_ack, **args):
        """
        Return action on status
        """
        Log.debug(str(args))
        if args['self_node_status'] == Action.FAILED and args['other_node_status'] == Action.FAILED:
            return OCF_SUCCESS
        elif args['self_node_status'] == Action.FAILED:
            return OCF_ERR_GENERIC
        elif args['self_node_status'] == Action.OK:
            return OCF_SUCCESS
        elif args['self_node_status'] == Action.RESOLVED:
            Log.info("Ack IEM for %s with key %s" %(args['filename'], args['path']+'_'+args['self_node']))
            return callback_ack(args['path']+'_'+args['self_node'])
        elif args['self_node_status'] == Action.RESTART:
            if 'service' in args and args['service'] != "-":
                cmd = "systemctl restart " + args['service']
                proc = SimpleProcess(cmd)
                output, err, rc = proc.run(universal_newlines=True)
                callback_ack(args['path']+'_'+args['self_node'])
                Log.info("Ack IEM for %s with key %s" %(args['filename'], args['path']+'_'+args['self_node']))
                return OCF_ERR_GENERIC if rc != 0 else OCF_SUCCESS
            else:
                # Get service name from any lib and restart service
                return OCF_SUCCESS
        else:
            Log.error("Unimplemented value for status %s" %args['self_node_status'])
            return OCF_ERR_UNIMPLEMENTED

class HardwareResourceAgent(ResourceAgent):
    """
    Resource agent to monitor hardware service
    """
    def __init__(self, decision_monitor, resource_schema):
        super(HardwareResourceAgent, self).__init__(decision_monitor, resource_schema)
        pass

    def monitor(self, state=const.STATE_RUNNING):
        """
        Monitor hardware and gives result
        """
        filename, path = self._get_params()
        Log.debug(f"In monitor for {filename}")
        if not os.path.exists(const.HA_INIT_DIR + filename) and state != const.STATE_STOP:
            return const.OCF_NOT_RUNNING
        self_node, other_node, self_node_status, other_node_status = self._get_status(
            self.decision_monitor.get_resource_group_status, path)
        Log.debug(f"In monitor group key is {path} and node {self_node}")
        return self._monitor_action(self._acknowledge_event_group, state,
            self_node=self_node, other_node=other_node,
            self_node_status=self_node_status, other_node_status=other_node_status,
            filename=filename, path=path)

    def start(self):
        """
        Start monitoring hardware and failover if resource is failed
        """
        filename, path = self._get_params()
        Log.debug(f"In start for {filename}")
        os.makedirs(const.HA_INIT_DIR, exist_ok=True)
        if not os.path.exists(const.HA_INIT_DIR + filename):
            with open(const.HA_INIT_DIR + filename, 'w'): pass
        return self.monitor(state=const.STATE_START)

    def stop(self):
        """
        Stop monitoring hardware
        """
        filename, path = self._get_params()
        Log.debug(f"In stop for {filename}")
        if os.path.exists(const.HA_INIT_DIR + filename):
            os.remove(const.HA_INIT_DIR + filename)
        while True:
            if self.monitor() == const.OCF_NOT_RUNNING:
                time.sleep(2)
                break
        if self.monitor(state=const.STATE_STOP) == Action.RESTART:
            Log.debug(f"Restarting {filename} resource")
            time.sleep(2)
            return const.OCF_SUCCESS
        return const.OCF_SUCCESS

    def metadata(self):
        """
        Provide meta data for resource agent and parameter
        """
        env=r'''
        <?xml version="1.0"?>
        <!DOCTYPE resource-agent SYSTEM "ra-api-1.dtd">
        <resource-agent name="hw_comp_ra">
        <version>1.0</version>

        <longdesc lang="en">
        Hardware Resource agent
        </longdesc>
        <shortdesc lang="en">Hardware Resource agent</shortdesc>
        <parameters>
        <parameter name="path">
        <longdesc lang="en"> Path to check status </longdesc>
        <shortdesc lang="en"> Check io or management path </shortdesc>
        <content type="string"/>
        </parameter>
        <parameter name="filename">
        <longdesc lang="en"> Node_id for resource </longdesc>
        <shortdesc lang="en"> Node id for resource </shortdesc>
        <content type="string"/>
        </parameter>
        </parameters>
        <actions>
        <action name="start"        timeout="20s" />
        <action name="stop"         timeout="20s" />
        <action name="monitor"      timeout="20s" interval="10s" depth="0" />
        <action name="meta-data"    timeout="5s" />
        </actions>
        </resource-agent>
        '''
        print(env)

    def _get_params(self):
        """
        Provide pacemaker parameter
        """
        try:
            ocf_env = self.get_env()
            filename = ocf_env[const.OCF_FILENAME]
            path = ocf_env[const.OCF_PATH]
            return filename, path
        except Exception as e:
            Log.error(e)
            return const.OCF_ERR_CONFIGURED

class IEMResourceAgent(ResourceAgent):
    """
    Resource agent to monitor software iem
    """
    def __init__(self, decision_monitor, resource_schema):
        super(IEMResourceAgent, self).__init__(decision_monitor, resource_schema)
        pass

    def monitor(self, state=const.STATE_RUNNING):
        """
        Monitor hardware and gives result
        """
        filename, path, service, node = self._get_params()
        Log.debug(f"In monitor for {filename}")
        if not os.path.exists(const.HA_INIT_DIR + filename) and state != const.STATE_STOP:
            return const.OCF_NOT_RUNNING
        self_node, other_node, self_node_status, other_node_status = self._get_status(
            self.decision_monitor.get_resource_status, path)
        Log.debug(f"In monitor group key: {path}, node: {self_node} "
                  f"status: {self_node_status}, service: {service}")
        if node != '-' and node != self_node and other_node_status == Action.RESOLVED:
            Log.info(f"Ack IEM for {filename} with key {path} node {node}")
            self._acknowledge_event(path+'_'+node)
        return self._monitor_action(self._acknowledge_event, state,
            self_node=self_node, other_node=other_node,
            self_node_status=self_node_status, other_node_status=other_node_status,
            filename=filename, path=path, service=service)

    def start(self):
        """
        Start monitoring hardware and failover if resource is failed
        """
        filename, path, service, node = self._get_params()
        Log.debug(f"In start for {filename}")
        os.makedirs(const.HA_INIT_DIR, exist_ok=True)
        if not os.path.exists(const.HA_INIT_DIR + filename):
            with open(const.HA_INIT_DIR + filename, 'w'): pass
        return self.monitor(state=const.STATE_START)

    def stop(self):
        """
        Stop monitoring hardware
        """
        filename, path, service, node = self._get_params()
        Log.debug(f"In stop for {filename}")
        if os.path.exists(const.HA_INIT_DIR + filename):
            os.remove(const.HA_INIT_DIR + filename)
        while True:
            if self.monitor() == const.OCF_NOT_RUNNING:
                time.sleep(2)
                break
        if self.monitor(state=const.STATE_STOP) == Action.RESTART:
            Log.debug(f"Restarting {filename} resource")
            time.sleep(2)
            return const.OCF_SUCCESS
        return const.OCF_SUCCESS

    def metadata(self):
        """
        Provide meta data for resource agent and parameter
        """
        env=r'''
        <?xml version="1.0"?>
        <!DOCTYPE resource-agent SYSTEM "ra-api-1.dtd">
        <resource-agent name="iem_comp_ra">
        <version>1.0</version>

        <longdesc lang="en">
        IEM Resource agent
        </longdesc>
        <shortdesc lang="en">Hardware Resource agent</shortdesc>
        <parameters>
        <parameter name="path">
        <longdesc lang="en"> Path to check status </longdesc>
        <shortdesc lang="en"> Check io or management path </shortdesc>
        <content type="string"/>
        </parameter>
        <parameter name="filename">
        <longdesc lang="en"> Node_id for resource </longdesc>
        <shortdesc lang="en"> Node id for resource </shortdesc>
        <content type="string"/>
        </parameter>
        <parameter name="service">
        <longdesc lang="en"> Enter service name to handle </longdesc>
        <shortdesc lang="en"> Handle service for IEM </shortdesc>
        <content type="string" default="-"/>
        </parameter>
        <parameter name="node">
        <longdesc lang="en"> Node id </longdesc>
        <shortdesc lang="en"> Node id to identify resource on same node </shortdesc>
        <content type="string" default="-"/>
        </parameter>
        </parameters>
        <actions>
        <action name="start"        timeout="20s" />
        <action name="stop"         timeout="20s" />
        <action name="monitor"      timeout="20s" interval="10s" depth="0" />
        <action name="meta-data"    timeout="5s" />
        </actions>
        </resource-agent>
        '''
        print(env)

    def _get_params(self):
        """
        Provide pacemaker parameter
        """
        try:
            ocf_env = self.get_env()
            filename = ocf_env[const.OCF_FILENAME]
            path = ocf_env[const.OCF_PATH]
            node = ocf_env[const.OCF_NODE] if const.OCF_NODE in ocf_env else '-'
            service = ocf_env[const.OCF_SERVICE] if const.OCF_SERVICE in ocf_env else '-'
            return filename, path, service, node
        except Exception as e:
            Log.error(e)
            return const.OCF_ERR_CONFIGURED

def main(resource, action=''):
    try:
        with open(const.RESOURCE_SCHEMA, 'r') as f:
            resource_schema = json.load(f)
        log_level = 'INFO' if 'log' not in resource_schema else resource_schema['log']
        os.makedirs(const.RA_LOG_DIR, exist_ok=True)
        Log.init(service_name='resource_agent', log_path=const.RA_LOG_DIR, level=log_level)
        resource_agent = resource(DecisionMonitor(), resource_schema)
        if action == 'monitor':
            return resource_agent.monitor()
        elif action == 'start':
            return resource_agent.start()
        elif action == 'stop':
            return resource_agent.stop()
        elif action == 'meta-data':
            resource_agent.metadata()
        else:
            print('Usage %s [monitor] [start] [stop] [meta-data]' % sys.argv[0])
            exit()
    except Exception as e:
        Log.error(traceback.format_exc())
        return const.OCF_ERR_GENERIC
