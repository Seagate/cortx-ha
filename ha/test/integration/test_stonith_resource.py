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
import sys
import pathlib
import traceback
import argparse
from ha.setup.create_pacemaker_resources import ha_group
from ha.setup.create_pacemaker_resources import cib_get
from cortx.utils.log import Log


# Test case for create stonith resource.

def _parse_input_args():
    """Parse and validate input arguments passed by mini-provisioner or CLI."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Create stonith resources for Cortx cluster")
    parser.add_argument("--cib-xml", type=str, default="/var/log/seagate/cortx/ha/cortx-lr2-cib.xml",
                        help="File name to store generated CIB")
    parser.add_argument("--resource_id", type=str,
                        help="ID of stoith resource")
    parser.add_argument("--ipaddr", type=str,
                        help="IP address or hostname of fencing device.")
    parser.add_argument("--login", type=str,
                        help="Login user.")
    parser.add_argument("--passwd", type=str, default="/var/log/seagate/cortx/ha/cortx-lr2-cib.xml",
                        help="Login password or passphrase.")
    parser.add_argument("--node_name", type=str, default="/var/log/seagate/cortx/ha/cortx-lr2-cib.xml",
                        help="A node controlled by this device (Optional unless pcmk_host_check=static-list).")
    parser.add_argument("--auth", type=str,
                        help="IPMI Lan Auth type.")
    return parser.parse_args()


if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))

    try:
        Log.init(service_name="create_pacemaker_resources",
                 log_path="/var/log/seagate/cortx/ha", level="INFO")
        args = _parse_input_args()

        cib_xml = cib_get(args.cib_xml)
        stonith_config = {
            "resource_id" : args.resource_id,
            "ipaddr" : args.ipaddr,
            "login" : args.login,
            "passwd" : args.passwd,
            "node_name": args.node_name,
            "auth": args.auth
        }
        ha_group(cib_xml, stonith_config=stonith_config)

    except Exception as e:
        print(f"{traceback.format_exc()}, {e}")
