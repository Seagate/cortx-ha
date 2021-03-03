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

"""Module to do pre-upgrade routines in scope of Disruptive Upgrade feature."""

import argparse
import os
import shlex
import subprocess
import tarfile
from glob import glob
from shutil import copytree, rmtree
from time import gmtime, strftime
from typing import Any
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from cortx.utils.log import Log
from ha.const import (BACKUP_DEST_DIR_CONF, BACKUP_DEST_DIR_CONSUL,
                      CONFIG_DIR, RA_LOG_DIR)
from ha.core.error import PreRequisiteUpgradeError
from ha.execute import SimpleCommand


def backup_consul(filename: str = "consul-kv-dump.json", dst: str = BACKUP_DEST_DIR_CONSUL) -> None:
    """
    Backup Consul KV.

    Parameters:
        filename: Consul dump file
        dst: Directory with to backup Consul dump

    Return:
        None

    Exceptions:
        PreRequisiteUpgradeError
    """
    consul_kv_dump = os.path.join(dst, filename)

    if os.path.exists(consul_kv_dump):
        for archive in glob(f"{dst}/*.tar.gz"):
            os.remove(archive)

        # Save previous one
        timestamp = strftime("%Y%m%d%H%M%S", gmtime())
        archive_name = os.path.join(dst, f"{consul_kv_dump}.{timestamp}.tar.gz")
        Log.info(f"Backup existing {consul_kv_dump} to {archive_name}")
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add(consul_kv_dump)
    else:
        os.makedirs(dst, exist_ok=True)

    consul_export_cmd = "consul kv export > {}".format(shlex.quote(consul_kv_dump))
    cp = subprocess.run(consul_export_cmd, shell=True, stderr=subprocess.PIPE)
    if cp.returncode:
        raise PreRequisiteUpgradeError("Consul export failed with error {}".format(cp.stderr.decode()))


def backup_configuration(src: str = CONFIG_DIR, dst: str = BACKUP_DEST_DIR_CONF) -> None:
    """
    Backup HA configuration.

    Parameters:
        src: HA configs location
        dst: Directory with HA config backup

    Return:
        None

    Exceptions:
        PreRequisiteUpgradeError
    """
    Log.info(f"Backup HA configuration from {src} to {dst}")
    try:
        if os.path.exists(dst):
            rmtree(dst)
        copytree(src, dst)
    except Exception as err:
        raise PreRequisiteUpgradeError("Failed to create backup of HA config") from err


def cluster_standby_mode() -> None:
    """
    Put cluster to standby mode.

    Note: this function may be replaced by Cluster Manager call.

    Exceptions:
        PreRequisiteUpgradeError
    """
    Log.info("Set cluster to standby mode")
    standby_cmd = "pcs node standby --all --wait=600"
    try:
        SimpleCommand().run_cmd(standby_cmd)
    except Exception as err:
        raise PreRequisiteUpgradeError("Cluster standby operation failed") from err


def _get_cib_xml() -> Element:
    """Call `pcs cluster cib` and return XML object for further parsing."""
    output, _, _ = SimpleCommand().run_cmd("pcs cluster cib")
    return ElementTree.fromstring(output)


def delete_resources() -> None:
    """
    Delete pacemaker resources.

    Exceptions:
        PreRequisiteUpgradeError
    """
    try:
        root = _get_cib_xml()
        resources = [e.attrib["id"] for e in root.findall(".//lrm_resource")
                     if "id" in e.attrib]
        Log.info(f"Going to delete following resources: {resources}")

        for r in resources:
            Log.info(f"Deleting {r}")
            SimpleCommand().run_cmd(f"pcs resource delete {r}")
    except Exception as err:
        raise PreRequisiteUpgradeError("Resource deletion failed") from err


def _parse_arguments() -> Any:
    """
    Parse and validate input arguments passed by mini-provisioner or CLI.

    Return:
        argparse namespace
    """
    parser = argparse.ArgumentParser(description="Does pre-upgrade routines")
    parser.add_argument("--backup-consul", action="store_true", help="Do consul backup")
    return parser.parse_args()


def _main() -> None:
    args = _parse_arguments()

    Log.init(service_name="pre_disruptive_upgrade", log_path=RA_LOG_DIR, level="INFO")

    Log.info("Script invoked as executable with params: {}".format(vars(args)))

    if args.backup_consul:
        backup_consul()

    backup_configuration()

    cluster_standby_mode()

    delete_resources()


if __name__ == "__main__":
    _main()
