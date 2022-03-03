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

import sys
import argparse
import errno
import json
import time

from cortx.utils.conf_store import Conf
from ha.util.conf_store import ConftStoreSearch
from ha.core.config.config_manager import ConfigManager
from ha import const
from ha.util.message_bus import MessageBus
from ha.fault_tolerance.event import Event
from ha.fault_tolerance.const import HEALTH_ATTRIBUTES

_index = 'cortx'
cluster_config_file = '/etc/cortx/cluster.conf'
config_file_format = 'yaml'
_events_key = 'events'
_source_key = 'source'
_node_id_key = 'node_id'
_resource_type_key = 'resource_type'
_resource_id_key = 'resource_id'
_resource_status_key = 'resource_status'
_specific_info_key = 'specific_info'
_delay_key = 'delay'

def get_data_nodes(conf_store: ConftStoreSearch = None) -> None:
    """
    Fetches data node ids using HA wrapper class and displays the result

    Args:
    conf_store: ConftStoreSearch object

    Returns: list of node ids
    """
    data_node_ids = conf_store.get_data_pods(_index)
    print(data_node_ids)

def get_server_nodes(conf_store: ConftStoreSearch = None) -> None:
    """
    Fetches server node ids using HA wrapper class and displays the result

    Args:
    conf_store: ConftStoreSearch object
    """
    server_node_ids = conf_store.get_server_pods(_index)
    print(server_node_ids)

def get_disks(args, conf_store: ConftStoreSearch = None) -> None:
    """
    Fetches disk ids using ConfStore search API and displays the result

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
    Fetches cvg ids using ConfStore search API and displays the result

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
    publishes the message on the message bus

    Args:
    conf_store: ConftStoreSearch object
    node_id: machine_id value
    config_file: config file path
    """
    try:
        with open(args.file, 'r') as fi:
            events_dict = json.load(fi)
            if _events_key in events_dict.keys():
                ConfigManager.init(None)
                MessageBus.init()
                message_type = Conf.get(const.HA_GLOBAL_INDEX, f'FAULT_TOLERANCE{const._DELIM}message_type')
                message_producer = MessageBus.get_producer("health_event_generator", message_type)
                cluster_id = Conf.get(const.HA_GLOBAL_INDEX, f'COMMON_CONFIG{const._DELIM}cluster_id')
                site_id = Conf.get(const.HA_GLOBAL_INDEX, f'COMMON_CONFIG{const._DELIM}site_id')
                rack_id = Conf.get(const.HA_GLOBAL_INDEX, f'COMMON_CONFIG{const._DELIM}rack_id')
                storageset_id = '1' # TODO: Read from config when available.
                for key, value in events_dict[_events_key].items():
                    resource_type = value[_resource_type_key]
                    if resource_type not in ['node', 'cvg', 'disk']:
                        raise Exception(f'Invalid resource_type: {resource_type}')
                    resource_status = value[_resource_status_key]
                    if resource_status not in ['recovering', 'online', 'failed', 'unknown', 'degraded', 'repairing', 'repaired', 'rebalancing', 'offline']:
                        raise Exception(f'Invalid resource_status: {resource_status}')
                    health_event = Event()
                    payload = {
                        HEALTH_ATTRIBUTES.SOURCE.value : value[_source_key],
                        HEALTH_ATTRIBUTES.CLUSTER_ID.value : cluster_id,
                        HEALTH_ATTRIBUTES.SITE_ID.value : site_id,
                        HEALTH_ATTRIBUTES.RACK_ID.value : rack_id,
                        HEALTH_ATTRIBUTES.STORAGESET_ID.value : storageset_id,
                        HEALTH_ATTRIBUTES.NODE_ID.value : value[_node_id_key],
                        HEALTH_ATTRIBUTES.RESOURCE_TYPE.value : resource_type,
                        HEALTH_ATTRIBUTES.RESOURCE_ID.value : value[_resource_id_key],
                        HEALTH_ATTRIBUTES.RESOURCE_STATUS.value : resource_status,
                        HEALTH_ATTRIBUTES.SPECIFIC_INFO.value : value[_specific_info_key]
                    }
                    health_event.set_payload(payload)
                    message_producer.publish(health_event.ret_dict())
                    if _delay_key in events_dict.keys():
                        time.sleep(events_dict[_delay_key])
    except Exception as err:
        sys.stderr.write(f"Health event generator failed. Error: {err}\n")
        return errno.EINVAL

def command_help(args, conf_store: ConftStoreSearch = None) -> None:
    """Handler function which displays help"""
    print(parser.parse_args([args.command, '--help']))


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

    parser_help = subparsers.add_parser('help', help='see `help -h`')
    parser_help.add_argument('command', help='command name which help is shown')
    parser_help.set_defaults(handler=command_help)

    args = my_parser.parse_args()
    return args, my_parser

if __name__ == '__main__':
    option = None
    args, parser_obj = get_args()
    Conf.init()
    file_to_load = f'{config_file_format}://{cluster_config_file}'
    Conf.load(_index, file_to_load)
    _conf_store = ConftStoreSearch(conf_store_req=False)

    if len(sys.argv) > 1:
        option = sys.argv[1]
    else:
        parser_obj.print_help()
        sys.exit(0)

    if hasattr(args, 'handler'):
        args.handler(args, conf_store=_conf_store)
    else:
        FUNCTION_MAP[option](conf_store=_conf_store)