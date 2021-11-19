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

import os
import json
from cortx.utils.log import Log
from ha.execute import SimpleCommand
from ha.core.error import CreateResourceError
from ha.core.error import CreateResourceConfigError
from ha.setup.setup_error import ConfigureStonithResourceError
from ha import const
from ha.setup.const import TIMEOUT_ACTION
from ha.setup.const import RESOURCE
from ha.setup.const import BUFFER_TIMEOUT
from ha.setup.const import TIMEOUT_MAP

"""
# List of resource
motr-free-space-mon
io_stack
    motr-confd-1
    hax
    motr-ios-<i>
    haproxy
    s3auth
    s3server-<i>
    s3backcons
    s3backprod
monitor
    sspl
management
    mgmt-vip
    kibana
    csm-agent
    csm-web
ha
    event_analyzer
    srv_counter
    health_monitor
"""

process = SimpleCommand()

def convert_to_sec(time_str: str) -> int:
    """
    Convert time to sec

    Args:
        time (str): Time in str format 1min 30s.

    Returns:
        int: Time in sec.
    """
    total_sec: int = 0
    times = time_str.split()
    for unit_time in times:
        if "m" in unit_time:
            total_sec += (int(unit_time.split("m")[0]) * 60)
        elif "s" in unit_time:
            total_sec += int(unit_time.split("s")[0])
        else:
            raise CreateResourceConfigError(f"Invalid unit {unit_time} for timestamp {time_str}")
    return total_sec

def get_systemd_timeout(systemd: str, action: str) -> int:
    """
    Get Stop timeout for systemd.

    Args:
        systemd (str): Service name.
        action (str): Systemd Action.

    Returns:
        int: Timeout in sec.
    """
    if action == TIMEOUT_ACTION.START.value:
        output, _, _ = process.run_cmd(f"systemctl show {systemd} -p TimeoutStartUSec")
    elif action == TIMEOUT_ACTION.STOP.value:
        output, _, _ = process.run_cmd(f"systemctl show {systemd} -p TimeoutStopUSec")
    else:
        raise CreateResourceConfigError(f"Invalid action {action} for systemd resource {systemd}")
    timeout = convert_to_sec(output.split("=")[1])
    return timeout

def get_res_timeout(resource: str, action: str, systemd: str = None) -> int:
    """
    Return resource timeout.

    Args:
        resource (str): resource name
        action (str): timeout action. (start/stop/monitor)

    Returns:
        int: timeout in sec
    """
    timeout = 0
    if systemd is None:
        timeout = int(TIMEOUT_MAP[action][resource]) + BUFFER_TIMEOUT
    else:
        timeout = get_systemd_timeout(systemd, action) + BUFFER_TIMEOUT
    Log.info(f"Timeout for {resource}:{systemd} {action} is {str(timeout)} sec.")
    return timeout

def cib_push(cib_xml):
    """Shortcut to avoid boilerplate pushing CIB file."""
    process.run_cmd(f"pcs cluster verify -V {cib_xml}")
    process.run_cmd(f"pcs cluster cib-push {cib_xml} --config")

def cib_get(cib_xml):
    """Generate CIB file using pcs."""
    process.run_cmd(f"pcs cluster cib {cib_xml}")
    return cib_xml

def change_pcs_default(cib_xml, push=False, **kwargs):
    """Modify pcs defaults here"""
    process.run_cmd(f"pcs -f {cib_xml} resource defaults resource-stickiness=1")
    if push:
        cib_push(cib_xml)

