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
 Description:       Hare plugin to provide Hare utility and interfaces.
 ****************************************************************************
"""

import json
from cortx.utils.log import Log
from ha import const

class Hare:

    @staticmethod
    def get_fid(service_name: str, node_id: str, instance_id: int) -> str:
        """
        Get Fid from hare mapping file for hare services.

        Args:
            service_name ([str]): Service name.
            node_id ([str]): Node name for fid instance.
            instance_id ([int]): Instance id for service.

        Returns:
            str: Return fid for hare service.
        """
        with open(const.HARE_FID_MAPPING_FILE) as fi:
            fid_schema = json.load(fi)
        fid: str = ""
        if service_name == "s3service":
            fid = Hare._get_s3server_fid(fid_schema, service_name, node_id, instance_id)
        else:
            fid = Hare._get_motr_fid(fid_schema, service_name, node_id, instance_id)
        Log.debug(f"Map ({service_name}, {node_id}, {instance_id}) to {fid}")
        return fid

    @staticmethod
    def _get_motr_fid(fid_schema: dict, service_name: str, node_id: str, instance_id: int) -> str:
        """
        Get Fid from hare mapping file for motr services.

        Args:
            fid_schema ([dict]): Schema for hare services fid.
            service_name ([str]): Service name.
            node_id ([str]): Node name for fid instance.
            instance_id ([int]): Instance id for service.

        Returns:
            str: Return fid for motr
        """
        motr_mapping: list = []
        count: int = 0
        for service in fid_schema["services"]:
            if service["name"] == service_name:
                count += 1
                motr_mapping.append(service["checks"][0]["args"][2])
        motr_mapping.sort()
        fid: str = motr_mapping[instance_id - 1]
        return fid

    @staticmethod
    def _get_s3server_fid(fid_schema: dict, service_name: str, node_id: str, instance_id: int) -> str:
        """
        Get Fid from hare mapping file for motr services.

        Args:
            fid_schema ([dict]): Schema for hare services fid.
            service_name ([str]): Service name.
            node_id ([str]): Node name for fid instance.
            instance_id ([int]): Instance id for service.

        Returns:
            str: Return fid for s3service
        """
        s3service_li: list = []
        fid: str = ""
        for service in fid_schema["services"]:
            clone_id = int(service["port"])
            if service["name"] == service_name:
                service_fid = service["checks"][0]["args"][2]
                fid = service_fid.split("@")[1]
                s3service_li.append(fid)
        s3service_li.sort()
        return s3service_li[instance_id - 1]