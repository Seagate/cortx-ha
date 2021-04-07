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
    from cortx.utils.conf_store.conf_store import Conf
    from ha import const
    from ha.core.config.config_manager import ConfigManager
    from ha.core.event_analyzer.filter.filter import AlertFilter
    import traceback
    try:
        ConfigManager.init("test_alert_filter")
        AlertFilter = AlertFilter()
        print("********Alert Filter********")
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

        Expected_result = False
        filter_type = Conf.get(const.ALERT_FILTER_INDEX, "alert.filter_type")
        resource_types_list = Conf.get(const.ALERT_FILTER_INDEX, "alert.resource_type")

        if filter_type == const.INCLUSION:
            if resource_type in resource_types_list:
                Expected_result = True
        elif filter_type == const.EXCLUSION:
            if resource_type not in resource_types_list:
                Expected_result = True
        else:
            print("Invalid filter type")

        if Expected_result == AlertFilter.filter_event(json.dumps(TestMsg)):
            print("Alert filter test pass successfully")
        else:
            print("Alert filter test failed")

    except Exception as e:
        print(f"{traceback.format_exc()}, {e}")
