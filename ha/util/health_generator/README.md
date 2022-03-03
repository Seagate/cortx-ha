# Introduction

This python script can be used for feeding mock health events to HA.

# Usage

usage: health_event_publisher [options]

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