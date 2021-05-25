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
import traceback
from string import Template

# Test case for iem filter
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))
    try:
        from cortx.utils.conf_store.conf_store import Conf
        from ha import const
        from ha.core.config.config_manager import ConfigManager
        from ha.core.event_analyzer.filter.filter import IEMFilter

        ConfigManager.init("test_iem_filter")
        IEMFilter = IEMFilter()
        print("********IEM Filter********")
        resource_type = "iem"
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

        Expected_result = False
        filter_type = Conf.get(const.ALERT_FILTER_INDEX, "iem.filter_type")
        components_types_list = Conf.get(const.ALERT_FILTER_INDEX, "iem.components")
        modules_dict = Conf.get(const.ALERT_FILTER_INDEX, "iem.modules")

        msg_type = TestMsg['sensor_response_type']
        _component_type = msg_type['specific_info']['component']
        _module_type = msg_type['specific_info']['module']

        if "actuator_response_type" not in TestMsg.keys():
            if filter_type == const.INCLUSION:
                if _component_type in components_types_list and _module_type in modules_dict.get(_component_type):
                    Expected_result = True
            elif filter_type == const.EXCLUSION:
                if _component_type not in components_types_list or _module_type not in modules_dict.get(
                        _component_type):
                    Expected_result = True
            else:
                print("Invalid filter type")

        if Expected_result == IEMFilter.filter_event(json.dumps(TestMsg)):
            print(Expected_result)
            print("IEM filter test pass successfully")
        else:
            print("IEM filter test failed")

    except Exception as e:
        print(f"{traceback.format_exc()}, {e}")
