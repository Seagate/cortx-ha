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

# Test case for Cluster management
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))
    from ha.core.cluster.cluster_manager import CortxClusterManager
    import traceback
    try:
        cm = CortxClusterManager()
        print(cm.controller_list)
        print("")
        print("********cluster controller*********")
        print(cm.cluster_controller.start())
        print(cm.cluster_controller.stop())
        print(cm.cluster_controller.status())
        print(cm.cluster_controller.standby())
        print(cm.cluster_controller.active())
        print(cm.cluster_controller.node_list())
        print(cm.cluster_controller.storageset_list())
        print(cm.cluster_controller.service_list())
        print(cm.cluster_controller.add_node("srvnode-1"))
        print(cm.cluster_controller.add_storageset("sr-1"))
        # node controller
        print("")
        print("********node controller*********")
        print(cm.node_controller.start("srvnode-1"))
        print(cm.node_controller.stop("srvnode-1"))
        print(cm.node_controller.status("srvnode-1"))
        print(cm.node_controller.standby("srvnode-1"))
        print(cm.node_controller.active("srvnode-1"))
        print("")
        print("********service controller*********")
        print(cm.service_controller.start("csm-agent","srvnode-1"))
        print(cm.service_controller.stop("csm-agent","srvnode-1"))
        print(cm.service_controller.status("csm-agent","srvnode-1"))
        print("")
        print("********storageset controller*********")
        print(cm.storageset_controller.start("st-1"))
        print(cm.storageset_controller.stop("st-1"))
        print(cm.storageset_controller.status("st-1"))
    except Exception as e:
        print(f"{traceback.format_exc()}, {e}")