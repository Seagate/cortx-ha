# Introduction

This python script can be used for feeding mock health events to HA.

# Usage

usage: ./mock_health_event_publisher.py [options]

Helps in publishing the mock health event

positional arguments:
  {publish,get-disks,get-cvgs,help}
    publish             Publish the health message
    get-disks           Displys the Disk Ids assosciated with the Node
    get-cvgs            Displys the CVG Ids assosciated with the Node
    help                see `help -h`

optional arguments:
  -h, --help            show this help message and exit
  -gdt, --get-data-nodes
                        Get the list of data node ids
  -gs, --get-server-nodes
                        Get the list of server node ids

Examples:
[root@cortx-ha-headless-svc /]# ./mock_health_event_publisher.py -gs
['658d34feae294a6197ec9f309dc846ef', '6b02f685e28e42ad92f1ebb434880ba8', '91c189443a6f48fcb395f9f9cac5447f']

[root@cortx-ha-headless-svc /]# ./mock_health_event_publisher.py -gdt
['6137d2e098354433a3b743ccc7737577', 'c6f34f1f5d144c4ba96463c304257ee8', 'fa583cf2324c49ec88d5557e6cdbd24a']

[root@cortx-ha-headless-svc /]# ./mock_health_event_publisher.py publish -f config.json
Publishing health event {'event': {'header': {'version': '1.0', 'timestamp': '1646628899', 'event_id': '1646628899df6b3f53931b4a209cea0da3a92d00ec'}, 'payload': {'source': 'hare', 'cluster_id': '30a58c57a8ca4c2abd55ba857bf5f026', 'site_id': '1', 'rack_id': '1', 'storageset_id': '1', 'node_id': '658d34feae294a6197ec9f309dc846ef', 'resource_type': 'node', 'resource_id': '658d34feae294a6197ec9f309dc846ef', 'resource_status': 'online', 'specific_info': {}}}}

# Config file

The config file is a json file with following format:

{
    "events": {
        "1": { # Any key
            "source": "hare", # Source of the event, monitor, ha, hare, etc.
            "node_id": "xxxx", # Node id fetched with -gdt/-gs arguments above.
            "resource_type": "node", # Resource type, node, cvg, disk, etc.
            "resource_id": "xxxx", # Resource id fetched with -gdt/-gs/get-cvgs/get-disks options above.
            "resource_status": "online", # Resource status, recovering, online, failed, unknown, degraded, repairing, repaired, rebalancing, offline, etc.
            "specific_info": {} # Key-value pairs e.g. "generation_id": "xxxx"
        },
         # Repeat the dictionary above with specific values if multiple events to be sent.
    },
    "delay": xxxx # If present this will add delay of specified seconds between the events.
}

# Restrictions
1. This script needs to be executed inside HA container.