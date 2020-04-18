#!/usr/bin/env python3

"""
 ****************************************************************************
 Filename:          hw_alert.py
 Description:       hw_alert resource agent

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
import pathlib

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

    @staticmethod
    def monitor():
        """
        Monitor service
        """
        pass

    @staticmethod
    def start():
        """
        Start service
        """
        pass

    @staticmethod
    def stop():
        """
        Stop service
        """
        pass

    @staticmethod
    def metadata():
        pass

class HardwareResourceAgent(ResourceAgent):
    """
    Resource agent to monitor hardware service
    """
    @staticmethod
    def monitor():
        """
        Monitor hardware and gives result
        """
        #return OCF_ERR_GENERIC
        return OCF_SUCCESS
        #return OCF_NOT_RUNNING

    @staticmethod
    def start():
        """
        Start monitoring hardware and failover if resource is failed
        """
        try:
            status = monitor()
        except:
            return OCF_ERR_GENERIC
        if status == OCF_SUCCESS:
            return OCF_SUCCESS
        elif status == OCF_NOT_RUNNING:
            try:
                stop()
            except:
                return OCF_ERR_GENERIC
        else:
            return OCF_ERR_GENERIC

    @staticmethod
    def stop():
        """
        Stop monitoring hardware
        """
        return OCF_SUCCESS

    @staticmethod
    def metadata():
        """
        Provide meta data for resource agent and patameter
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
        <parameter name="key" unique="1" required="1">
        <longdesc lang="en"> Key To identify result in DB </longdesc>
        <shortdesc lang="en"> Key To identify result in DB </shortdesc>
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

    @staticmethod
    def get_env():
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
            #ocf_env['OCF_RESOURCE_INSTANCE'] RESOURCE NAME
            #ocf_env['OCF_RESKEY_key']  KEY
            return ocf_env    
        except Exception as e:
            return {}

def main():
    try:
        if len(sys.argv)==1:
            print('Usage %s [monitor | start | stop | meta-data]' % sys.argv[0])
            exit()
        if sys.argv[1]=='monitor':
            return HardwareResourceAgent.monitor()
        elif sys.argv[1]=='start':
            return HardwareResourceAgent.start()
        elif sys.argv[1]=='stop':
            return HardwareResourceAgent.stop()
        elif sys.argv[1]=='meta-data':
            HardwareResourceAgent.metadata()
        else:
            print('Usage %s [monitor] [start] [stop] [meta-data]' % sys.argv[0])
            exit()
    except Exception as e:
        raise e

if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))
    sys.exit(main())
