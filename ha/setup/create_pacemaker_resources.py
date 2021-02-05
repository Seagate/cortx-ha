#!/bin/python3

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


class CreateResourceError(Exception):
    """Exception to indicate any failure happened during resource creation."""


class CreateResourceConfigError(CreateResourceError):
    """Exception to indicate that given resource configuration is incorrect or incomplete."""


def cib_push(cib_xml):
    """Shortcut to avoid boilerplate pushing CIB file."""
    cmd_push = f"pcs cluster cib-push {cib_xml} --config"
    SimpleCommand().run_cmd(cmd_push)


def cib_get(cib_xml):
    """Generate CIB file using pcs."""
    cmd = f"pcs cluster cib {cib_xml}"
    SimpleCommand().run_cmd(cmd)

    return cib_xml


def motr_hax(cib_xml, push=False):
    """Create resources that belong to motr group and clone the group."""
    # TODO here that it's temporary code and should be removed once fixed by hax/provisioner.
    cmd_hare_consul = f"pcs -f {cib_xml} resource create hax-consul systemd:hare-consul-agent --group io_group"
    cmd_hax = f"pcs -f {cib_xml} resource create hax systemd:hare-hax --group io_group"
    cmd_confd = f"pcs -f {cib_xml} resource create motr-confd-1 ocf:seagate:dynamic_fid_service_ra service=m0d fid_service_name=confd --group io_group --force"
    cmd_ios = f"pcs -f {cib_xml} resource create motr-ios-1 ocf:seagate:dynamic_fid_service_ra service=m0d fid_service_name=ios --group io_group --force"

    for s in (cmd_hare_consul, cmd_hax, cmd_confd, cmd_ios):
        SimpleCommand().run_cmd(s)

    if push:
        cib_push(cib_xml)


def free_space_monitor(cib_xml, push=False):
    """Create free space monitor resource. 1 per cluster, no affinity."""
    cmd_fsm = f"pcs -f {cib_xml} resource create motr-free-space-mon systemd:motr-free-space-monitor op monitor interval=30s meta failure-timeout=300s"
    SimpleCommand().run_cmd(cmd_fsm)

    constraints = [
            f"pcs -f {cib_xml} constraint order motr-ios-1 then motr-free-space-mon",
            f"pcs -f {cib_xml} constraint colocation add motr-free-space-mon with motr-ios-1"
            ]
    for c in constraints:
        SimpleCommand().run_cmd(c)

    if push:
        cib_push(cib_xml)


def s3servers(cib_xml, instance=11, push=False):
    """Create resources that belong to s3server group and clone the group.

    S3 background consumer is ordered after s3server and co-located with it.
    """
    for i in range(1, int(instance)+1):
        cmd_s3server = f"pcs -f {cib_xml} resource create s3server-{i} ocf:seagate:dynamic_fid_service_ra service=s3server fid_service_name=s3service --group io_group --force"
        SimpleCommand().run_cmd(cmd_s3server)
    cmd_s3bc = f"pcs -f {cib_xml} resource create s3backcons systemd:s3backgroundconsumer meta failure-timeout=300s --group io_group"
    SimpleCommand().run_cmd(cmd_s3bc)

    if push:
        cib_push(cib_xml)


def s3bp(cib_xml, push=False):
    """Create S3 background producer.

    S3 background producer have to be only 1 per cluster and co-located with
    s3server.
    """
    cmd_s3bp = f"pcs -f {cib_xml} resource create s3backprod systemd:s3backgroundproducer op monitor interval=30s"
    cmd_order = f"pcs -f {cib_xml} constraint order io_group-clone then s3backprod"

    for s in (cmd_s3bp, cmd_order):
        SimpleCommand().run_cmd(s)

    if push:
        cib_push(cib_xml)


def s3auth(cib_xml, push=False):
    """Create haproxy S3 auth server resource in pacemaker."""
    cmd_s3auth = f"pcs -f {cib_xml} resource create s3auth systemd:s3authserver clone op monitor interval=30"
    SimpleCommand().run_cmd(cmd_s3auth)

    if push:
        cib_push(cib_xml)


def haproxy(cib_xml, push=False):
    """Create haproxy clone resource in pacemaker."""
    cmd_haproxy = f"pcs -f {cib_xml} resource create haproxy systemd:haproxy op monitor interval=30 --group io_group"
    SimpleCommand().run_cmd(cmd_haproxy)

    if push:
        cib_push(cib_xml)


def sspl(cib_xml, push=False):
    """Create sspl clone resource in pacemaker."""
    # Using sspl-ll service file according to the content of SSPL repo
    cmd_sspl = f"pcs -f {cib_xml} resource create sspl-ll systemd:sspl-ll clone op monitor interval=30"
    SimpleCommand().run_cmd(cmd_sspl)

    if push:
        cib_push(cib_xml)


def io_stack(cib_xml, s3_count, push=False):
    """Create IO stack related resources."""
    resources = [motr_hax, s3auth, haproxy]
    for rcs in resources:
        rcs(cib_xml, push)

    s3servers(cib_xml, s3_count, push)
    cmd_clone_group = f"pcs -f {cib_xml} resource clone io_group"
    SimpleCommand().run_cmd(cmd_clone_group)
    s3bp(cib_xml, push)

    if push:
        cib_push(cib_xml)