def hax(cib_xml, push=False, **kwargs):
    """Create resources that belong to hax and clone the group."""
    hax_start = str(get_res_timeout(RESOURCE.HAX.value, TIMEOUT_ACTION.START.value, "hare-hax"))
    hax_stop = str(get_res_timeout(RESOURCE.HAX.value, TIMEOUT_ACTION.STOP.value, "hare-hax"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.HAX.value} systemd:hare-hax \
        op start timeout={hax_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={hax_stop}s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone {RESOURCE.HAX.value}")
    if push:
        cib_push(cib_xml)

def motr_conf(cib_xml, push=False, **kwargs):
    """Create resources that belong to motr confd and clone the group."""
    # Use @AnyFid to get timeout for service
    confd_systemd = "m0d@AnyFid"
    confd_start = str(get_res_timeout(RESOURCE.MOTR_CONFD.value, TIMEOUT_ACTION.START.value, confd_systemd))
    confd_stop = str(get_res_timeout(RESOURCE.MOTR_CONFD.value, TIMEOUT_ACTION.STOP.value, confd_systemd))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.MOTR_CONFD.value}-1 ocf:seagate:dynamic_fid_service_ra \
        service=m0d fid_service_name=confd update_attrib=true \
        op start timeout={confd_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={confd_stop}s interval=0s")
    try:
        quorum_size = int(kwargs["node_count"])
        process.run_cmd(f"pcs -f {cib_xml} resource clone {RESOURCE.MOTR_CONFD.value}-1 interleave=true clone-min={quorum_size}")
    except Exception as e:
        raise CreateResourceConfigError(f"Invalid node_count. Error: {e}")

    # Constraint
    process.run_cmd(f"pcs -f {cib_xml} constraint order {RESOURCE.HAX.value}-clone then {RESOURCE.MOTR_CONFD.value}-1-clone")
    process.run_cmd(f"pcs -f {cib_xml} constraint colocation add {RESOURCE.MOTR_CONFD.value}-1-clone with {RESOURCE.HAX.value}-clone")

    if push:
        cib_push(cib_xml)

def get_ios_instances(**kwargs):
    if "ios_instances" in kwargs:
        ios_instances = int(kwargs["ios_instances"])
    else:
        ios_instances = 1

    return ios_instances

def motr(cib_xml, push=False, **kwargs):
    """Configure motr resource."""
    # Use @AnyFid to get timeout for service
    ios_systemd = "m0d@AnyFid"
    ios_start = str(get_res_timeout(RESOURCE.MOTR_IOS.value, TIMEOUT_ACTION.START.value, ios_systemd))
    ios_stop = str(get_res_timeout(RESOURCE.MOTR_IOS.value, TIMEOUT_ACTION.STOP.value, ios_systemd))
    ios_instances = get_ios_instances(**kwargs)

    for i in range(1, int(ios_instances)+1):
        process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.MOTR_IOS.value}-{i} ocf:seagate:dynamic_fid_service_ra \
            service=m0d fid_service_name=ioservice update_attrib=true \
            op start timeout={ios_start}s interval=0s \
            op monitor timeout=29s interval=30s \
            op stop timeout={ios_stop}s interval=0s")
        process.run_cmd(f"pcs -f {cib_xml} resource clone {RESOURCE.MOTR_IOS.value}-{i} interleave=true")

        # Constraint
        try:
            quorum_size = int(kwargs["node_count"])//2
            quorum_size += 1
            process.run_cmd(f"pcs -f {cib_xml} constraint location {RESOURCE.MOTR_IOS.value}-{i}-clone rule score=-INFINITY \
                    not_defined {RESOURCE.MOTR_CONFD.value}-count or {RESOURCE.MOTR_CONFD.value}-count lt integer {quorum_size}")
            process.run_cmd(f"pcs -f {cib_xml} constraint order {RESOURCE.HAX.value}-clone then {RESOURCE.MOTR_IOS.value}-{i}-clone")
            process.run_cmd(f"pcs -f {cib_xml} constraint colocation add {RESOURCE.MOTR_IOS.value}-{i}-clone with {RESOURCE.HAX.value}-clone")
            process.run_cmd(f"pcs -f {cib_xml} constraint order stop {RESOURCE.MOTR_IOS.value}-{i}-clone then stop {RESOURCE.MOTR_CONFD.value}-1-clone kind=Optional")
        except Exception as e:
            raise CreateResourceConfigError(f"Invalid node_count. Error: {e}")
    if push:
        cib_push(cib_xml)

def stop_constraint_on_motr_ios(resource_name, cib_xml, push=False, **kwargs):
    ios_instances = get_ios_instances(**kwargs)
    for i in range(1, int(ios_instances)+1):
        process.run_cmd(f"pcs -f {cib_xml} constraint order stop {resource_name} then stop {RESOURCE.MOTR_IOS.value}-{i}-clone kind=Optional")
    if push:
        cib_push(cib_xml)

def free_space_monitor(cib_xml, push=False, **kwargs):
    """Create free space monitor resource. 1 per cluster, no affinity."""
    free_space_start = str(get_res_timeout(RESOURCE.MOTR_FREE_SPACE_MON.value, TIMEOUT_ACTION.START.value, "motr-free-space-monitor"))
    free_space_stop = str(get_res_timeout(RESOURCE.MOTR_FREE_SPACE_MON.value, TIMEOUT_ACTION.STOP.value, "motr-free-space-monitor"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.MOTR_FREE_SPACE_MON.value} systemd:motr-free-space-monitor \
        op start timeout={free_space_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={free_space_stop}s interval=0s meta failure-timeout=300s")

    # Constraint
    process.run_cmd(f"pcs -f {cib_xml} constraint location {RESOURCE.MOTR_FREE_SPACE_MON.value} rule score=-INFINITY \
                    not_defined {RESOURCE.MOTR_IOS.value}-count or {RESOURCE.MOTR_IOS.value}-count lt integer 1")
    stop_constraint_on_motr_ios(RESOURCE.MOTR_FREE_SPACE_MON.value, cib_xml, push, **kwargs)
    if push:
        cib_push(cib_xml)

def get_s3servers_instances(**kwargs):
    try:
        instance = int(kwargs["s3_instances"])
        return instance
    except Exception as e:
        raise CreateResourceConfigError(f"Invalid s3 instance. Error: {e}")

def s3servers(cib_xml, push=False, **kwargs):
    """
    Create resources that belong to s3server group and clone the group.
    S3 background consumer is ordered after s3server and co-located with it.
    """
    # Use @AnyFid to get timeout for service
    s3server_systemd = "s3server@AnyFid"
    s3servers_start = str(get_res_timeout(RESOURCE.S3_SERVER.value, TIMEOUT_ACTION.START.value, s3server_systemd))
    s3servers_stop = str(get_res_timeout(RESOURCE.S3_SERVER.value, TIMEOUT_ACTION.STOP.value, s3server_systemd))
    instance = get_s3servers_instances(**kwargs)
    for i in range(1, int(instance)+1):
        process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.S3_SERVER.value}-{i} ocf:seagate:dynamic_fid_service_ra \
            service=s3server fid_service_name=s3server update_attrib=true \
            op start timeout={s3servers_start}s interval=0s \
            op monitor timeout=29s interval=30s \
            op stop timeout={s3servers_stop}s interval=0s")
        process.run_cmd(f"pcs -f {cib_xml} resource clone {RESOURCE.S3_SERVER.value}-{i} interleave=true")

        # Constraint
        process.run_cmd(f"pcs -f {cib_xml} constraint location {RESOURCE.S3_SERVER.value}-{i}-clone rule score=-INFINITY \
                        not_defined {RESOURCE.MOTR_IOS.value}-count or  {RESOURCE.MOTR_IOS.value}-count lt integer 1")
        process.run_cmd(f"pcs -f {cib_xml} constraint colocation add {RESOURCE.S3_SERVER.value}-{i}-clone with s3auth-clone")
        stop_constraint_on_motr_ios(f"{RESOURCE.S3_SERVER.value}-{i}-clone", cib_xml, push, **kwargs)
    if push:
        cib_push(cib_xml)

def stop_constraint_on_s3servers(resource_name, cib_xml, push=False, **kwargs):
    s3_instances = get_s3servers_instances(**kwargs)
    for i in range(1, int(s3_instances)+1):
        process.run_cmd(f"pcs -f {cib_xml} constraint order stop {resource_name} then stop s3server-{i}-clone kind=Optional")
    if push:
        cib_push(cib_xml)

def s3bc(cib_xml, push=False, **kwargs):
    """Create S3 background consumer."""
    s3bc_start = str(get_res_timeout(RESOURCE.S3_BACK_CONS.value, TIMEOUT_ACTION.START.value, "s3backgroundconsumer"))
    s3bc_stop = str(get_res_timeout(RESOURCE.S3_BACK_CONS.value, TIMEOUT_ACTION.STOP.value, "s3backgroundconsumer"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.S3_BACK_CONS.value} systemd:s3backgroundconsumer meta failure-timeout=300s \
        op start timeout={s3bc_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={s3bc_stop}s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone {RESOURCE.S3_BACK_CONS.value} interleave=true")

    # Constraint
    process.run_cmd(f"pcs -f {cib_xml} constraint location {RESOURCE.S3_BACK_CONS.value}-clone rule score=-INFINITY \
                    not_defined {RESOURCE.S3_SERVER.value}-count or {RESOURCE.S3_SERVER.value}-count lt integer 1")
    stop_constraint_on_s3servers(f"{RESOURCE.S3_BACK_CONS.value}-clone", cib_xml, push, **kwargs)
    if push:
        cib_push(cib_xml)

def s3bp(cib_xml, push=False, **kwargs):
    """Create S3 background producer.

    S3 background producer have to be only 1 per cluster and co-located with
    s3server.
    """
    s3bp_start = str(get_res_timeout(RESOURCE.S3_BACK_PROD.value, TIMEOUT_ACTION.START.value, "s3backgroundproducer"))
    s3bp_stop = str(get_res_timeout(RESOURCE.S3_BACK_PROD.value, TIMEOUT_ACTION.STOP.value, "s3backgroundproducer"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.S3_BACK_PROD.value} systemd:s3backgroundproducer \
        op start timeout={s3bp_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={s3bp_stop}s interval=0s")

    # Constraint
    process.run_cmd(f"pcs -f {cib_xml} constraint location {RESOURCE.S3_BACK_PROD.value} rule score=-INFINITY \
                    not_defined {RESOURCE.S3_SERVER.value}-count or {RESOURCE.S3_SERVER.value}-count lt integer 1")
    stop_constraint_on_s3servers(RESOURCE.S3_BACK_PROD.value, cib_xml, push, **kwargs)
    if push:
        cib_push(cib_xml)

def s3auth(cib_xml, push=False, **kwargs):
    """Create haproxy S3 auth server resource in pacemaker."""
    s3auth_start = str(get_res_timeout(RESOURCE.S3AUTH.value, TIMEOUT_ACTION.START.value, "s3authserver"))
    s3auth_stop = str(get_res_timeout(RESOURCE.S3AUTH.value, TIMEOUT_ACTION.STOP.value, "s3authserver"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.S3AUTH.value} systemd:s3authserver \
        op start timeout={s3auth_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={s3auth_stop}s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone {RESOURCE.S3AUTH.value}")
    if push:
        cib_push(cib_xml)

def haproxy(cib_xml, push=False, **kwargs):
    """Create haproxy clone resource in pacemaker."""
    haproxy_start = str(get_res_timeout(RESOURCE.HAPROXY.value, TIMEOUT_ACTION.START.value, "haproxy"))
    haproxy_stop = str(get_res_timeout(RESOURCE.HAPROXY.value, TIMEOUT_ACTION.STOP.value, "haproxy"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.HAPROXY.value} systemd:haproxy \
        op start timeout={haproxy_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={haproxy_stop}s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone {RESOURCE.HAPROXY.value} interleave=true")

    # Constraint
    process.run_cmd(f"pcs -f {cib_xml} constraint location {RESOURCE.HAPROXY.value}-clone rule score=-INFINITY \
                    not_defined {RESOURCE.S3_SERVER.value}-count or {RESOURCE.S3_SERVER.value}-count lt integer 1")
    stop_constraint_on_s3servers(f"{RESOURCE.HAPROXY.value}-clone", cib_xml, push, **kwargs)
    if push:
        cib_push(cib_xml)

def sspl(cib_xml, push=False, **kwargs):
    """Create sspl clone resource in pacemaker."""
    # Using sspl service file according to the content of SSPL repo
    sspl_start = str(get_res_timeout(RESOURCE.SSPL.value, TIMEOUT_ACTION.START.value, "sspl"))
    sspl_stop = str(get_res_timeout(RESOURCE.SSPL.value, TIMEOUT_ACTION.STOP.value, "sspl"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.SSPL.value} systemd:sspl \
        op start timeout={sspl_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={sspl_stop}s interval=0s --group monitor_group")
    if push:
        cib_push(cib_xml)

def mgmt_vip(cib_xml, push=False, **kwargs):
    """Create mgmt Virtual IP resource."""
    mgmt_vip_start = str(get_res_timeout(RESOURCE.MGMT_VIP.value, TIMEOUT_ACTION.START.value))
    mgmt_vip_stop = str(get_res_timeout(RESOURCE.MGMT_VIP.value, TIMEOUT_ACTION.STOP.value))
    vip_health_start = str(get_res_timeout(RESOURCE.VIP_HEALTH_MONITOR.value, TIMEOUT_ACTION.START.value))
    vip_health_stop = str(get_res_timeout(RESOURCE.VIP_HEALTH_MONITOR.value, TIMEOUT_ACTION.STOP.value))
    if "mgmt_info" not in kwargs.keys() or len(kwargs["mgmt_info"]) == 0:
        Log.warn("Management VIP is not detected in current configuration.")
    else:
        mgmt_info = kwargs["mgmt_info"]
        output, err, rc0 = process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.VIP_HEALTH_MONITOR.value} ocf:seagate:vip_health_monitor \
            vip={mgmt_info['mgmt_vip']} nic={mgmt_info['mgmt_iface']} \
            op start timeout={vip_health_start}s interval=0s \
            op monitor timeout=29s interval=30s \
            op stop timeout={vip_health_stop}s interval=0s --group management_group", check_error=False)
        output, err, rc1 = process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.MGMT_VIP.value} ocf:heartbeat:IPaddr2 \
            ip={mgmt_info['mgmt_vip']} cidr_netmask={mgmt_info['mgmt_netmask']} nic={mgmt_info['mgmt_iface']} iflabel=mgmt_vip \
            op start timeout={mgmt_vip_start}s interval=0s \
            op monitor timeout=29s interval=30s \
            op stop timeout={mgmt_vip_stop}s interval=0s --group management_group", check_error=False)
        if rc0 != 0 or rc1 != 0:
            raise CreateResourceError(f"Mgmt vip creation failed, mgmt info: {mgmt_info}, Err: {err}")
    if push:
        cib_push(cib_xml)

def csm(cib_xml, push=False, **kwargs):
    """Create mandatory resources for mgmt stack."""
    csm_agent_start = str(get_res_timeout(RESOURCE.CSM_AGENT.value, TIMEOUT_ACTION.START.value, "csm_agent"))
    csm_agent_stop = str(get_res_timeout(RESOURCE.CSM_AGENT.value, TIMEOUT_ACTION.STOP.value, "csm_agent"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.CSM_AGENT.value} systemd:csm_agent \
        op start timeout={csm_agent_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={csm_agent_stop}s interval=0s --group management_group")
    csm_web_start = str(get_res_timeout(RESOURCE.CSM_WEB.value, TIMEOUT_ACTION.START.value, "csm_web"))
    csm_web_stop = str(get_res_timeout(RESOURCE.CSM_WEB.value, TIMEOUT_ACTION.STOP.value, "csm_web"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.CSM_WEB.value} systemd:csm_web \
        op start timeout={csm_web_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={csm_web_stop}s interval=0s --group management_group")
    if push:
        cib_push(cib_xml)

def kibana(cib_xml, push=False, **kwargs):
    """Create mandatory resources for mgmt stack."""
    kibana_start = str(get_res_timeout(RESOURCE.KIBANA.value, TIMEOUT_ACTION.START.value, "kibana"))
    kibana_stop = str(get_res_timeout(RESOURCE.KIBANA.value, TIMEOUT_ACTION.STOP.value, "kibana"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.KIBANA.value} systemd:kibana \
        op start timeout={kibana_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={kibana_stop}s interval=0s --group management_group")
    if push:
        cib_push(cib_xml)

def event_analyzer(cib_xml, push=False, **kwargs):
    """Create event analyzer resource."""
    event_analyzer_start = str(get_res_timeout(RESOURCE.EVENT_ANALYZER.value, TIMEOUT_ACTION.START.value, "event_analyzer"))
    event_analyzer_stop = str(get_res_timeout(RESOURCE.EVENT_ANALYZER.value, TIMEOUT_ACTION.STOP.value, "event_analyzer"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.EVENT_ANALYZER.value} systemd:event_analyzer \
        op start timeout={event_analyzer_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={event_analyzer_stop}s interval=0s --group ha_group")
    if push:
        cib_push(cib_xml)

def health_monitor(cib_xml, push=False, **kwargs):
    """Create health monitor resource."""
    health_monitor_start = str(get_res_timeout(RESOURCE.HEALTH_MONITOR.value, TIMEOUT_ACTION.START.value, "health_monitor"))
    health_monitor_stop = str(get_res_timeout(RESOURCE.HEALTH_MONITOR.value, TIMEOUT_ACTION.STOP.value, "health_monitor"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.HEALTH_MONITOR.value} systemd:health_monitor \
        op start timeout={health_monitor_start}s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout={health_monitor_stop}s interval=0s --group ha_group")
    if push:
        cib_push(cib_xml)

def instance_counter(cib_xml, push=False, **kwargs):
    """Create service instance counter resource."""
    counter_start = str(get_res_timeout(RESOURCE.SRV_COUNTER.value, TIMEOUT_ACTION.START.value))
    counter_stop = str(get_res_timeout(RESOURCE.SRV_COUNTER.value, TIMEOUT_ACTION.STOP.value))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.SRV_COUNTER.value} ocf:seagate:service_instances_counter \
        op start timeout={counter_start}s interval=0s \
        op monitor timeout=5s interval=6s \
        op stop timeout={counter_stop}s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone {RESOURCE.SRV_COUNTER.value}")
    if push:
        cib_push(cib_xml)

def mbus_rest(cib_xml, push=False, **kwargs):
    """Create service instance counter resource."""
    mbus_rest_start = str(get_res_timeout(RESOURCE.M_BUS_REST.value, TIMEOUT_ACTION.START.value, "cortx_message_bus"))
    mbus_rest_stop = str(get_res_timeout(RESOURCE.M_BUS_REST.value, TIMEOUT_ACTION.STOP.value, "cortx_message_bus"))
    process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.M_BUS_REST.value} systemd:cortx_message_bus \
        op start timeout={mbus_rest_start}s interval=0s \
        op monitor timeout=29s interval=30s \
        op stop timeout={mbus_rest_stop}s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone {RESOURCE.M_BUS_REST.value}")
    if push:
        cib_push(cib_xml)

def uds(cib_xml, push=False, **kwargs):
    """Create uds resource."""
    uds_start = str(get_res_timeout(RESOURCE.UDS.value, TIMEOUT_ACTION.START.value, "uds"))
    uds_stop = str(get_res_timeout(RESOURCE.UDS.value, TIMEOUT_ACTION.STOP.value, "uds"))
    with_uds = kwargs["uds"] if "uds" in kwargs else False
    if with_uds:
        process.run_cmd(f"pcs -f {cib_xml} resource create {RESOURCE.UDS.value} systemd:uds \
            op start timeout={uds_start}s interval=0s \
            op monitor timeout=29s interval=30s \
            op stop timeout={uds_stop}s interval=0s")

        # Constraints
        process.run_cmd(f"pcs -f {cib_xml} pcs -f {cib_xml} constraint colocation add {RESOURCE.UDS.value} with {RESOURCE.CSM_AGENT.value} score=INFINITY")
        process.run_cmd(f"pcs -f {cib_xml} pcs -f {cib_xml} constraint order {RESOURCE.CSM_AGENT.value} then {RESOURCE.UDS.value}")

        if push:
            cib_push(cib_xml)

def configure_stonith(cib_xml=None, push=False, **kwargs):
    """Create ipmi stonith resource."""

    if cib_xml is None:
        cib_xml = cib_get(const.CIB_FILE)

    stonith_config = kwargs.get("stonith_config")
    if stonith_config and stonith_config.get("node_type").lower() == const.INSTALLATION_TYPE.HW.value.lower():
        resource_id = stonith_config.get("resource_id")
        Log.info(f"Configuring stonith resource : {resource_id}")

        # check for stonith config present for that node
        _output, _err, _rc = process.run_cmd(const.PCS_STONITH_SHOW.replace("<resource_id>", resource_id), check_error=False)
        if _output and "Error" not in _output and resource_id in _output:
            Log.info(f"Stonith resource already configured : {resource_id}.")
            return

        ipaddr = stonith_config.get("ipaddr")
        login = stonith_config.get("login")
        passwd = stonith_config.get("passwd")
        pcmk_host_list = stonith_config.get("pcmk_host_list")
        auth = stonith_config.get("auth")

        process.run_cmd(f"pcs -f {cib_xml} stonith create {resource_id} fence_ipmilan ipaddr={ipaddr} \
            login={login} passwd={passwd} pcmk_host_list={pcmk_host_list} pcmk_host_check=static-list \
            lanplus=true auth={auth} power_timeout=40 verbose=true \
            op monitor interval=10s meta failure-timeout=15s --group ha_group", secret=passwd)
        process.run_cmd(f"pcs -f {cib_xml} constraint location {resource_id} avoids {pcmk_host_list}")
        process.run_cmd(f"pcs -f {cib_xml} resource clone {resource_id}")

        Log.info(f"Configured stonith resource : {resource_id}")
        if push:
            cib_push(cib_xml)
    else:
        raise ConfigureStonithResourceError(f"Stonith configuration not available to create "
                                            f"stonith resource or not detected HW env")

core_io = [hax, motr_conf, motr, s3auth, s3servers, haproxy]
io_helper_aa = [s3bc]
io_helper_ap = [free_space_monitor, s3bp]
monitor_config = [sspl]
management_config = [mgmt_vip, kibana, csm, uds]
ha_group_config = [event_analyzer, instance_counter, health_monitor]
base_services_config = [mbus_rest]

def io_stack(cib_xml, push=False, **kwargs):
    """Create IO stack related resources."""
    Log.info("HA Rules: ******* io_group *********")
    # Create core io resources
    for create_resource in core_io:
        Log.info(f"HA Rules: Configure {str(create_resource)}")
        create_resource(cib_xml, push, **kwargs)
    # Create helper active_active io resources
    for create_resource in io_helper_aa:
        Log.info(f"HA Rules: Configure {str(create_resource)}")
        create_resource(cib_xml, push, **kwargs)
    # Create helper active_passive io resources
    for create_resource in io_helper_ap:
        Log.info(f"HA Rules: Configure {str(create_resource)}")
        create_resource(cib_xml, push, **kwargs)
    if push:
        cib_push(cib_xml)

def monitor_stack(cib_xml, push=False, **kwargs):
    """Configure monitor stack"""
    Log.info("HA Rules: ******* monitor_group *********")
    for create_resource in monitor_config:
        Log.info(f"HA Rules: Configure {str(create_resource)}")
        create_resource(cib_xml, push, **kwargs)
    process.run_cmd(f"pcs -f {cib_xml} resource clone monitor_group")
    if push:
        cib_push(cib_xml)

def management_group(cib_xml, push=False, **kwargs):
    """Configure management group"""
    Log.info("HA Rules: ******* management_group *********")
    for create_resource in management_config:
        Log.info(f"HA Rules: Configure {str(create_resource)}")
        create_resource(cib_xml, push, **kwargs)
    if push:
        cib_push(cib_xml)

def ha_group(cib_xml, push=False, **kwargs):
    """Configure management group"""
    Log.info("HA Rules: ******* ha_group *********")
    for create_resource in ha_group_config:
        Log.info(f"HA Rules: Configure {str(create_resource)}")
        create_resource(cib_xml, push, **kwargs)
    if push:
        cib_push(cib_xml)

def base_services(cib_xml, push=False, **kwargs):
    """Configure base services (Foundation)"""
    Log.info("HA Rules: ******* base services *********")
    for create_resource in base_services_config:
        Log.info(f"HA Rules: Configure {str(create_resource)}")
        create_resource(cib_xml, push, **kwargs)
    if push:
        cib_push(cib_xml)

def create_all_resources(cib_xml=const.CIB_FILE, push=True, **kwargs):
    """Populate the cluster with all Cortx resources.

    Parameters:
        cib_xml - file where CIB XML shall be stored (optional)
        push - whether changes shall be actually applied (optional)
    Returns: None

    Exceptions:
        CreateResourceError: failed to create any resource.
        CreateResourceConfigError: exception is generated if set of argument is
        not empty but incomplete.
    """
    try:
        Log.info("HA Rules: Start creating all HA resources.")
        cib_get(cib_xml)
        # Configure io resource
        io_stack(cib_xml, False, **kwargs)
        # Configuration of monitor
        monitor_stack(cib_xml, False, **kwargs)
        # Configure of management group
        management_group(cib_xml, False, **kwargs)
        # Configure HA management group
        ha_group(cib_xml, False, **kwargs)
        # Configure base services
        base_services(cib_xml, False, **kwargs)
        # Change the defaults
        change_pcs_default(cib_xml, False, **kwargs)

        if push:
            cib_push(cib_xml)
        Log.info("HA Rules: Successfully configured all HA resources and its configuration.")
    except Exception:
        raise CreateResourceError("Failed to populate cluster with resources")
