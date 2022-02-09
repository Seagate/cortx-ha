#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

from ha.core.cluster.cluster_manager import CortxClusterManager

if __name__ == '__main__':
    cluster_manager = CortxClusterManager()
    # Complete health
    result = cluster_manager.get_system_health(element="cluster", depth=0)
    print(result)
    # Partial Health
    result = cluster_manager.get_system_health(element="cluster", depth=5)
    print(result)
    # Top 2 element health
    result = cluster_manager.get_system_health(element="cluster", depth=2)
    print(result)
