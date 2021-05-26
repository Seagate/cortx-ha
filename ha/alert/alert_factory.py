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


class AlertFactory:

    @staticmethod
    def get_alert_monitor_instance(alert_type: str):

        alert_class = None

        from ha.alert.node_alert_monitor import NodeAlertMonitor
        from ha.alert.resource_alert_monitor import ResourceAlertMonitor

        # Mapping of REQUIRED_EVENTS to class
        alert_class_mapping = {"node": NodeAlertMonitor,
            "resource": ResourceAlertMonitor
        }

        try:
            alert_class = alert_class_mapping[alert_type]
        except Exception as e:
            Log.error(e)

        return alert_class
