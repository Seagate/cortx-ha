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

# Test case for alert filter
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))
    from ha.core.event_analyzer.parser.parser import AlertParser
    from ha.core.system_health.model.health_event import HealthEvent
    import traceback
    try:
        alert_parser = AlertParser()
        print("********Alert Parser********")
        resource_type = "enclosure:fru:fan"
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
                    "description": "The fan module is not installed."
                },
                "alert_type": "missing",
                "severity": "critical",
                "specific_info": {
                    "status": "Not Installed",
                    "name": "Fan Module 4",
                    "enclosure-id": 0,
                    "durable-id": "fan_module_0.4",
                    "fans": [],
                    "health-reason": "The fan module is not installed.",
                    "health": "Fault",
                    "location": "Enclosure 0 - Right",
                    "position": "Indexed",
                    "health-recommendation": "Install the missing fan module."
                },
                "alert_id": "15740759091a4e14bca51d46908ac3e9102605d560",
                "host_id": "s3node-host-1"
            }
        }

        health_event = alert_parser.parse_event(json.dumps(TestMsg))

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
            print("Event alert parser test passed successfully")
        else:
            print("Event alert parser test failed")

    except Exception as e:
        print(f"{traceback.format_exc()}, {e}")
