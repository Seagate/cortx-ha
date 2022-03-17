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
        """
        Init method
        """
        print(f"Producer id: {producer_id}, message_type: {message_type}, partition: {partitions}")

    def publish(self, message: any):
        print(f"Publishing alert..\n{message}")
        return message


class MockAlert:

    @staticmethod
    def get_host_alert():
        # Alert without generation_id
        return { "event": {
                "header":{
                    "version":"1.0",
                    "timestamp":"112255",
                    "event_id":"11225568919c5ba8f88ad24cc18f632a75de115aca"
                },
                "payload":{
                    "source":"monitor",
                    "cluster_id":"None",
                    "site_id":"None",
                    "rack_id":"None",
                    "storageset_id":"None",
                    "node_id":"dummy.colo.seagate.com",
                    "resource_type":"host",
                    "resource_id":"dummy.colo.seagate.com",
                    "resource_status":"online",
                    "specific_info":{
                    }
                }
            }
        }

    @staticmethod
    def get_pod_alert():
        # Alert with generation_id
        return { "event":{
                "header":{
                    "version":"1.0",
                    "timestamp":"112233",
                    "event_id":"11223368911c9b81b8d3c84305a49c191e6a8c3bb5"
                },
                "payload":{
                    "source":"monitor",
                    "cluster_id":"None",
                    "site_id":"None",
                    "rack_id":"None",
                    "storageset_id":"None",
                    "node_id":"dummy0fff6f947e8aecc6a27a25b7329",
                    "resource_type":"node",
                    "resource_id":"dummy02fff6f947e8aecc6a27a25b7329",
                    "resource_status":"online",
                    "specific_info":{
                        "generation_id":"cortx-data-dummy0"
                    }
                }
            }
        }

    @staticmethod
    def toggle_status(alert):
        if alert["event"]["payload"]["resource_status"] == "online":
            alert["event"]["payload"]["resource_status"] = "offline"
        else:
            alert["event"]["payload"]["resource_status"] = "online"
        return alert



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

        host_alert = MockAlert.get_host_alert()
        pod_alert = MockAlert.get_pod_alert()

        # Check the alert is a new alert
        assert monitor._is_published_alert(host_alert) == False, "Failed to publish new alert"
        assert monitor._is_published_alert(pod_alert) == False, "Failed to publish new alert"

        # Publish
        mock_producer.publish(host_alert)
        mock_producer.publish(pod_alert)

        # Check the alert is already published
        assert monitor._is_published_alert(host_alert) == True, "Duplicate host alert is published"
        assert monitor._is_published_alert(pod_alert) == True, "Duplicate pod alert is published"

        # Check alert is not getting modified by is_published_alert validation
        actual_pod_alert = MockAlert.get_pod_alert()
        assert pod_alert == actual_pod_alert

        # Change pod status
        pod_alert = MockAlert.toggle_status(pod_alert)
        mock_producer.publish(pod_alert)

        # Check the alert is already published
        assert monitor._is_published_alert(pod_alert) == False, "Failed to publish new alert"
        print("Successfully verified the alert.")

        # we are exiting here so no needs to join the thread
        mock_producer._stop_alert_processing = True

    except Exception as e:
       print(f"Failed to verify the alert is already published or not. Error: {e}")
