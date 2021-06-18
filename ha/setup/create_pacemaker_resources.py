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

import argparse
from ha.execute import SimpleCommand
from cortx.utils.log import Log

from ha.core.error import CreateResourceError
from ha.core.error import CreateResourceConfigError
from ha import const

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
    sspl-ll
management
    mgmt-vip
    kibana
    csm-agent
    csm-web
ha
    event_analyzer
    srv_counter
"""

process = SimpleCommand()

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
    # hax
    process.run_cmd(f"pcs -f {cib_xml} resource create hax systemd:hare-hax \
        op start timeout=100s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=120s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone hax")
    if push:
        cib_push(cib_xml)

def motr_conf(cib_xml, push=False, **kwargs):
    process.run_cmd(f"pcs -f {cib_xml} resource create motr-confd-1 ocf:seagate:dynamic_fid_service_ra service=m0d fid_service_name=confd \
        update_attrib=true \
        op start timeout=100s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=120s interval=0s")
    try:
        quorum_size = int(kwargs["node_count"])
        process.run_cmd(f"pcs -f {cib_xml} resource clone motr-confd-1 interleave=true clone-min={quorum_size}")
    except Exception as e:
        raise CreateResourceConfigError(f"Invalid node_count. Error: {e}")

    # Constraint
    process.run_cmd(f"pcs -f {cib_xml} constraint order hax-clone then motr-confd-1-clone")
    process.run_cmd(f"pcs -f {cib_xml} constraint colocation add motr-confd-1-clone with hax-clone")

    if push:
        cib_push(cib_xml)


def motr(cib_xml, push=False, **kwargs):
    """Configure motr resource."""
    if "ios_instances" in kwargs:
        ios_instances = int(kwargs["ios_instances"])
    else:
        ios_instances = 1
    for i in range(1, int(ios_instances)+1):
        process.run_cmd(f"pcs -f {cib_xml} resource create motr-ios-{i} ocf:seagate:dynamic_fid_service_ra service=m0d fid_service_name=ioservice \
            update_attrib=true \
            op start timeout=100s interval=0s \
            op monitor timeout=30s interval=30s \
            op stop timeout=120s interval=0s")
        process.run_cmd(f"pcs -f {cib_xml} resource clone motr-ios-{i}")

        # Constraint
        try:
            quorum_size = int(kwargs["node_count"])//2
            quorum_size += 1
            process.run_cmd(f"pcs -f {cib_xml} constraint location motr-ios-{i}-clone rule score=-INFINITY \
                    not_defined motr-confd-count or motr-confd-count lt integer {quorum_size}")
            process.run_cmd(f"pcs -f {cib_xml} constraint order hax-clone then motr-ios-{i}-clone")
            process.run_cmd(f"pcs -f {cib_xml} constraint colocation add motr-ios-{i}-clone with hax-clone")
        except Exception as e:
            raise CreateResourceConfigError(f"Invalid node_count. Error: {e}")
    if push:
        cib_push(cib_xml)

def free_space_monitor(cib_xml, push=False, **kwargs):
    """Create free space monitor resource. 1 per cluster, no affinity."""
    process.run_cmd(f"pcs -f {cib_xml} resource create motr-free-space-mon systemd:motr-free-space-monitor \
        op start timeout=100s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=120s interval=0s meta failure-timeout=300s")

    # Constraint
    process.run_cmd(f"pcs -f {cib_xml} constraint location motr-free-space-mon rule score=-INFINITY \
                    not_defined motr-ios-count or motr-ios-count lt integer 1")
    if push:
        cib_push(cib_xml)

def s3servers(cib_xml, push=False, **kwargs):
    """Create resources that belong to s3server group and clone the group.

    S3 background consumer is ordered after s3server and co-located with it.
    """
    try:
        instance = int(kwargs["s3_instances"])
    except Exception as e:
        raise CreateResourceConfigError(f"Invalid s3 instance. Error: {e}")
    for i in range(1, int(instance)+1):
        process.run_cmd(f"pcs -f {cib_xml} resource create s3server-{i} ocf:seagate:dynamic_fid_service_ra \
            service=s3server fid_service_name=s3server update_attrib=true \
            op start timeout=60s interval=0s \
            op monitor timeout=30s interval=30s \
            op stop timeout=60s interval=0s")
        process.run_cmd(f"pcs -f {cib_xml} resource clone s3server-{i} interleave=true")

        # Constraint
        process.run_cmd(f"pcs -f {cib_xml} constraint location s3server-{i}-clone rule score=-INFINITY \
                        not_defined motr-ios-count or  motr-ios-count lt integer 1")
        process.run_cmd(f"pcs -f {cib_xml} constraint colocation add s3server-{i}-clone with s3auth-clone")
    if push:
        cib_push(cib_xml)

def s3bc(cib_xml, push=False, **kwargs):
    """Create S3 background consumer."""
    process.run_cmd(f"pcs -f {cib_xml} resource create s3backcons systemd:s3backgroundconsumer meta failure-timeout=300s \
        op start timeout=100s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=120s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone s3backcons")

    # Constraint
    process.run_cmd(f"pcs -f {cib_xml} constraint location s3backcons-clone rule score=-INFINITY \
                    not_defined s3server-count or s3server-count lt integer 1")
    if push:
        cib_push(cib_xml)

def s3bp(cib_xml, push=False, **kwargs):
    """Create S3 background producer.

    S3 background producer have to be only 1 per cluster and co-located with
    s3server.
    """
    process.run_cmd(f"pcs -f {cib_xml} resource create s3backprod systemd:s3backgroundproducer \
        op start timeout=60s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=60s interval=0s")

    # Constraint
    process.run_cmd(f"pcs -f {cib_xml} constraint location s3backprod rule score=-INFINITY \
                    not_defined s3server-count or s3server-count lt integer 1")
    if push:
        cib_push(cib_xml)

def s3auth(cib_xml, push=False, **kwargs):
    """Create haproxy S3 auth server resource in pacemaker."""
    process.run_cmd(f"pcs -f {cib_xml} resource create s3auth systemd:s3authserver \
        op start timeout=60s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=60s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone s3auth")
    if push:
        cib_push(cib_xml)

def haproxy(cib_xml, push=False, **kwargs):
    """Create haproxy clone resource in pacemaker."""
    process.run_cmd(f"pcs -f {cib_xml} resource create haproxy systemd:haproxy \
        op start timeout=60s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=60s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone haproxy")

    # Constraint
    process.run_cmd(f"pcs -f {cib_xml} constraint location haproxy-clone rule score=-INFINITY \
                    not_defined s3server-count or s3server-count lt integer 1")
    if push:
        cib_push(cib_xml)

def sspl(cib_xml, push=False, **kwargs):
    """Create sspl clone resource in pacemaker."""
    # Using sspl-ll service file according to the content of SSPL repo
    process.run_cmd(f"pcs -f {cib_xml} resource create sspl-ll systemd:sspl-ll \
        op start timeout=60s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=60s interval=0s --group monitor_group")
    if push:
        cib_push(cib_xml)

def mgmt_vip(cib_xml, push=False, **kwargs):
    """Create mgmt Virtual IP resource."""
    if "mgmt_info" not in kwargs.keys() or len(kwargs["mgmt_info"]) == 0:
        Log.warn("Management VIP is not detected in current configuration.")
    else:
        mgmt_info = kwargs["mgmt_info"]
        output, err, rc = process.run_cmd(f"pcs -f {cib_xml} resource create mgmt-vip ocf:heartbeat:IPaddr2 \
            ip={mgmt_info['mgmt_vip']} cidr_netmask={mgmt_info['mgmt_netmask']} nic={mgmt_info['mgmt_iface']} iflabel=mgmt_vip \
            op start timeout=60s interval=0s \
            op monitor timeout=30s interval=30s \
            op stop timeout=60s interval=0s --group management_group", check_error=False)
        if rc != 0:
            raise CreateResourceError(f"Mgmt vip creation failed, mgmt info: {mgmt_info}, Err: {err}")
    if push:
        cib_push(cib_xml)

def csm(cib_xml, push=False, **kwargs):
    """Create mandatory resources for mgmt stack."""
    process.run_cmd(f"pcs -f {cib_xml} resource create csm-agent systemd:csm_agent \
        op start timeout=60s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=120s interval=0s --group management_group")
    process.run_cmd(f"pcs -f {cib_xml} resource create csm-web systemd:csm_web \
        op start timeout=60s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=60s interval=0s --group management_group")
    if push:
        cib_push(cib_xml)

def kibana(cib_xml, push=False, **kwargs):
    """Create mandatory resources for mgmt stack."""
    process.run_cmd(f"pcs -f {cib_xml} resource create kibana systemd:kibana \
        op start timeout=60s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=60s interval=0s --group management_group")
    if push:
        cib_push(cib_xml)

def event_analyzer(cib_xml, push=False, **kwargs):
    """Create event analyzer resource."""
    process.run_cmd(f"pcs -f {cib_xml} resource create event_analyzer systemd:event_analyzer \
        op start timeout=60s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=60s interval=0s --group ha_group")
    if push:
        cib_push(cib_xml)

def instance_counter(cib_xml, push=False, **kwargs):
    """Create service instance counter resource."""
    process.run_cmd(f"pcs -f {cib_xml} resource create srv_counter ocf:seagate:service_instances_counter \
        op start timeout=60s interval=0s \
        op monitor timeout=5s interval=5s \
        op stop timeout=60s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone srv_counter")
    if push:
        cib_push(cib_xml)

def mbus_rest(cib_xml, push=False, **kwargs):
    """Create service instance counter resource."""
    process.run_cmd(f"pcs -f {cib_xml} resource create mbus_rest systemd:cortx_message_bus \
        op start timeout=60s interval=0s \
        op monitor timeout=3s interval=3s \
        op stop timeout=60s interval=0s")
    process.run_cmd(f"pcs -f {cib_xml} resource clone mbus_rest")
    if push:
        cib_push(cib_xml)

def uds(cib_xml, push=False, **kwargs):
    """Create uds resource."""
    with_uds = kwargs["uds"] if "uds" in kwargs else False
    if with_uds:
        process.run_cmd(f"pcs -f {cib_xml} resource create uds systemd:uds \
            op start timeout=60s interval=0s \
            op monitor timeout=30s interval=30s \
            op stop timeout=60s interval=0s")

        # Constraints
        process.run_cmd(f"pcs -f {cib_xml} pcs -f {cib_xml} constraint colocation add uds with csm-agent score=INFINITY")
        process.run_cmd(f"pcs -f {cib_xml} pcs -f {cib_xml} constraint order csm-agent then uds")

        if push:
            cib_push(cib_xml)

core_io = [hax, motr_conf, motr, s3auth, s3servers, haproxy]
io_helper_aa = [s3bc]
io_helper_ap = [free_space_monitor, s3bp]
monitor_config = [sspl]
management_config = [mgmt_vip, kibana, csm, uds]
ha_group_config = [event_analyzer, instance_counter]
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
