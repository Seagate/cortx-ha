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
import pathlib
import sys
import time

sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))

from ha.monitor.k8s.object_monitor import ObjectMonitor

class MockProducer:

    def __init__(self, producer_id: str, message_type: str, partitions: int):
       print(f"Producer id: {producer_id}, message_type: {message_type}, partition: {partitions}")
       self.is_publish = False

    def publish(self, message: any):
        print("Test call: mocking publish event.")
        print(message)
        self.is_publish = True


if __name__ == "__main__":
    print("******** Testing K8s Event Parsing ********")
    try:
        pod_labels =  ['cortx-data', 'cortx-server']
        pod_label_str = ', '.join(pod_label for pod_label in pod_labels)

        kwargs = {'pretty': True}

        kwargs['label_selector'] = f'name in ({pod_label_str})'
        pod_thread = ObjectMonitor('pod', **kwargs)

        #  Setting mock producer to publish
        mock_producer = MockProducer("mock_producer", "mock_message", 1)
        pod_thread._producer = mock_producer

        # setting demon so on existing the main thread this thread will be exit
        pod_thread.daemon = True
        pod_thread.start()

        # wait for 30 seconds and check if publish is done
        # if done then exit.
        for count in range(0, 30):
            time.sleep(1)
            if mock_producer.is_publish:
                break

        # we are exiting here so no needs to join the thread
        sys.exit()

    except Exception as e:
        print(f"Failed to run K8s Event Parsing test, Error: {e}")
