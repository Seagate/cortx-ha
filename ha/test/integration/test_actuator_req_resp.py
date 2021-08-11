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

import sys
import json
import traceback

from cortx.utils.message_bus import MessageConsumer
from cortx.utils.message_bus import MessageBusAdmin
from cortx.utils.message_bus.error import MessageBusError
from cortx.utils.message_bus import MessageProducer


def send_response(msg):
    try:
        admin = MessageBusAdmin(admin_id="admin")
        admin.register_message_type(message_types=["alerts"], partitions=1)
        print("sending response now")
    except MessageBusError as e:
        print("\n\n\n\n" + e.desc + "\n\n\n\n")
        if "ALREADY_EXISTS" not in e.desc:
            raise e

    # Get uuid from request and replace in response
    success_dict = {"title": "SSPL Actuator Response","description": "Seagate Storage Platform Library - Actuator Response", "username": "sspl-ll","signature": "None","time": "1628060172","expires": 3600,"message": {"sspl_ll_msg_header": {"schema_version": "1.0.0","sspl_version": "2.0.0","msg_version": "1.0.0","uuid": "16476007-a739-4785-b5c7-f3de189cdf9d"},"actuator_response_type": {"host_id": "ssc-vm-rhev4-0180.colo.seagate.com","alert_type": "control:shutdown","alert_id": "16280601712397710d3c4f40d38e1a77cee3a4c097","severity": "informational","info": {"resource_type": "enclosure:fru:controller","resource_id": "*","event_time": "1628060171","site_id": "DC01","node_id": "SN01","rack_id": "RC01","cluster_id": "CC01"},"specific_info": {"message": "Shutdown request Successful","command": "shutdown both"}}}}

    #fail_dict = {"title": "SSPL Actuator Response","description": "Seagate Storage Platform Library - Actuator Response", "username": "sspl-ll","signature": "None","time": "1628060172","expires": 3600,"message": {"sspl_ll_msg_header": {"schema_version": "1.0.0","sspl_version": "2.0.0","msg_version": "1.0.0","uuid": "16476007-a739-4785-b5c7-f3de189cdf9d"},"actuator_response_type": {"host_id": "ssc-vm-rhev4-0180.colo.seagate.com","alert_type": "control:shutdown","alert_id": "16280601712397710d3c4f40d38e1a77cee3a4c097","severity": "warning","info": {"resource_type": "enclosure:fru:controller","resource_id": "*","event_time": "1628060171","site_id": "DC01","node_id": "SN01","rack_id": "RC01","cluster_id": "CC01"},"specific_info": {"message": "Shutdown request Failed","command": "shutdown both"}}}}

    req_json = json.loads(msg)

    # Send success /fail resp based on test reqmt
    resp = success_dict
    #resp = fail_dict
    resp["message"]["sspl_ll_msg_header"]["uuid"] = req_json["message"]["sspl_ll_msg_header"]["uuid"]
    print(f"uuid is {resp['message']['sspl_ll_msg_header']['uuid']}")
    resp_msg = [json.dumps(resp)]

    producer = MessageProducer(producer_id="sspl-sensor", message_type="alerts", method="sync")
    producer.send(resp_msg)
    print(f"Response is sent: \n {resp_msg} \n")


if __name__ == '__main__':
    consumer = MessageConsumer(consumer_id="1",
                                consumer_group='actualtor_req_manager',
                                message_types=["requests"],
                                auto_ack=False, offset='earliest')

    while True:
        try:
            print("In receiver")
            message = consumer.receive(timeout=0)
            #consumer.ack()
            #continue

            msg = json.loads(message.decode('utf-8'))
            print(f"Got a request: \n {msg} \n")
            consumer.ack()

            # Create a new sender for topic requests
            send_response(json.dumps(msg))

        except Exception as e:
            print(e)
            print(traceback.format_exe())
            sys.exit(0)

