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

import json
import os
import sys
import pathlib
from string import Template

sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))
from ha.core.event_analyzer.parser.parser import IEMParser
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.config.config_manager import ConfigManager
from ha.const import IEM_DESCRIPTION, PVTFQDN_TO_NODEID_KEY, ALERT_ATTRIBUTES, EVENT_ATTRIBUTES

# Test case for iem parser
if __name__ == '__main__':
    ConfigManager.init("test_iem_parser")
    confstore = ConfigManager._get_confstore()
    iem_parser = IEMParser()
    print("********iem Parser********")
    resource_type = "node"
    host = "abcd.data.private"
    node_id = "001"
    status = "offline"
    iem_description = IEM_DESCRIPTION
    iem_description = Template(iem_description).substitute(host=host, status=status)
    TestMsg = {
        ALERT_ATTRIBUTES.HEADER: {
        ALERT_ATTRIBUTES.MSG_VERSION: "1.0.0",
        ALERT_ATTRIBUTES.SCHEMA_VERSION: "1.0.0",
        ALERT_ATTRIBUTES.SSPL_VERSION: "1.0.0"
        },
        ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE: {
            ALERT_ATTRIBUTES.INFO: {
                ALERT_ATTRIBUTES.EVENT_TIME: "1574075909",
                ALERT_ATTRIBUTES.RESOURCE_ID: "Fan Module 4",
                ALERT_ATTRIBUTES.SITE_ID: 1,
                ALERT_ATTRIBUTES.NODE_ID: 1,
                ALERT_ATTRIBUTES.CLUSTER_ID: 1,
                ALERT_ATTRIBUTES.RACK_ID: 1,
                ALERT_ATTRIBUTES.RESOURCE_TYPE: resource_type,
                ALERT_ATTRIBUTES.DESCRIPTION: iem_description
            },
            ALERT_ATTRIBUTES.ALERT_TYPE: "missing",
            ALERT_ATTRIBUTES.SEVERITY: "warning",
            ALERT_ATTRIBUTES.SPECIFIC_INFO: {
                ALERT_ATTRIBUTES.SOURCE: "Software",
                ALERT_ATTRIBUTES.COMPONENT: "ha",
                ALERT_ATTRIBUTES.MODULE: "Node",
                ALERT_ATTRIBUTES.EVENT: "The cluster has lost one server. System is running in degraded mode.",
                ALERT_ATTRIBUTES.IEC: "WS0080010001"
            },
            ALERT_ATTRIBUTES.ALERT_ID: "15740759091a4e14bca51d46908ac3e9102605d560",
            ALERT_ATTRIBUTES.HOST_ID: "abcd.com"
        }
    }

    # Push hostname to node id mapping to confstore
    print(f"Adding hostname to node id mapping to confstore for {host}:{node_id}")
    confstore.set(f"{PVTFQDN_TO_NODEID_KEY}/{host}", node_id)

    try:
        health_event = iem_parser.parse_event(json.dumps(TestMsg))
        if isinstance(health_event, HealthEvent):
            print(f"{EVENT_ATTRIBUTES.EVENT_ID} : {health_event.event_id}")
            print(f"{EVENT_ATTRIBUTES.EVENT_TYPE} : {health_event.event_type}")
            print(f"{EVENT_ATTRIBUTES.SEVERITY} : {health_event.severity}")
            print(f"{EVENT_ATTRIBUTES.SITE_ID} : {health_event.site_id}")
            print(f"{EVENT_ATTRIBUTES.RACK_ID} : {health_event.rack_id}")
            print(f"{EVENT_ATTRIBUTES.CLUSTER_ID} : {health_event.cluster_id}")
            print(f"{EVENT_ATTRIBUTES.STORAGESET_ID} : {health_event.storageset_id}")
            print(f"{EVENT_ATTRIBUTES.NODE_ID} : {health_event.node_id}")
            print(f"{EVENT_ATTRIBUTES.HOST_ID} : {health_event.host_id}")
            print(f"{EVENT_ATTRIBUTES.RESOURCE_TYPE} : {health_event.resource_type}")
            print(f"{EVENT_ATTRIBUTES.TIMESTAMP} : {health_event.timestamp}")
            print(f"{EVENT_ATTRIBUTES.RESOURCE_ID} : {health_event.resource_id}")
            print(f"{EVENT_ATTRIBUTES.SPECIFIC_INFO} : {health_event.specific_info}")
            print("IEM parser positive test passed successfully")
        else:
            print("IEM parser positive test failed")
    except Exception as e:
        print(f"Failed to run IEM parser positive test, Error: {e}")

    try:
        # Delete one key from the IEM msg and validate the exception handling
        del TestMsg[ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_ID]
        msg_test = json.dumps(TestMsg)
        health_event = iem_parser.parse_event(json.dumps(TestMsg))
        print("IEM parser negative test failed")
    except Exception as e:
        print(f"IEM parser negative test passed successfully, caught err: {e}")

    # Delete hostname to node id mapping from confstore
    print(f"Deleting hostname to node id mapping from confstore for {host}")
    confstore.delete(f"{PVTFQDN_TO_NODEID_KEY}/{host}")