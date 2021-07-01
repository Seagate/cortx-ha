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

from enum import Enum

class TIMEOUT_ACTION(Enum):
    START = "start"
    STOP = "stop"
    MONITOR = "monitor"

class RESOURCE(Enum):
    HAX = "hax"
    MOTR_CONFD = "motr-confd"
    MOTR_IOS = "motr-ios"
    MOTR_FREE_SPACE_MON = "motr-free-space-mon"
    S3_SERVER = "s3server"
    S3_BACK_CONS = "s3backcons"
    S3_BACK_PROD = "s3backprod"
    S3AUTH = "s3auth"
    HAPROXY = "haproxy"
    SSPL_LL = "sspl-ll"
    MGMT_VIP = "mgmt-vip"
    CSM_AGENT = "csm-agent"
    CSM_WEB = "csm-web"
    KIBANA = "kibana"
    EVENT_ANALYZER = "event_analyzer"
    SRV_COUNTER = "srv_counter"
    M_BUS_REST = "mbus_rest"
    UDS = "uds"

BUFFER_TIMEOUT=5

TIMEOUT_MAP = {
    # Default systemd timeout is 90sec and non systemd resource timeout is 60sec.
    TIMEOUT_ACTION.START.value: {
        RESOURCE.HAX.value: "90",
        RESOURCE.MOTR_CONFD.value: "90",
        RESOURCE.MOTR_IOS.value: "90",
        RESOURCE.MOTR_FREE_SPACE_MON.value: "90",
        RESOURCE.S3_SERVER.value: "90",
        RESOURCE.S3_BACK_CONS.value: "90",
        RESOURCE.S3_BACK_PROD.value: "90",
        RESOURCE.S3AUTH.value: "90",
        RESOURCE.HAPROXY.value: "90",
        RESOURCE.SSPL_LL.value: "90",
        RESOURCE.MGMT_VIP.value: "60",
        RESOURCE.CSM_AGENT.value: "90",
        RESOURCE.CSM_WEB.value: "90",
        RESOURCE.KIBANA.value: "90",
        RESOURCE.EVENT_ANALYZER.value: "90",
        RESOURCE.SRV_COUNTER.value: "60",
        RESOURCE.M_BUS_REST.value: "90",
        RESOURCE.UDS.value: "90"
    },
    TIMEOUT_ACTION.STOP.value: {
        RESOURCE.HAX.value: "90",
        RESOURCE.MOTR_CONFD.value: "90",
        RESOURCE.MOTR_IOS.value: "90",
        RESOURCE.MOTR_FREE_SPACE_MON.value: "90",
        RESOURCE.S3_SERVER.value: "90",
        RESOURCE.S3_BACK_CONS.value: "90",
        RESOURCE.S3_BACK_PROD.value: "90",
        RESOURCE.S3AUTH.value: "90",
        RESOURCE.HAPROXY.value: "90",
        RESOURCE.SSPL_LL.value: "90",
        RESOURCE.MGMT_VIP.value: "60",
        RESOURCE.CSM_AGENT.value: "90",
        RESOURCE.CSM_WEB.value: "90",
        RESOURCE.KIBANA.value: "90",
        RESOURCE.EVENT_ANALYZER.value: "90",
        RESOURCE.SRV_COUNTER.value: "60",
        RESOURCE.M_BUS_REST.value: "90",
        RESOURCE.UDS.value: "90"
    }
}
