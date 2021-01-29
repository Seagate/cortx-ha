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
 Description:       resource_agent resource agent
 ****************************************************************************
"""

import os
from cortx.utils.log import Log
from ha import const

class ResourceAgent:
    """
    Base class resource agent to monitor services
    """
    def monitor(self):
        """
        Monitor service
        """
        return const.OCF_ERR_UNIMPLEMENTED

    def start(self):
        """
        Start service
        """
        return const.OCF_ERR_UNIMPLEMENTED

    def stop(self):
        """
        Stop service
        """
        return const.OCF_ERR_UNIMPLEMENTED

    def metadata(self):
        pass

    def get_env(self) -> dict:
        """
        Get env variable and parameter provided by pacemaker
        """
        try:
            key = None
            ocf_env = {}
            env = os.environ
            for key in env.keys():
                if key.startswith("OCF_"):
                    ocf_env[key] = env[key]
            return ocf_env
        except Exception as e:
            Log.error(e)
            return {}

class CortxServiceRA(ResourceAgent):
    """
    Cortx Service RA
    """
    def __init__(self):
        """
        Initialize CortxServiceRA class.
        """
        super(CortxServiceRA, self).__init__()