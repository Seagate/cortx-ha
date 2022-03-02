# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
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


import sys
import argparse

from cortx.utils.conf_store import Conf
from ha.util.conf_store import ConftStoreSearch


_index = 'cortx'
cluster_config_file = '/etc/cortx/cluster.conf'
config_file_format = 'yaml'

def get_data_nodes(conf_store: ConftStoreSearch = None, node_id: str = None) -> list:
    """
    Fetches data node ids using HA wrapper class and displays the result

    Args:
    conf_store: ConftStoreSearch object

    Returns: list of node ids
    """
    data_node_ids = conf_store.get_data_pods(_index)
    return data_node_ids

def get_server_nodes(conf_store: ConftStoreSearch = None, node_id: str = None) -> None:
    """
    Fetches server node ids using HA wrapper class and displays the result

    Args:
    conf_store: ConftStoreSearch object
    """
    server_node_ids = conf_store.get_server_pods(_index)
    print(server_node_ids)

def get_disks(conf_store: ConftStoreSearch, node_id: str) -> None:
    """
    Fetches disk ids using ConfStore search API and displays the result

    Args:
    conf_store: ConftStoreSearch object
    node_id: machine_id value
    """
    # TODO: This is temporary code till this is avalable in HA.
    num_of_cvgs = Conf.get(_index, f'node>{node_id}>storage>num_cvg')
    disk_ids = []
    for cvg in range(num_of_cvgs):
        num_of_data_disks = Conf.get(_index, f'node>{node_id}>storage>cvg[{cvg}]>devices>num_data')
        num_of_metadata_disks = Conf.get(_index, f'node>{node_id}>storage>cvg[{cvg}]>devices>num_metadata')
        [ disk_ids.append(Conf.get(_index, f'node>{node_id}>storage>cvg[{cvg}]>devices>data[{dt_disk}]')) for dt_disk in range(num_of_data_disks)]
        [ disk_ids.append(Conf.get(_index, f'node>{node_id}>storage>cvg[{cvg}]>devices>metadata[{md_disk}]')) for md_disk in range(num_of_metadata_disks)]
    print(disk_ids)

def get_cvgs(conf_store: ConftStoreSearch, node_id: str) -> None:
    """
    Fetches cvg ids using ConfStore search API and displays the result

    Args:
    conf_store: ConftStoreSearch object
    node_id: machine_id value
    """
    # TODO: This is temporary code till this is avalable in HA.
    cvg_count = Conf.get(_index, f'node>{node_id}>storage>num_cvg')
    print([Conf.get(_index, f'node>{node_id}>storage>cvg[{cvg}]>name') for cvg in range(cvg_count)])

def publish(conf_store: ConftStoreSearch = None, node_id: str = None, config_file: str = None):
    print('inside publish')

FUNCTION_MAP = {
                '-gdt' : get_data_nodes, '--get-data-nodes': get_data_nodes,
                '-gs' : get_server_nodes, '--get-server-nodes': get_server_nodes,
                '-gd' : get_disks, '--get-disks': get_disks,
                '-gc' : get_cvgs, '--get-cvgs': get_cvgs,
                '-p' : publish, '--publish': publish
                }

my_parser = argparse.ArgumentParser(prog='health_event_publisher',
                                    usage='%(prog)s [options]',
                                    description='Helps in publishing the mock health event',
                                    epilog='Hope it is useful! :)')

get_options = my_parser.add_mutually_exclusive_group(required=True)
get_options.add_argument('-gd', '--get-disks', action='store_true', help='Get the DISK IDs')
get_options.add_argument('-gc', '--get-cvgs', action='store_true', help='Get the CVG IDs')
get_options.add_argument('-gdt', '--get-data-nodes', action='store_true', help='Get the data nodes')
get_options.add_argument('-gs', '--get-server-nodes', action='store_true', help='Get the server nodes')
get_options.add_argument('-p', '--publish', action='store_true', help='Publish the message')

my_parser.parse_args()

if __name__ == '__main__':
    Conf.init()
    file_to_load = f'{config_file_format}://{cluster_config_file}'
    Conf.load(_index, file_to_load)
    _conf_store = ConftStoreSearch(conf_store_req=False)
    # To fetch disk or cvg id, node id is required. So, one of the node_id
    # will be picked from the list which we will get from get_data_nodes function
    # and ids of disk and cvg assosciated with that node will be displayed
    node_ids = get_data_nodes(conf_store=_conf_store)
    option = sys.argv[1]
    if option == '-gdt' or option == '--get-data-nodes':
        print(node_ids)
    else:
        FUNCTION_MAP[option](conf_store=_conf_store, node_id=node_ids[0])
