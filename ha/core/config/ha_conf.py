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

from cortx.utils.conf_store.conf_store import Conf

from ha import const

class HAConf:
    """
    Central HA configuration for all get/set conf interface.
    """
    @staticmethod
    def initalize(cluster_confstore):
        """
        Create singleton class.

        Args:
            cluster_confstore (ConsulConfStore): Consul conf store.
        """
        self._cluster_confstore = cluster_confstore

    @staticmethod
    def get_major_version():
        """
        Get product version

        Returns:
            [int]: Return version
        """
        version = Conf.get(const.HA_GLOBAL_INDEX, "VERSION.version")
        major_version = version.split('.')
        return major_version[0]
