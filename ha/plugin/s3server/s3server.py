#!/usr/bin/env python3

# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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
 Description:       S3server plugin to provide S3server utility and interfaces.
 ****************************************************************************
"""

import json
from cortx.utils.log import Log
from ha import const

class S3server:

    @staticmethod
    def getFid(service_name: str, node_id: str, instance_id: int) -> str:
        """
        Get Fid from hare mapping file for motr services.

        Args:
            service_name ([str]): Service name.
            node_id ([str]): Node name for fid instance.
            instance_id ([int]): Instance id for service.

        Returns:
            str: Return fid for s3service
        """
        try:
            with open(const.FID_MAPPING_FILE) as fi:
                fid_service_mapping = json.load(fi)
            clone_id: int = 0
            fid: str = ""
            for service in fid_service_mapping["services"]:
                clone_id = int(service["port"])
                if service["name"] == service_name and clone_id == instance_id:
                    service_fid = service["checks"][0]["args"][2]
                    fid = service_fid.split("@")[1]
                    break
            Log.debug(f"Map ({service_name}, {node_id}, {instance_id}) to {fid}")
            return fid
        except Exception as e:
            Log.error(f"Failed to get fid for ({service_name}, {node_id}, \
                {instance_id}). Error: {e}")
            return None