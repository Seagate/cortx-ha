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


"""
 ****************************************************************************
 Description:       Provide cental configuration.
 ****************************************************************************
"""

from cortx.utils.log import Log
from cortx.utils.conf_store.conf_store import Conf

from ha import const

# TODO: redefine class as per config manager module design
class ConfigManager:
    """
    HA configuration to provide central ha configuration
    """
    # TODO: create separate function for log and conf file
    @staticmethod
    def init(log_name) -> None:
        """
        Initialize ha conf and log
        Args:
            log_name ([str]): service_name for log init.
        """
        Conf.init(delim='.')
        Conf.load(const.HA_GLOBAL_INDEX, f"yaml://{const.HA_CONFIG_FILE}")
        Conf.load(const.RESOURCE_GLOBAL_INDEX, f"json://{const.RESOURCE_SCHEMA}")
        log_path = Conf.get(const.HA_GLOBAL_INDEX, "LOG.path")
        log_level = Conf.get(const.HA_GLOBAL_INDEX, "LOG.level")
        Log.init(service_name=log_name, log_path=log_path, level=log_level)

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

    @staticmethod
    def load_controller_schema() -> None:
        """
        Load controller interface schema for cluster management.
        """
        Conf.load(const.CLUSTER_MANAGER_CONTROLLER_INDEX,
            f"json://{const.CLUSTER_MANAGER_CONTROLLER_SCHEMA}")
