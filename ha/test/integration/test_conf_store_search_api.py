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

import os
import pathlib
import sys

from ha.util.conf_store import ConftStoreSearch
from cortx.utils.conf_store import Conf
from ha.core.config.config_manager import ConfigManager

sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))

if __name__ == "__main__":
    try:
        Conf.load("cortx", "yaml:///etc/cortx/cluster.conf")
        ConfigManager.init("test_conf_store_search_api")
        cluster_card  = ConftStoreSearch()

        print("\n******** Testing confstore search APIs for data and server PODs ********\n")
        cluster_card.set_cluster_cardinality("cortx")
        cc = cluster_card.get_cluster_cardinality()
        print(f"Following clsuter cardinality is set: {cc}")

        print("\n\n**************   Testing confstore APIs for CVG & disk  ***********\n")
        node_id = cluster_card._get_data_pods("cortx")[0]

        cvg_list = ConftStoreSearch.get_cvg_list("cortx", node_id)
        print(f"\nCVGs present under node {node_id} are : ", cvg_list)

        disk_list = ConftStoreSearch.get_disk_list("cortx", node_id)
        print(f"\nDisks present under node {node_id} are : ", disk_list)

        disk_list_per_cvg = ConftStoreSearch.get_disk_list_for_cvg("cortx", node_id, cvg_id=cvg_list[0])
        print(f"\nDisk present under node {node_id} & CVG {cvg_list[0]} are : ", disk_list_per_cvg)

    except Exception as e:
        print(f"Failed to test confstore search APIs, Error: {e}")
