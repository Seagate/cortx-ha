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
io_group-clone
    hax-consul
    hax
    motr-confd-1
    motr-ios-1
    haproxy
    s3auth
    s3server-1
    s3server-2
    s3server-3
    s3server-4
    s3backcons
s3backprod
sspl-ll-clone
    sspl-ll
management
    kibana
    csm-agent
    csm-web
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

def hax(cib_xml, push=False, **kwargs):
    """Create resources that belong to hax and clone the group."""
    # TODO cmd_hare_consul is temporary code and should be removed once fixed by hax/provisioner.
    # hax-consul
    process.run_cmd(f"pcs -f {cib_xml} resource create hax-consul systemd:hare-consul-agent \
        op start timeout=100s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=120s interval=0s --group io_group")
    # hax
    process.run_cmd(f"pcs -f {cib_xml} resource create hax systemd:hare-hax \
        op start timeout=100s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=120s interval=0s --group io_group")
    if push:
        cib_push(cib_xml)

def motr(cib_xml, push=False, **kwargs):
    """Configure motr resource."""
    process.run_cmd(f"pcs -f {cib_xml} resource create motr-confd-1 ocf:seagate:dynamic_fid_service_ra service=m0d fid_service_name=confd \
        op start timeout=100s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=120s interval=0s --group io_group")
    if "ios_instances" in kwargs:
        ios_instances = int(kwargs["ios_instances"])
    else:
        ios_instances = 1
    for i in range(1, int(ios_instances)+1):
        process.run_cmd(f"pcs -f {cib_xml} resource create motr-ios-{i} ocf:seagate:dynamic_fid_service_ra service=m0d fid_service_name=ioservice \
            op start timeout=100s interval=0s \
            op monitor timeout=30s interval=30s \
            op stop timeout=120s interval=0s --group io_group")
    if push:
        cib_push(cib_xml)

def free_space_monitor(cib_xml, push=False, **kwargs):
    """Create free space monitor resource. 1 per cluster, no affinity."""
    process.run_cmd(f"pcs -f {cib_xml} resource create motr-free-space-mon systemd:motr-free-space-monitor \
        op start timeout=100s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=120s interval=0s meta failure-timeout=300s")
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
        process.run_cmd(f"pcs -f {cib_xml} resource create s3server-{i} ocf:seagate:dynamic_fid_service_ra service=s3server fid_service_name=s3server \
            op start timeout=60s interval=0s \
            op monitor timeout=30s interval=30s \
            op stop timeout=60s interval=0s --group io_group")
    if push:
        cib_push(cib_xml)

def s3bc(cib_xml, push=False, **kwargs):
    """Create S3 background consumer."""
    process.run_cmd(f"pcs -f {cib_xml} resource create s3backcons systemd:s3backgroundconsumer meta failure-timeout=300s \
        op start timeout=100s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=120s interval=0s --group io_group")
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
    if push:
        cib_push(cib_xml)

def s3auth(cib_xml, push=False, **kwargs):
    """Create haproxy S3 auth server resource in pacemaker."""
    process.run_cmd(f"pcs -f {cib_xml} resource create s3auth systemd:s3authserver \
        op start timeout=60s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=60s interval=0s --group io_group")
    if push:
        cib_push(cib_xml)

def haproxy(cib_xml, push=False, **kwargs):
    """Create haproxy clone resource in pacemaker."""
    process.run_cmd(f"pcs -f {cib_xml} resource create haproxy systemd:haproxy \
        op start timeout=60s interval=0s \
        op monitor timeout=30s interval=30s \
        op stop timeout=60s interval=0s --group io_group")
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
    mgmt_vip_cfg = {k: kwargs[k] for k in ("vip", "cidr", "iface")
                    if k in kwargs and kwargs[k] is not None}
    if len(mgmt_vip_cfg) not in (0, 3):
        raise CreateResourceConfigError("Given mgmt VIP configuration is incomplete")
    if mgmt_vip_cfg:
        process.run_cmd(f"pcs -f {cib_xml} resource create mgmt-vip ocf:heartbeat:IPaddr2 \
            ip={mgmt_vip_cfg['vip']} cidr_netmask={mgmt_vip_cfg['cidr']} nic={mgmt_vip_cfg['iface']} iflabel=v1 \
            op start timeout=60s interval=0s \
            op monitor timeout=30s interval=30s \
            op stop timeout=60s interval=0s --group management_group")
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

def uds(cib_xml, push=False, **kwargs):
    """Create uds resource."""
    with_uds = kwargs["uds"] if "uds" in kwargs else False
    if with_uds:
        process.run_cmd(f"pcs -f {cib_xml} resource create uds systemd:uds \
            op start timeout=60s interval=0s \
            op monitor timeout=30s interval=30s \
            op stop timeout=60s interval=0s")
        if push:
            cib_push(cib_xml)

def config_constraint(cib_xml, push=False, **kwargs):
    """
    Configure all constaints

    Args:
        cib_xml (str): cib cluster file.
    """
    constraints = [
            f"pcs -f {cib_xml} constraint order io_group-clone then motr-free-space-mon",
            f"pcs -f {cib_xml} constraint colocation add motr-free-space-mon with io_group-clone",
            f"pcs -f {cib_xml} constraint colocation add s3backprod with io_group-clone"
            # According to EOS-9258, there is a bug which requires UDS to be started after csm_agent
            f"pcs -f {cib_xml} constraint colocation add uds with csm-agent score=INFINITY",
            f"pcs -f {cib_xml} constraint order csm-agent then uds"
        ]
    with_uds = kwargs["uds"] if "uds" in kwargs else False
    for c in constraints:
        if with_uds == False and "uds" in c:
            continue
        process.run_cmd(c)
    if push:
        cib_push(cib_xml)

core_io = [hax, motr, s3auth, s3servers, haproxy]
io_helper_aa = [s3bc]
io_helper_ap = [free_space_monitor, s3bp]
monitor_config = [sspl]
management_config = [mgmt_vip, kibana, csm, uds]
# TODO: ha_group

def io_stack(cib_xml, push, **kwargs):
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
    process.run_cmd(f"pcs -f {cib_xml} resource clone io_group")
    if push:
        cib_push(cib_xml)

def monitor_stack(cib_xml, push, **kwargs):
    """Configure monitor stack"""
    Log.info("HA Rules: ******* monitor_group *********")
    for create_resource in monitor_config:
        Log.info(f"HA Rules: Configure {str(create_resource)}")
        create_resource(cib_xml, push, **kwargs)
    process.run_cmd(f"pcs -f {cib_xml} resource clone monitor_group")
    if push:
        cib_push(cib_xml)

def management_group(cib_xml, push, **kwargs):
    """Configure management group"""
    Log.info("HA Rules: ******* management_group *********")
    for create_resource in management_config:
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
        # Configure constraint
        Log.info("HA Rules: Start configuring HA Rules.")
        config_constraint(cib_xml, False, **kwargs)
        if push:
            cib_push(cib_xml)
        Log.info("HA Rules: Successfully configured all HA resources and its configuration.")
    except Exception:
        raise CreateResourceError("Failed to populate cluster with resources")