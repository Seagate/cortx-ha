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

"""
Implementation of standalone cluster checks.

Approach:
1. Initialize ClusterStatusPcs object.
2. Read ClusterLayout from component files.
3. Create ClusterTestAdapter and invoke favorite checks.

All checks here simply return a bool value. The decision what to do is
suposed to be done on higher level.
However, incidents and inconsistencies are logged to component logger.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Iterable, List, Callable
from ha.setup.cluster_validator.cluster_layout import ClusterLayout, ClusterLayoutJson
from ha.setup.cluster_validator.cluster_status import (ClusterCloneResource, ClusterStatusPcs)
from ha.const import COMPONENTS_CONFIG_DIR, RA_LOG_DIR
from ha.setup.cluster_validator.pcs_const import RESOURCE_ATTRIBUTES
from cortx.utils.log import Log


class ClusterTestAdapter():
    """Checks runner.

    Just create an object and call check_* methods.
    """
    def __init__(self, status: ClusterStatusPcs, layout: ClusterLayout):
        self.status = status
        self.layout = layout

    # TODO: ClusterLayout can be used later to retrieve the number once such
    # information is added there.
    def check_disabled_services(self, expected_number: int = 0) -> bool:
        """Check number of disabled services."""
        summary = self.status.get_summary()
        return summary.num_resources_disabled == expected_number

    # TODO: ClusterLayout can be used later to retrieve the number
    # Currently, assuming that the caller will provide it
    def check_number_of_nodes(self, expected_number: int) -> bool:
        """Check expected number of nodes configured."""
        summary = self.status.get_summary()
        return summary.num_nodes == expected_number

    def check_maintenance_mode(self, expected_state: bool = False) -> bool:
        """Check maintenance status."""
        # Assuming that maintenance mode is not specified in layout
        summary = self.status.get_summary()
        return summary.maintenance_mode == expected_state

    def check_stonith_state(self, expected_state: bool = False) -> bool:
        """Check stonith status."""
        # Assuming that stonith configuration is not specified in layout so far
        summary = self.status.get_summary()
        return summary.stonith_enabled == expected_state

    def check_quorum_state(self) -> bool:
        """Check that cluster has quorum."""
        # Assuming that cluster shall always have quorum
        summary = self.status.get_summary()
        return summary.quorum is True

    # NOTE: nodelist can be taken from ClusterLayout, but here some flexibility
    # may be required if cluster is big and only some parts require validation.
    def check_nodes_online(self, nodelist: Iterable[str]) -> bool:
        """Check that given nodes are online"""
        nodes_online = filter(lambda a: a.online, self.status.get_nodes())
        nodes_online_names = set(map(lambda a: a.name, nodes_online))
        return nodes_online_names == set(nodelist)

    def check_nodes_standby(self, nodelist: Iterable = None) -> bool:
        """
        Check whether nodes are in standby mode.

        Missing nodelist means that all existing nodes SHALL NOT be in
        standby mode - for the sake of usability.
        Nodes from nodelist are expected to be in standby mode - this is
        expected to be rare use case for the function.
        """
        standby_nodes = filter(lambda a: a.standby, self.status.get_nodes())
        if nodelist is None:
            return list(standby_nodes) == []

        standby_nodes_names = set(map(lambda a: a.name, standby_nodes))
        return standby_nodes_names.symmetric_difference(nodelist) == set()

    # TODO: This function requires refactoring to eliminate code duplication
    def check_nodes_maintenance(self, nodelist: Iterable = None) -> bool:
        """
        Check whether nodes are in maintenance mode.

        Missing nodelist means that all existing nodes SHALL NOT be in
        maintenance mode - for the sake of usability.
        Nodes from nodelist are expected to be in maintenance mode - this is
        expected to be rare use case for the function.
        """
        maintenance_nodes = filter(
            lambda a: a.maintenance, self.status.get_nodes())
        if nodelist is None:
            return list(maintenance_nodes) == []

        maintenance_nodes_names = set(map(lambda a: a.name, maintenance_nodes))
        return maintenance_nodes_names.symmetric_difference(nodelist) == set()

    # TODO: This function requires refactoring to eliminate code duplication
    def check_nodes_unclean(self, nodelist: Iterable = None) -> bool:
        """
        Check whether nodes are in unclean state.

        Missing nodelist means that all existing nodes SHALL NOT be in
        unclean state - for the sake of usability.
        Nodes from nodelist are expected to be in unclean state - this is
        expected to be rare use case for the function.
        """
        unclean_nodes = filter(lambda a: a.unclean, self.status.get_nodes())
        if nodelist is None:
            return list(unclean_nodes) == []

        unclean_nodes_names = set(map(lambda a: a.name, unclean_nodes))
        return unclean_nodes_names.symmetric_difference(nodelist) == set()

    def __compare_by_attribute(self, attr_name: str, expected_value: Any,
                               exceptions: Iterable[str] = None,) -> bool:
        exceptions = set() if exceptions is None else set(exceptions)
        all_resources = self.status.get_all_resources()
        target_set = filter(lambda a: getattr(a, attr_name)
                            == expected_value, all_resources)
        all_resources = map(lambda a: a.name, all_resources)
        target_set = map(lambda a: a.name, target_set)
        diff = set(all_resources).difference(target_set)
        return exceptions.symmetric_difference(diff) == set()

    def check_resources_failed(self, exceptions: Iterable[str] = None,
                               is_failed: bool = False) -> bool:
        """Check resources fail state.

        Take set of failed/not-failed resources.
        Check the difference with exceptions.
        """
        return self.__compare_by_attribute(RESOURCE_ATTRIBUTES.FAILED, is_failed, exceptions)

    def check_resources_managed(self, exceptions: Iterable[str] = None,
                                is_managed: bool = True) -> bool:
        """Check resources managed/unmanaged state.

        Take set of managed/unmanaged resources.
        Check the difference with exceptions.
        """
        return self.__compare_by_attribute(RESOURCE_ATTRIBUTES.MANAGED, is_managed, exceptions)

    def check_resources_role(self, exceptions: Iterable[str] = None,
                             expected_role: str = RESOURCE_ATTRIBUTES.STARTED) -> bool:
        """Check resources roles."""
        if exceptions is None:
            exceptions = []
        all_resources = self.status.get_all_resources()
        result = True
        for a_resource in all_resources:
            if isinstance(a_resource, ClusterCloneResource):
                for copy in a_resource.copies:
                    if copy.role != expected_role and copy.name not in exceptions:
                        Log.info(
                            f"Resource {a_resource.name}:{copy.name} state expected: {expected_role} actual: {copy.role}")
                        result = False
            else:
                if a_resource.role != expected_role and a_resource.name not in exceptions:
                    Log.info(
                        f"Resource {a_resource.name} state expected: {expected_role} actual: {a_resource.role}")
                    result = False
        return result

    def check_resource_layout(self) -> bool:
        """
        Check that all necessary resources are created.

        "Bad" resources are logged and skipped to check others.
        """
        check_res = True
        for res, desc in self.layout.resources.items():
            resource_list = []
            try:
                name_list = []
                # Counters is syntastic sugar to specify names for several
                # identical resources
                if desc[RESOURCE_ATTRIBUTES.PROVIDER][RESOURCE_ATTRIBUTES.COUNTERS]:
                    for counter in desc[RESOURCE_ATTRIBUTES.PROVIDER][RESOURCE_ATTRIBUTES.COUNTERS]:
                        name_list.append(f"{res}-{counter}")
                else:
                    name_list = [res]
                for res_name in name_list:
                    # Check that resource actually exists
                    if desc[RESOURCE_ATTRIBUTES.HA][RESOURCE_ATTRIBUTES.MODE] == RESOURCE_ATTRIBUTES.ACTIVE_ACTIVE:
                        if desc[RESOURCE_ATTRIBUTES.GROUP] != "":
                            resource = self.status.get_resource_from_cloned_group_by_name(res_name)
                            resource_list.append(resource)
                        else:
                            resource = self.status.get_clone_resource_by_name(res_name)
                            resource_list.extend(resource.copies)
                    else:
                        resource = self.status.get_unique_resource_by_name(res_name)
                        resource_list.append(resource)

                    if not resource_list:
                        Log.info(f"Resource {res_name} not found in status")
                        check_res = False
                        continue
            except Exception:
                check_res = False
                continue

            for a_resource in resource_list:
                # Check provider and service
                expected = "{}:{}".format(
                    desc[RESOURCE_ATTRIBUTES.PROVIDER][RESOURCE_ATTRIBUTES.NAME], desc[RESOURCE_ATTRIBUTES.PROVIDER][RESOURCE_ATTRIBUTES.SERVICE])
                actual = a_resource.resource_agent
                if expected != actual:
                    Log.info(
                        f"{res}: invalid resource agent is used {actual} instead of {expected}")
                    check_res = False

                try:
                    if desc[RESOURCE_ATTRIBUTES.GROUP] != a_resource.group:
                        Log.info(f'{res}: wrong group {a_resource.group} vs expected {desc[RESOURCE_ATTRIBUTES.GROUP]}')
                        check_res = False
                except KeyError:
                    Log.warn(f"{res} : Group is not defined.")
                # TODO: Location to be checked once component files become part of provisioning

        return check_res

    def check_nodes_configured(self) -> bool:
        """Compare expected set of nodes against existing one."""
        expected = set(self.layout.nodes)
        actual = set([node.name for node in self.status.get_nodes()])
        amount_ok = len(expected) == len(actual)
        if not amount_ok:
            Log.info("Amount of nodes does not correspond: {} layout vs {} actual". format(
                     len(expected), len(actual)))
        content_ok = expected == actual
        if not content_ok:
            Log.info("Expected set of nodes is not equal to actual set of nodes. Diff: {}".format(
                     expected.symmetric_difference(actual)))
        return amount_ok and content_ok


class TestExecutor:

    @staticmethod
    def _get_component_json_files(comp_files_dir: str = COMPONENTS_CONFIG_DIR) -> List[str]:
        path_to_files = Path(comp_files_dir)
        return list(map(str, path_to_files.glob("*.json")))

    @staticmethod
    def validate_cluster(node_list: list,
                         comp_files_dir: str = COMPONENTS_CONFIG_DIR,
                         executor: Callable[[str], tuple] = None) -> bool:
        """
        Perform cluster sanity-checks.

        A wrapper for many check functions to be called at once.

        Params:
            node_list: expected list of nodes in the cluster.
            comp_files_dir: directory where component json files are located.
            executor: Callable to invoke "pcs status xml". Used for tests.

        Returns:
            bool: result of sanity checks.

        Raises:
            FileNotFoundError: no component files found.
            ValidationStatusError: issues with ClusterStatus class.
            ValidationConfigError: issues with ClusterLayout init.
        """
        res = True

        status = ClusterStatusPcs(executor=executor)
        file_list = TestExecutor._get_component_json_files(comp_files_dir)
        if not file_list:
            raise FileNotFoundError(
                f"Component files were not found in {comp_files_dir}")
        layout = ClusterLayoutJson.from_json_file(file_list, node_list)
        validator = ClusterTestAdapter(status, layout)

        sub_res = validator.check_resource_layout()
        res &= sub_res
        if not sub_res:
            Log.info("Cluster resource layout does't correspond to component files config.")

        sub_res = validator.check_quorum_state()
        res &= sub_res
        if not sub_res:
            Log.info("Cluster doesn't have quorum. This is a showstopper!")

        # NOTE: Change if this assumption is incorrect or even remove this!
        sub_res = validator.check_stonith_state(expected_state=False)
        res &= sub_res
        if not sub_res:
            Log.info("Stonith is not disabled for some reason. Check expected configuration.")

        sub_res = validator.check_maintenance_mode(expected_state=False)
        res &= sub_res
        if not sub_res:
            Log.info("Cluster maintenance mode is on. Cluster check expected configuration.")

        sub_res = validator.check_nodes_online(nodelist=node_list)
        res &= sub_res
        if not sub_res:
            Log.info("Some nodes are offline. Check HA logs for details.")

        sub_res = validator.check_nodes_standby()
        res &= sub_res
        if not sub_res:
            Log.info("Some nodes are in standby. Check HA logs for details.")

        sub_res = validator.check_nodes_maintenance()
        res &= sub_res
        if not sub_res:
            Log.info(
                "Some nodes are in maintenance mode. Cluster doesn't function normally.")

        sub_res = validator.check_nodes_unclean()
        res &= sub_res
        if not sub_res:
            Log.info(
                "Some nodes are in unclean state. Cluster doesn't function normally.")

        sub_res = validator.check_resources_failed()
        res &= sub_res
        if not sub_res:
            Log.info("Some resources are failed. Cluster doesn't function normally.")

        sub_res = validator.check_resources_role(expected_role="Started")
        res &= sub_res
        if not sub_res:
            Log.info("Some resources are not started. Cluster doesn't function normally.")

        return res

    @staticmethod
    def parse_args() -> Any:
        parser = argparse.ArgumentParser(
            description="Perform sanity-check of cluster configuration")
        parser.add_argument("--nodes", type=str, nargs="+",
                            help="List of cluster nodes expected by setup")
        parser.add_argument("--comp-dir", type=str, default=COMPONENTS_CONFIG_DIR,
                            help="List of cluster nodes expected by setup")
        return parser.parse_args()


def _main():
    args = TestExecutor.parse_args()

    Log.init(service_name="validate_cluster",
             log_path=RA_LOG_DIR, level="INFO")

    ret = TestExecutor.validate_cluster(node_list=args.nodes, comp_files_dir=args.comp_dir)
    sys.exit(ret)