def mgmt_vip(cib_xml, vip, iface, cidr=24, push=False):
    """Create mgmt Virtual IP resource."""
    cmd = f"pcs -f {cib_xml} resource create mgmt-vip ocf:heartbeat:IPaddr2 \
ip={vip} cidr_netmask={cidr} nic={iface} iflabel=v1 \
op start   interval=0s timeout=60s \
op monitor interval=5s timeout=20s \
op stop    interval=0s timeout=60s"
    SimpleCommand().run_cmd(cmd)

    if push:
        cib_push(cib_xml)


def mgmt_resources(cib_xml, push=False):
    """Create mandatory resources for mgmt stack."""
    kibana = f"pcs -f {cib_xml} resource create kibana systemd:kibana op monitor interval=30s"
    agent = f"pcs -f {cib_xml} resource create csm-agent systemd:csm_agent op monitor interval=30s"
    web = f"pcs -f {cib_xml} resource create csm-web systemd:csm_web op monitor interval=30s"

    for c in (kibana, agent, web):
        SimpleCommand().run_cmd(c)

    if push:
        cib_push(cib_xml)


def uds(cib_xml, push=False):
    """Create uds resource and constraints."""
    cmd_uds = f"pcs -f {cib_xml} resource create uds systemd:uds op monitor interval=30s"
    SimpleCommand().run_cmd(cmd_uds)
    constraints = [
            f"pcs -f {cib_xml} constraint colocation add uds with csm-agent score=INFINITY",
            # According to EOS-9258, there is a bug which requires UDS to be started after csm_agent
            f"pcs -f {cib_xml} constraint order csm-agent then uds"
            ]
    for c in constraints:
        SimpleCommand().run_cmd(c)
    if push:
        cib_push(cib_xml)


def mgmt_stack(cib_xml, mgmt_vip_cfg, with_uds=False, push=False):
    """Create Mgmt stack related resources.

    It also creates and defines management group to support colocation and
    ordering requirements.
    """
    mgmt_resources(cib_xml)

    if with_uds:
        uds(cib_xml)

    cmd = f"pcs -f {cib_xml} resource group add management kibana csm-agent csm-web"
    SimpleCommand().run_cmd(cmd)

    if mgmt_vip_cfg:
        mgmt_vip(cib_xml, **mgmt_vip_cfg, push=False)
        cmd_group = f"pcs -f {cib_xml} resource group add management kibana --before csm-agent"
        SimpleCommand().run_cmd(cmd_group)

    if push:
        cib_push(cib_xml)


def create_all_resources(cib_xml="/var/log/seagate/cortx/ha/cortx-lr2-cib.xml",
                         push=True, **kwargs):
    """Populate the cluster with all Cortx resources.

    Parameters:
        cib_xml - file where CIB XML shall be stored (optional)
        push - whether changes shall be actually applied (optional)
        vip - mgmt virtual ip (example: 10.0.0.6)
        cidr - netmask for mgmt vip (example: 24)
        iface - interface to configure mgmt vip (example: eno1)

        vip, cidr, iface options are validated to be passed together.

    Returns: None

    Exceptions:
        CreateResourceError: failed to create any resourse.
        CreateResourceConfigError: exception is generated if set of argument is
        not empty but incomplete.
    """
    mgmt_vip_cfg = {k: kwargs[k] for k in ("vip", "cidr", "iface")
                    if k in kwargs and kwargs[k] is not None}
    if len(mgmt_vip_cfg) not in (0, 3):
        raise CreateResourceConfigError("Given mgmt VIP configuration is incomplete")

    with_uds = kwargs["uds"] if "uds" in kwargs else False
    s3_instances = int(kwargs["s3_instances"]) if "s3_instances" in kwargs else 11
    try:
        cib_get(cib_xml)
        io_stack(cib_xml, s3_instances)
        sspl(cib_xml)
        mgmt_stack(cib_xml, mgmt_vip_cfg, with_uds)
        if push:
            cib_push(cib_xml)
    except Exception:
        raise CreateResourceError("Failed to populate cluster with resources")


def _parse_input_args():
    """Parse and validate input arguments passed by mini-provisioner or CLI."""
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Create resources for Cortx cluster")
    parser.add_argument("--dry-run", action="store_true", help="Generate CIB XML but don't push")
    parser.add_argument("--with-uds", action="store_true", default=False, help="Also create UDS resource")
    parser.add_argument("--cib-xml", type=str, default="/var/log/seagate/cortx/ha/cortx-lr2-cib.xml", help="File name to store generated CIB")
    group = parser.add_argument_group("Management", "Parameters to setup virtual IP if needed")
    group.add_argument("--vip", type=str, nargs="?", help="Virtual mgmt IP address")
    group.add_argument("--cidr", type=int, nargs="?", help="Netmask for mgmt VIP. Ex.: 24")
    group.add_argument("--iface", type=str, nargs="?", help="Network interface for mgmt VIP")
    return parser.parse_args()


def _main():
    # Workaround to make SimpleCommand work, not crash
    Log.init(service_name="create_pacemaker_resources",
             log_path="/var/log/seagate/cortx/ha", level="INFO")

    args = _parse_input_args()

    create_all_resources(args.cib_xml, vip=args.vip, cidr=args.cidr,
                         iface=args.iface, s3_instances=args.s3_instances, push=not args.dry_run,
                         uds=args.with_uds)


if __name__ == "__main__":
    _main()
