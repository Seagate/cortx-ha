import sys
import argparse

from cortx.utils.conf_store import Conf
from ha.util.conf_store import ConftStoreSearch


_index = 'cortx'

def get_data_nodes(conf_store: ConftStoreSearch):
    data_node_ids = conf_store.get_data_pods(_index)
    print(data_node_ids)

def get_server_nodes(conf_store: ConftStoreSearch):
    server_node_ids = conf_store.get_data_pods(_index)
    print(data_node_ids)

def get_disks(conf_store: ConftStoreSearch):
    print('inside get disks')

def get_cvgs(conf_store: ConftStoreSearch):
    print('inside get cvgs')

FUNCTION_MAP = {'-gdt' : get_data_nodes}

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
    Conf.load(_index, 'yaml:///etc/cortx/cluster.conf')
    _conf_store = ConftStoreSearch(conf_store_req=False)
    option = sys.argv[1]
    FUNCTION_MAP[option](_conf_store)
