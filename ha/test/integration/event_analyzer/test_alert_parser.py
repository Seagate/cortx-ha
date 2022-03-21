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

sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))
from ha.core.event_analyzer.parser.parser import AlertParser
from ha.core.system_health.model.health_event import HealthEvent
from ha.core.config.config_manager import ConfigManager
from ha.const import ALERT_ATTRIBUTES, EVENT_ATTRIBUTES

# Test case for alert filter
if __name__ == '__main__':
    ConfigManager.init("test_alert_parser")
    alert_parser = AlertParser()
    print("********Alert Parser********")
    resource_type = "enclosure:fru:fan"
    TestAlert = {
        ALERT_ATTRIBUTES.USERNAME: "sspl-ll",
        ALERT_ATTRIBUTES.DESCRIPTION: "Seagate Storage Platform Library - Sensor Response",
        ALERT_ATTRIBUTES.TITLE: "SSPL Sensor Response",
        ALERT_ATTRIBUTES.EXPIRES: 3600,
        ALERT_ATTRIBUTES.SIGNATURE: "None",
        ALERT_ATTRIBUTES.TITLE: "1621581798",
        ALERT_ATTRIBUTES.MESSAGE: {
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
                    ALERT_ATTRIBUTES.DESCRIPTION: "The fan module is not installed."
                },
                ALERT_ATTRIBUTES.SOURCE: 'source_1',
                ALERT_ATTRIBUTES.ALERT_TYPE: "missing",
                ALERT_ATTRIBUTES.SEVERITY: "critical",
                ALERT_ATTRIBUTES.SPECIFIC_INFO: {
                    ALERT_ATTRIBUTES.STATUS: "Not Installed",
                    ALERT_ATTRIBUTES.NAME: "Fan Module 4",
                    ALERT_ATTRIBUTES.ENCLOSURE_ID: 0,
                    ALERT_ATTRIBUTES.DURABLE_ID: "fan_module_0.4",
                    ALERT_ATTRIBUTES.FANS: [],
                    ALERT_ATTRIBUTES.HEALTH_REASON: "The fan module is not installed.",
                    ALERT_ATTRIBUTES.HEALTH: "Fault",
                    ALERT_ATTRIBUTES.LOCATION: "Enclosure 0 - Right",
                    ALERT_ATTRIBUTES.POSITION: "Indexed",
                    ALERT_ATTRIBUTES.HEALTH_RECOMMENDATION: "Install the missing fan module."
                },
                "alert_id": "15740759091a4e14bca51d46908ac3e9102605d560",
                "host_id": "s3node-host-1"
            }
        }
    }

    health_event = alert_parser.parse_event(json.dumps(TestAlert))

    if isinstance(health_event, HealthEvent):
        print(f"{EVENT_ATTRIBUTES.SOURCE} : {health_event.source}")
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
        print("Event alert parser test passed successfully")
    else:
        print("Event alert parser test failed")

    #Delete one key of the alert msg and validate the exception handling
    del TestAlert[ALERT_ATTRIBUTES.MESSAGE][ALERT_ATTRIBUTES.SENSOR_RESPONSE_TYPE][ALERT_ATTRIBUTES.ALERT_ID]
    msg_test = json.dumps(TestAlert)
    try:
        health_event = alert_parser.parse_event(json.dumps(TestAlert))
    except Exception as e:
        print(f"Negative test case passed successfully, caught err: {e}")
