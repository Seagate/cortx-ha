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

"""Module to do pre-upgrade routines in scope of Disruptive Upgrade feature."""

import os
import sys
import shlex
import time
import argparse
import subprocess
import traceback
import tarfile
from glob import glob
from shutil import copytree, rmtree
from time import gmtime, strftime
from typing import Any

from cortx.utils.log import Log
from ha.const import (BACKUP_DEST_DIR_CONF, BACKUP_DEST_DIR_CONSUL, CONFIG_DIR, PCS_RESOURCE_REFRESH, LIST_PCS_RESOURCES,
                    PCS_CLUSTER_STANDBY, RA_LOG_DIR, PCS_CLEANUP, PCS_CLUSTER_STATUS, PCS_FAILCOUNT_STATUS, PCS_DELETE_RESOURCE)
from ha.core.error import UpgradeError
from ha.execute import SimpleCommand
from ha.core.config.config_manager import ConfigManager

def backup_consul(filename: str = "consul-kv-dump.json", dst: str = BACKUP_DEST_DIR_CONSUL) -> None:
    """
    Backup Consul KV.

    Parameters:
        filename: Consul dump file
        dst: Directory with to backup Consul dump

    Return:
        None

    Exceptions:
        UpgradeError
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
        raise UpgradeError("Consul export failed with error {}".format(cp.stderr.decode()))

def backup_configuration(src: str = CONFIG_DIR, dst: str = BACKUP_DEST_DIR_CONF) -> None:
    """
    Backup HA configuration.

    Parameters:
        src: HA configs location
        dst: Directory with HA config backup

    Return:
        None

    Exceptions:
        UpgradeError
    """
    Log.info(f"Backup HA configuration from {src} to {dst}")
    try:
        if os.path.exists(dst):
            rmtree(dst)
        copytree(src, dst)
    except Exception as err:
        raise UpgradeError("Failed to create backup of HA config")

def cluster_standby_mode() -> None:
    """
    Put cluster to standby mode.

    Note: this function may be replaced by Cluster Manager call.

    Exceptions:
        UpgradeError
    """
    Log.info("Set cluster to standby mode")
    Log.info("Please wait, standby can take max 20 to 30 min.")
    standby_cmd = f"{PCS_CLUSTER_STANDBY} --wait=1800"
    try:
        SimpleCommand().run_cmd(standby_cmd)
    except Exception as err:
        raise UpgradeError("Cluster standby operation failed")

def _get_resource_list() -> list:
    """Get list of resource"""
    resources: list = []
    # clear history before getting list of resource
    SimpleCommand().run_cmd(PCS_RESOURCE_REFRESH)
    output, _, _ = SimpleCommand().run_cmd(LIST_PCS_RESOURCES, check_error=False)
    if "NO resources" in output:
        return resources
    for resource in output.split("\n"):
        res = resource.split(":")[0]
        if res != "" and res not in resources:
            resources.append(res)
    return resources

def delete_resources() -> None:
    """
    Delete pacemaker resources.

    Exceptions:
        UpgradeError
    """
    try:
        resources = _get_resource_list()
        Log.info(f"Going to delete following resources: {resources}")
        for r in resources:
            Log.info(f"Deleting resource {r}")
            SimpleCommand().run_cmd(PCS_DELETE_RESOURCE.replace("<resource>", r))
        SimpleCommand().run_cmd(PCS_CLEANUP)
        Log.info("Wait 2 min till all resource deleted.")
        is_resource_deleted(120)
    except Exception as err:
        raise UpgradeError("Resource deletion failed")

def check_cluster_health() -> None:
    """ Check cluster status and make sure cluster is healthy """
    # Check if cluster running
    _, _, rc = SimpleCommand().run_cmd(PCS_CLUSTER_STATUS, check_error=False)
    if rc != 0:
        raise UpgradeError("Cluster is not running on current node")
    output, _, _ = SimpleCommand().run_cmd(PCS_FAILCOUNT_STATUS)
    if "INFINITY" in output:
        raise UpgradeError(f"Cluster is not stable, some resource are not healthy. {output}")

def is_resource_deleted(timeout) -> None:
    """ Check if pre disruptive upgrade is successful """
    base_wait = 5
    while timeout > 0:
        resources = _get_resource_list()
        Log.info(f"Waiting for {str(timeout)} to delete resources {resources}.")
        if len(resources) == 0:
            Log.info("All resource deleted successfully.")
            break
        time.sleep(base_wait)
        timeout -= base_wait
    resources = _get_resource_list()
    if len(resources) != 0:
        raise UpgradeError(f"Failed to delete resource. Remaining resources {resources} ...")

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
    ConfigManager.init(log_name="pre_disruptive_upgrade",
                                        log_path=RA_LOG_DIR, level="INFO")
    Log.info("Script invoked as executable with params: {}".format(vars(args)))
    check_cluster_health()
    if args.backup_consul:
        backup_consul()
    backup_configuration()
    cluster_standby_mode()
    delete_resources()

if __name__ == "__main__":
    try:
        _main()
        sys.stdout.write("Successfully completed pre disruptive upgrade")
        sys.exit(0)
    except Exception as e:
        Log.error(f"Failed pre disruptive upgrade. Error: {e}. Traceback:\n {traceback.format_exc()}")
        sys.stderr.write("Failed to perform pre disruptive upgrade. Please check log for more detail.")
        sys.exit(1)
