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

import json
import time

from cortx.utils.message_bus import MessageBusAdmin
from cortx.utils.message_bus.error import MessageBusError
from cortx.utils.message_bus import MessageProducer

if __name__ == '__main__':
    try:
        admin = MessageBusAdmin(admin_id="admin")
        admin.register_message_type(message_types=["alerts"], partitions=1)
    except MessageBusError as e:
        print("\n\n\n\n" + e.desc + "\n\n\n\n")
        if "ALREADY_EXISTS" not in e.desc:
            raise e

    message_list = [json.dumps({"username": "sspl-ll", "description": "Seagate Storage Platform Library - Sensor Response", "title": "SSPL Sensor Response", "expires": 3600, "signature": "None", "time": "1621581798", "message": {"sspl_ll_msg_header": {"schema_version": "1.0.0", "sspl_version": "2.0.0", "msg_version": "1.0.0"}, "sensor_response_type": {"info": {"event_time": "1621581795", "resource_id": "iem", "resource_type": "iem", "description": "The cluster has lost ssc-vm-4455.colo.seagate.com server. System is running in degraded mode. For more information refer the Troubleshooting guide. Extra Info: host=ssc-vm-4455.colo.seagate.com; status=standby;", "impact": "NA", "recommendation": "NA", "site_id": "1", "node_id": "0", "rack_id": "1", "cluster_id": "e7106e74-828b-4b46-b319-d3594f39fb1f"}, "alert_type": "get", "severity": "warning", "specific_info": {"source": "Software", "component": "ha", "module": "NodeFailure", "event": "The cluster has lost one server. System is running in degraded mode.", "IEC": "WS0080010001"}, "alert_id": "16215817982ac7b67a94584377a060ffaca0b56cf8", "host_id": "srvnode-1.mgmt.public"}}})]
    producer = MessageProducer(producer_id="sspl-sensor", message_type="alerts", method="sync")
    producer.send(message_list)
    #for i in range(0, 1000):
    #    print(f"count {str(i)}")
    #    message_list = [json.dumps({"username": f"sspl-ll{str(i)}"})]
    #    producer.send(message_list)
    #    time.sleep(5)
    print("Message send")