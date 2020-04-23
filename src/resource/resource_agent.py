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

from eos.utils.log import Log
from eos.utils.process import SimpleProcess
from eos.utils.ha.dm.decision_monitor import DecisionMonitor
from eos.utils.ha.dm.actions import Action
from ha import const

OCF_SUCCESS=0
OCF_ERR_GENERIC=1
OCF_ERR_ARGS=2
OCF_ERR_UNIMPLEMENTED=3
OCF_ERR_PERM=4
OCF_ERR_INSTALLED=5
OCF_ERR_CONFIGURED=6
OCF_NOT_RUNNING=7

class ResourceAgent:
    """
    Base class resource agent to monitor services
    """
    def __init__(self, decision_monitor, resource_schema):
        pass

    def monitor(self):
        """
        Monitor service
        """
        return OCF_ERR_UNIMPLEMENTED

    def start(self):
        """
        Start service
        """
        return OCF_ERR_UNIMPLEMENTED

    def stop(self):
        """
        Stop service
        """
        return OCF_ERR_UNIMPLEMENTED

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

    def acknowledge_event(self, key):
        """
        Ack event
        """
        try:
            self.decision_monitor.acknowledge_resource_group(key)
            return OCF_SUCCESS
        except Exception as e:
            Log.error("Failed to delete key: %s" %(key))
            return OCF_ERR_GENERIC

class HardwareResourceAgent(ResourceAgent):
    """
    Resource agent to monitor hardware service
    """
    def __init__(self, decision_monitor, resource_schema):
        super(HardwareResourceAgent, self).__init__(decision_monitor, resource_schema)
        self.decision_monitor = decision_monitor
        self.nodes = resource_schema['nodes']

    def monitor(self):
        """
        Monitor hardware and gives result
        """
        filename, path = self._get_params()
        Log.debug("In monitor for %s" %filename)
        if not os.path.exists(const.HA_INIT_DIR + filename):
            return OCF_NOT_RUNNING
        key = self.nodes['local']
        Log.debug("In monitor group key is {}".format(path+'_'+key))
        status = self.decision_monitor.get_resource_group_status(path+'_'+key)
        if status == Action.FAILED:
            return OCF_ERR_GENERIC
        elif status == Action.OK:
            return OCF_SUCCESS
        elif status == Action.RESOLVED:
            Log.info("Ack IEM for %s with key %s" %(filename, path+'_'+key))
            return self.acknowledge_event(path+'_'+key)
        else:
            Log.error("Unimplemented value for status %s" %status)
            return OCF_ERR_UNIMPLEMENTED

    def start(self):
        """
        Start monitoring hardware and failover if resource is failed
        """
        filename, path = self._get_params()
        Log.debug("In start for %s" %filename)
        os.makedirs(const.HA_INIT_DIR, exist_ok=True)
        if not os.path.exists(const.HA_INIT_DIR + filename):
            with open(const.HA_INIT_DIR + filename, 'w'): pass
        return self.monitor()

    def stop(self):
        """
        Stop monitoring hardware
        """
        filename, path = self._get_params()
        Log.debug("In stop for %s" %filename)
        if os.path.exists(const.HA_INIT_DIR + filename):
            os.remove(const.HA_INIT_DIR + filename)
        while True:
            if self.monitor() != OCF_SUCCESS:
                time.sleep(2)
                break
        return OCF_SUCCESS

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
            filename = ocf_env['OCF_RESKEY_filename']
            path = ocf_env['OCF_RESKEY_path']
            return filename, path
        except Exception as e:
            Log.error(e)
            return OCF_ERR_CONFIGURED

class IEMResourceAgent(ResourceAgent):
    """
    Resource agent to monitor software iem
    """
    def __init__(self, decision_monitor, resource_schema):
        super(IEMResourceAgent, self).__init__(decision_monitor, resource_schema)
        self.decision_monitor = decision_monitor
        self.nodes = resource_schema['nodes']

    def monitor(self):
        """
        Monitor hardware and gives result
        """
        filename, path, service, node = self._get_params()
        Log.debug("In monitor for %s" %filename)
        if not os.path.exists(const.HA_INIT_DIR + filename):
            return OCF_NOT_RUNNING
        key = self.nodes['local']
        status = self.decision_monitor.get_resource_group_status(path+'_'+key)
        Log.debug("In monitor group key: %s, status: %s, service: %s" %(path+'_'+key, status, service))
        if status == Action.FAILED:
            return OCF_ERR_GENERIC
        elif status == Action.OK:
            return OCF_SUCCESS
        elif status == Action.RESOLVED:
            return self.acknowledge_event(path+'_'+key)
        elif status == Action.RESTART:
            if service != "-":
                cmd = "systemctl restart " + service
                proc = SimpleProcess(cmd)
                output, err, rc = proc.run(universal_newlines=True)
                self.acknowledge_event(path+'_'+key)
                Log.info("Ack IEM for %s with key %s" %(filename, path+'_'+key))
                return OCF_ERR_GENERIC if rc != 0 else OCF_SUCCESS
            else:
                # Get service name from any lib and restart service
                return OCF_SUCCESS
        else:
            Log.error("Unimplemented value for status %s" %status)
            return OCF_ERR_UNIMPLEMENTED

    def start(self):
        """
        Start monitoring hardware and failover if resource is failed
        """
        filename, path, service, node = self._get_params()
        Log.debug("In start for %s" %filename)
        key = self.nodes['local']
        os.makedirs(const.HA_INIT_DIR, exist_ok=True)
        if not os.path.exists(const.HA_INIT_DIR + filename):
            with open(const.HA_INIT_DIR + filename, 'w'): pass
        if key != node:
            Log.info("Ack IEM for %s with key %s" %(filename, path+'_'+key))
            self.acknowledge_event(path+'_'+key)
        return self.monitor()

    def stop(self):
        """
        Stop monitoring hardware
        """
        filename, path, service, node = self._get_params()
        Log.debug("In stop for %s" %filename)
        if os.path.exists(const.HA_INIT_DIR + filename):
            os.remove(const.HA_INIT_DIR + filename)
        while True:
            if self.monitor() != OCF_SUCCESS:
                time.sleep(2)
                break
        return OCF_SUCCESS

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
        <parameter name="service">
        <longdesc lang="en"> Enter service name to handle </longdesc>
        <shortdesc lang="en"> Handle service for IEM </shortdesc>
        <content type="string" default="-"/>
        <parameter name="node">
        <longdesc lang="en"> Node id </longdesc>
        <shortdesc lang="en"> Node id to identify resource on same node </shortdesc>
        <content type="string"/>
        </parameter>
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
            filename = ocf_env['OCF_RESKEY_filename']
            path = ocf_env['OCF_RESKEY_path']
            path = ocf_env['OCF_RESKEY_node']
            if 'OCF_RESKEY_service' not in ocf_env:
                ocf_env['OCF_RESKEY_service'] = '-'
            service = ocf_env['OCF_RESKEY_service']
            return filename, path, service, node
        except Exception as e:
            Log.error(e)
            return OCF_ERR_CONFIGURED

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
        Log.error(e)
        return OCF_ERR_GENERIC