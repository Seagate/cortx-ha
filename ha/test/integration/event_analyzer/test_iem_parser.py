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
from ha import const

# Test case for iem parser
if __name__ == '__main__':
    ConfigManager.init("test_iem_parser")
    confstore = ConfigManager._get_confstore()
    iem_parser = IEMParser()
    print("********iem Parser********")
    resource_type = "node"
    host = "abcd.com"
    node_id = "001"
    status = "offline"
    iem_description = const.IEM_DESCRIPTION
    iem_description = Template(iem_description).substitute(host=host, status=status)
    TestMsg = {
        "sspl_ll_msg_header": {
        "msg_version": "1.0.0",
        "schema_version": "1.0.0",
        "sspl_version": "1.0.0"
        },
        "sensor_response_type": {
            "info": {
                "event_time": "1574075909",
                "resource_id": "Fan Module 4",
                "site_id": 1,
                "node_id": 1,
                "cluster_id": 1,
                "rack_id": 1,
                "resource_type": resource_type,
                "description": iem_description
            },
            "alert_type": "missing",
            "severity": "warning",
            "specific_info": {
                "source": "Software",
                "component": "ha",
                "module": "Node",
                "event": "The cluster has lost one server. System is running in degraded mode.",
                "IEC": "WS0080010001"
            },
            "alert_id": "15740759091a4e14bca51d46908ac3e9102605d560",
            "host_id": "abcd.com"
        }
    }

    # Push hostname to node id mapping to confstore
    print(f"Adding hostname to node id mapping to confstore for {host}:{node_id}")
    confstore.set(f"{const.HOSTNAME_TO_NODEID_KEY}/{host}", node_id)

    try:
        health_event = iem_parser.parse_event(json.dumps(TestMsg))
        if isinstance(health_event, HealthEvent):
            print(f"event_id : {health_event.event_id}")
            print(f"event_type : {health_event.event_type}")
            print(f"severity : {health_event.severity}")
            print(f"site_id : {health_event.site_id}")
            print(f"rack_id : {health_event.rack_id}")
            print(f"cluster_id : {health_event.cluster_id}")
            print(f"storageset_id : {health_event.storageset_id}")
            print(f"node_id : {health_event.node_id}")
            print(f"host_id : {health_event.host_id}")
            print(f"resource_type : {health_event.resource_type}")
            print(f"timestamp : {health_event.timestamp}")
            print(f"resource_id : {health_event.resource_id}")
            print(f"specific_info : {health_event.specific_info}")
            print("IEM parser positive test passed successfully")
        else:
            print("IEM parser positive test failed")
    except Exception as e:
        print(f"Failed to run IEM parser positive test, Error: {e}")

    try:
        # Delete one key from the IEM msg and validate the exception handling
        del TestMsg["sensor_response_type"]["alert_id"]
        msg_test = json.dumps(TestMsg)
        health_event = iem_parser.parse_event(json.dumps(TestMsg))
        print("IEM parser negative test failed")
    except Exception as e:
        print(f"IEM parser negative test passed successfully, caught err: {e}")

    # Delete hostname to node id mapping from confstore
    print(f"Deleting hostname to node id mapping from confstore for {host}")
    confstore.delete(f"{const.HOSTNAME_TO_NODEID_KEY}/{host}")