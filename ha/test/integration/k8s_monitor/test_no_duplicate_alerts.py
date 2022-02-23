#!/usr/bin/env python3

# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
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
import pathlib
import sys

sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))

from ha.monitor.k8s.object_monitor import ObjectMonitor
from ha.core.config.config_manager import ConfigManager


class MockProducer:

    def __init__(self, producer_id: str, message_type: str, partitions: int):
       print(f"Producer id: {producer_id}, message_type: {message_type}, partition: {partitions}")

    def publish(self, message: any):
        print(f"Publishing alert..\n{message.to_dict()}")
        return message


class MockAlert:

    alert = {
        '_resource_type': 'node',
        '_resource_name': '0000759b5d544cad8ea8cc6ee8ef0000',
        '_alert_type': 'online',
        '_k8s_container': None,
        '_generation_id': 'cortx-data-dummy',
        '_node': 'dummy-host.colo.seagate.com',
        '_is_status': True,
        '_timestamp': '1645601710'}

    @staticmethod
    def to_dict():
        return MockAlert.alert


if __name__ == "__main__":
    print("******** Testing K8s Not Publishing Duplicate Alerts ********")
    try:
        ConfigManager.init("test_k8s_resource_monitor")

        pod_labels =  ['cortx-data', 'cortx-server']
        pod_label_str = ', '.join(pod_label for pod_label in pod_labels)

        kwargs = {'pretty': True}
        kwargs['label_selector'] = f'name in ({pod_label_str})'

        #  Setting mock producer to publish
        mock_producer = MockProducer("mock_producer", "mock_message", 1)

        monitor = ObjectMonitor(mock_producer, 'pod', **kwargs)

        alert = MockAlert()

        # Check the alert is a new alert
        assert monitor._is_published_alert(alert) == False

        # Publish
        mock_producer.publish(alert)

        # Check the alert is already published
        assert monitor._is_published_alert(alert) == True, "Duplicate alert is published"
        print("Successfully verified the alert.")

        # we are exiting here so no needs to join the thread
        mock_producer._stop_alert_processing = True

    except Exception as e:
       print(f"Failed to verify the alert is already published or not. Error: {e}")
