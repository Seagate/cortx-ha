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


class ClusterCreateError(Exception):

    """Exception to indicate that cluster can't be created due to some error."""


class ClusterAuthError(ClusterCreateError):
    """

    Exception to indicate that authorization procedure failed.
    """


class ClusterSetupError(ClusterCreateError):
    """Exception to indicate that cluster setup procedure failed."""


def cluster_auth(username, password, nodelist):
    """
    Authorize cluster nodes.

    Parameters:
            username - just a user name to make cluster authorization
            password - just a password for aforementioned user
            nodelist - List with nodes which to authorize

    Returns: None.

    Exceptions:
        ClusterCreateError: generic exception to catch all creation-related
        problems.
        ClusterAuthError: failure happened during setup operation.
    """
    nodes = " ".join(nodelist)
    cmd_auth = f"pcs cluster auth -u {username} -p {password} {nodes}"
    try:
        SimpleCommand().run_cmd(cmd_auth)
    except Exception:
        raise ClusterAuthError(f"Failed to authorize the nodes: {nodes}")


def cluster_create(cluster_name, nodelist, enable=True, put_standby=True):
    """
    Create cluster on given nodes. Enables and starts cluster if needed.

    Parameters:
        cluster_name    - name of the cluster to be created
        nodelist        - List with nodes where setup the cluster
        enable          - whether cluster service shall start on boot
        put_standby     - whether [nodeslist] shall be put to standby mode

    Returns: None.

    Exceptions:
        ClusterCreateError: generic exception to catch all creation-related
        problems.
        ClusterSetupError: failure happened during setup operation.
    """
    nodes = " ".join(nodelist)
    cmd_setup = f"pcs cluster setup --start --name {cluster_name} {nodes}"
    cmd_standby = f"pcs node standby {nodes}"
    cmd_stonith = "pcs property set stonith-enabled=False"
    cmd_enable = f"pcs cluster enable {nodes}"

    cmdlist = [cmd_setup]
    if enable:
        cmdlist.append(cmd_enable)
    if put_standby:
        cmdlist.append(cmd_standby)
    cmdlist.append(cmd_stonith)
    try:
        for s in cmdlist:
            SimpleCommand().run_cmd(s)
    except Exception:
        raise ClusterSetupError("Failed to setup the cluster")


def _parse_input_args():
    """
    Parse and validate input arguments passed by mini-provisioner or CLI.

    Returns dictonary with context.
    """
    parser = argparse.ArgumentParser(description="Creates pacemaker cluster")
    parser.add_argument("--cluster",
                        default="cortx-lr2",
                        type=str,
                        help="Cluster name")
    parser.add_argument("--username",
                        required=True,
                        type=str,
                        help="User to be used for cluster auth")
    parser.add_argument("--password",
                        required=True,
                        type=str,
                        help="Password to be used for cluster auth")
    parser.add_argument("--standby",
                        action='store_true',
                        help="Put nodes into standby on cluster creation")
    # Nodes to setup cluster can be entered via file or via parameters
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("nodelist",
                       type=str,
                       nargs="*",
                       default=[],
                       help="List of nodes where cluster can be created")
    group.add_argument("--nodefile",
                       required=False,
                       type=str,
                       help="File with list of nodes")
    return parser.parse_args()


def _read_file_list(filename):
    nodelist = []
    with open(filename, "r") as f:
        nodelist = f.read().splitlines()
    return nodelist


def _main():
    # Workaround to make SimpleCommand work, not crash
    Log.init(service_name="create_cluster",
             log_path="/var/log/seagate/cortx/ha",
             level="INFO")

    args = _parse_input_args()
    nodelist = args.nodelist if args.nodelist else _read_file_list(
        args.nodefile)
    if not nodelist:
        raise ValueError("node list shall not be empty")
    cluster_auth(args.username, args.password, nodelist)
    cluster_create(args.cluster, nodelist, put_standby=args.standby)


if __name__ == "__main__":
    _main()
