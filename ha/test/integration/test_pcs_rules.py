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

import os
import sys
import pathlib
import argparse
from cortx.utils.log import Log
sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..'))
from ha.setup.create_pacemaker_resources import create_all_resources

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
    Log.init(service_name="create_pacemaker_resources",
             log_path="/var/log/seagate/cortx/ha", level="INFO")

    args = _parse_input_args()

    create_all_resources(args.cib_xml, vip=args.vip, cidr=args.cidr,
                         iface=args.iface, s3_instances=args.s3_instances, push=not args.dry_run,
                         uds=args.with_uds)


if __name__ == "__main__":
    _main()