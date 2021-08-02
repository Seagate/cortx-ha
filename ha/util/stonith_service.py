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

# Note: This class is used to bind different type of controller together.
# Other controller like node, cluster, storageset, service inheriting
# from this class.


class StonithService:
    """ Generic Stonith service class """
    def __init__(self):
        """
        Initialize Stonith service class.
        """
        pass

    def power_off(self, nodeid: str):
        """
        Power OFF node with nodeid

        Args:
            nodeid (str): Node ID from cluster nodes.
        """
        pass

    def power_on(self, nodeid: str):
        """
        Power ON node with nodeid

        Args:
            nodeid (str): Node ID from cluster nodes.
        """
        pass
