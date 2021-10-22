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


from ha.monitor.k8s.object_monitor import ObjectMonitor

if __name__ == "__main__":
    object_threads = []
    # Read I/O pod selector label from ha.conf . Will be received from provisioner confstore 
    # provisioner needs to be informed to add it in confstore  (to be added there )
    pod_label = 'test-replicated'

    kwargs = {'pretty': True}
    # Change to multiprocessing
    node_thread = ObjectMonitor('node', **kwargs)
    kwargs['label_selector'] = f'app={pod_label}'
    pod_thread = ObjectMonitor('pod', **kwargs)

    pod_thread.start()
    node_thread.start()

    object_threads.append(pod_thread)
    object_threads.append(node_thread)

    for a_thread in object_threads:
        a_thread.join()

    print("All threads have exited.")
