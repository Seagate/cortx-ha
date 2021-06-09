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

import os
import sys
import pathlib

# Test case for alert filter
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))
    from ha.core.config.config_manager import ConfigManager
    from ha.alert.filter import AlertEventFilter
    import traceback

    try:
        test_pass = False
        ConfigManager.init("test_alert_event_filter")
        alert_event_filter = AlertEventFilter()
        print("********Alert Event Filter********")
        TestEvent = {'CRM_notify_kind': 'node', 'CRM_notify_node': 'srvnode-3.data.private', 'CRM_alert_nodeid': '3',
                     'CRM_notify_node_sequence': '167', 'CRM_notify_recipient': 'syslog',
                     'CRM_notify_timestamp': '05:04:48.309814', 'CRM_alert_desc': 'lost', 'CRM_alert_kind': 'node',
                     'CRM_alert_node': 'srvnode-3.data.private', 'CRM_notify_version': '1.1.23',
                     'CRM_notify_nodeid': '3', 'CRM_alert_recipient': 'syslog',
                     'CRM_alert_timestamp': '05:04:48.309814', 'CRM_alert_node_sequence': '167',
                     'CRM_alert_version': '1.1.23', 'CRM_notify_desc': 'lost'}
        alert_event_filter.initialize_crm(TestEvent)

        expected_module = "node"
        expected_operations = ["lost", "member"]

        alert_event_module, alert_event_type = alert_event_filter.filter_event()

        if expected_module == alert_event_module and alert_event_type in expected_operations:
            test_pass = True

        if test_pass:
            print("Alert event filter test pass successfully")
        else:
            print("Alert event filter test failed")

    except Exception as e:
        print(f"{traceback.format_exc()}, {e}")
