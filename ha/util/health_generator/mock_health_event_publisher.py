#!/usr/bin/env python3

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

"""
Module helps in generating the mock health event and publishing it to the
message bus.

"""

import argparse
import sys
import pathlib

from cortx.utils.conf_store import Conf
from ha.util.conf_store import ConftStoreSearch

docker_env_file = '/.dockerenv'
_index = 'cortx'
cluster_config_file = '/etc/cortx/cluster.conf'
config_file_format = 'yaml'

def is_container_env() -> bool:
    """Returns True if environment is docker container else False."""
    docker_env_file_path = pathlib.Path(docker_env_file)
    if docker_env_file_path.exists():
        return True
    return False

def get_data_nodes(conf_store: ConftStoreSearch = None) -> list:
    """
    Fetches data node ids using HA wrapper class and displays the result.

    Args:
    conf_store: ConftStoreSearch object

    Returns: list of node ids
    """
    data_node_ids = conf_store.get_data_pods(_index)
    return data_node_ids

def get_server_nodes(conf_store: ConftStoreSearch = None) -> list:
    """
    Fetches server node ids using HA wrapper class and displays the result.

    Args:
    conf_store: ConftStoreSearch object

    Returns: list of node ids
    """
    server_node_ids = conf_store.get_server_pods(_index)
    return server_node_ids

def get_disks(args, conf_store: ConftStoreSearch = None) -> None:
    """
    Fetches disk ids using ConfStore search API and displays the result.

    Args:
    conf_store: ConftStoreSearch object
    node_id: machine_id value
    """
    # TODO: This is temporary code till this is avalable in HA.
    node_id = args.node_id
    num_of_cvgs = Conf.get(_index, f'node>{node_id}>storage>num_cvg')
    disk_ids = []
    for cvg in range(num_of_cvgs):
        num_of_data_disks = Conf.get(_index, f'node>{node_id}>storage>cvg[{cvg}]>devices>num_data')
        num_of_metadata_disks = Conf.get(_index, f'node>{node_id}>storage>cvg[{cvg}]>devices>num_metadata')
        [ disk_ids.append(Conf.get(_index, f'node>{node_id}>storage>cvg[{cvg}]>devices>data[{dt_disk}]')) for dt_disk in range(num_of_data_disks)]
        [ disk_ids.append(Conf.get(_index, f'node>{node_id}>storage>cvg[{cvg}]>devices>metadata[{md_disk}]')) for md_disk in range(num_of_metadata_disks)]
    print(disk_ids)

def get_cvgs(args, conf_store: ConftStoreSearch = None) -> None:
    """
    Fetches cvg ids using ConfStore search API and displays the result.

    Args:
    conf_store: ConftStoreSearch object
    node_id: machine_id value
    """
    node_id = args.node_id
    # TODO: This is temporary code till this is avalable in HA.
    cvg_count = Conf.get(_index, f'node>{node_id}>storage>num_cvg')
    print([Conf.get(_index, f'node>{node_id}>storage>cvg[{cvg}]>name') for cvg in range(cvg_count)])

def publish(args, conf_store: ConftStoreSearch = None) -> None:
    """
    publishes the message on the message bus.

    Args:
    conf_store: ConftStoreSearch object
    node_id: machine_id value
    config_file: config file path
    """
    print(f'inside publish, config file: {args.file}')

FUNCTION_MAP = {
                '-gdt' : get_data_nodes, '--get-data-nodes': get_data_nodes,
                '-gs' : get_server_nodes, '--get-server-nodes': get_server_nodes
                }

def get_args():
    """
    Configures the command line arguments.
    """
    my_parser = argparse.ArgumentParser(prog='health_event_publisher',
                                        usage='%(prog)s [options]',
                                        description='Helps in publishing the mock health event',
                                        epilog='Hope it is useful! :)')

    subparsers = my_parser.add_subparsers()

    my_parser.add_argument('-gdt', '--get-data-nodes', action='store_true', help='Get the list of data node ids')
    my_parser.add_argument('-gs', '--get-server-nodes', action='store_true', help='Get the list of server node ids')

    parser_publish = subparsers.add_parser('publish', help='Publish the message')
    parser_publish.add_argument('-f', '--file', action='store', help='imput config file', required=True)
    parser_publish.set_defaults(handler=publish)

    parser_disks = subparsers.add_parser('get-disks', help='Displys the Disk Ids assosciated with the Node')
    parser_disks.add_argument('-n', '--node-id', help='Node id for which disk id is required', required=True)
    parser_disks.set_defaults(handler=get_disks)

    parser_cvgs = subparsers.add_parser('get-cvgs', help='Displys the CVG Ids assosciated with the Node')
    parser_cvgs.add_argument('-n', '--node-id', help='Node id for which disk id is required', required=True)
    parser_cvgs.set_defaults(handler=get_cvgs)

    args = my_parser.parse_args()
    return args, my_parser


if __name__ == '__main__':
    if not is_container_env():
        sys.exit('Please use this script in containerized environment')
    option = None
    args, parser_obj = get_args()
    Conf.init()
    file_to_load = f'{config_file_format}://{cluster_config_file}'
    Conf.load(_index, file_to_load)
    _conf_store = ConftStoreSearch(conf_store_req=False)

    data_node_ids = get_data_nodes(conf_store=_conf_store)

    if len(sys.argv) > 1:
        option = sys.argv[1]
    else:
        parser_obj.print_help()
        sys.exit(0)

    if hasattr(args, 'handler'):
        if hasattr(args, 'node_id') and args.node_id not in data_node_ids:
            print('Please provide data node id to get disk and cvg id')
            sys.exit(1)
        args.handler(args, conf_store=_conf_store)
    else:
        print(FUNCTION_MAP[option](conf_store=_conf_store))

