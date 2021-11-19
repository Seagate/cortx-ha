#!/usr/bin/env python3

# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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
import unittest
from ha.setup.cluster_validator.cluster_layout import ClusterLayoutJson
from ha.setup.cluster_validator.cluster_status import (ClusterStatusPcs, ClusterResource,
                                                       ClusterCloneResource)
from ha.setup.cluster_validator.cluster_test import ClusterTestAdapter, validate_cluster
from cortx.utils.log import Log

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def run_cmd(cmd: str) -> tuple:
    # I hope this will work everywhere.
    with open(f"{DIR_PATH}/normal_status.xml", "r") as f:
        output = f.read()
    return (output, 0, 0)


def run_cmd_groups(cmd: str) -> tuple:
    with open(f"{DIR_PATH}/all-combinations.xml", "r") as f:
        output = f.read()
    return (output, 0, 0)


class TestClusterLayout(unittest.TestCase):
    def test_component_import(self):
        """
        Test ClusterLayout creation from JSON component file.

        This test can be used to control that component files are
        compatible with ClusterLayout parser.

        The idea is to read all components succesfully and just pretty print
        the object for manual validation. Though, some automated test
        procedure would be welcome here.
        """
        prefix = f"{DIR_PATH}/../../../../conf/etc/v2/components/"
        components = ["uds.json",
                      "csm.json",
                      "free-space-monitor.json",
                      "hare-hax.json",
                      "mgmt-vip.json",
                      "motr.json",
                      "s3servers.json",
                      "sspl.json",
                      ]
        file_list = [prefix + s for s in components]
        node_list = ["srvnode-1", "srvnode-2", "srvnode-3"]
        layout = ClusterLayoutJson.from_json_file(file_list, node_list)
        self.assertNotEqual(layout, None)


class TestClusterStatus(unittest.TestCase):
    """Test pcs status parsing functions."""

    def test_get_all_resources(self):
        status = ClusterStatusPcs(executor=run_cmd)
        self.assertNotEqual(status, None)
        resources = status.get_all_resources()
        self.assertEqual(type(resources), list)
        self.assertEqual(len(resources), 3)
        # TODO: add more checks

    def test_get_all_resources_2(self):
        """Dedicated test for temporarily purposes."""
        status = ClusterStatusPcs(executor=run_cmd_groups)
        self.assertNotEqual(status, None)
        resources = status.get_all_resources()
        self.assertEqual(type(resources), list)
        print(resources)

    def test_get_clone_resource_by_name(self):
        status = ClusterStatusPcs(executor=run_cmd)
        self.assertNotEqual(status, None)
        res = status.get_clone_resource_by_name("test-cl")
        self.assertTrue(isinstance(res, ClusterCloneResource))
        self.assertEqual(res.name, "test-cl")
        self.assertEqual(len(res.copies), 2)

        res = status.get_clone_resource_by_name("does-not-exist")
        self.assertEqual(res, None)

    def test_get_unique_resource_by_name(self):
        status = ClusterStatusPcs(executor=run_cmd_groups)
        self.assertNotEqual(status, None)
        res = status.get_unique_resource_by_name("test-4")
        self.assertTrue(isinstance(res, ClusterResource))
        self.assertEqual(res.name, "test-4")
        self.assertEqual(res.group, "")

        res = status.get_unique_resource_by_name("does-not-exist")
        self.assertEqual(res, None)

        status = ClusterStatusPcs(executor=run_cmd_groups)
        self.assertNotEqual(status, None)
        res = status.get_unique_resource_by_name("test-5")
        self.assertTrue(isinstance(res, ClusterResource))
        self.assertEqual(res.name, "test-5")
        self.assertEqual(res.group, "alone")

        res = status.get_unique_resource_by_name("test-3")
        self.assertEqual(res, None)

    def test_get_resource_from_cloned_group_by_name(self):
        status = ClusterStatusPcs(executor=run_cmd_groups)
        self.assertNotEqual(status, None)
        res = status.get_resource_from_cloned_group_by_name("test-1")
        self.assertNotEqual(res, None)
        self.assertEqual(res.name, "test-1")
        self.assertEqual(res.group, "io_group")
        self.assertTrue(res.clone)

    def test_get_nodes(self):
        status = ClusterStatusPcs(executor=run_cmd)
        self.assertNotEqual(status, None)

        nodes = status.get_nodes()
        self.assertEqual(len(nodes), 2)

        expected = ["ssc-vm-1550.colo.seagate.com",
                    "ssc-vm-1551.colo.seagate.com", ]
        names = set()
        for node in nodes:
            self.assertTrue(node.online)
            self.assertFalse(node.standby)
            self.assertFalse(node.unclean)
            self.assertEqual(node.resources_running, 2)
            names.add(node.name)

        self.assertEqual(names, set(expected))

    def test_get_summary(self):
        status = ClusterStatusPcs(executor=run_cmd)
        self.assertNotEqual(status, None)
        summary = status.get_summary()
        self.assertTrue(summary.quorum)
        self.assertFalse(summary.stonith_enabled)
        self.assertFalse(summary.maintenance_mode)
        self.assertEqual(summary.num_nodes, 2)
        self.assertEqual(summary.num_resources_configured, 4)
        self.assertEqual(summary.num_resources_disabled, 0)


class TestClusterValidation(unittest.TestCase):
    """Run cluster checks on simple examples."""

    def test_check_nodes_configured(self):
        status = ClusterStatusPcs(executor=run_cmd_groups)
        node_list = ["localhrost", "localfrost"]
        layout = ClusterLayoutJson.from_json_file([], node_list)
        validator = ClusterTestAdapter(status, layout)
        self.assertTrue(validator.check_nodes_configured())

    def test_check_resource_layout(self):
        status = ClusterStatusPcs(executor=run_cmd_groups)
        node_list = ["localhrost", "localfrost"]
        file_list = [f"{DIR_PATH}/all-combinations.json"]
        layout = ClusterLayoutJson.from_json_file(file_list, node_list)
        validator = ClusterTestAdapter(status, layout)
        self.assertTrue(validator.check_resource_layout())

    def test_check_resources_role(self):
        status = ClusterStatusPcs(executor=run_cmd)
        validator = ClusterTestAdapter(status, None)
        self.assertTrue(validator.check_resources_role())

    def test_check_resources_failed(self):
        status = ClusterStatusPcs(executor=run_cmd)
        validator = ClusterTestAdapter(status, None)
        self.assertTrue(validator.check_resources_failed())

    def test_check_resources_managed(self):
        status = ClusterStatusPcs(executor=run_cmd)
        validator = ClusterTestAdapter(status, None)
        self.assertTrue(validator.check_resources_managed())

    def test_check_nodes_unclean(self):
        status = ClusterStatusPcs(executor=run_cmd_groups)
        validator = ClusterTestAdapter(status, None)
        self.assertTrue(validator.check_nodes_unclean())

    def test_check_nodes_maintenance(self):
        status = ClusterStatusPcs(executor=run_cmd_groups)
        validator = ClusterTestAdapter(status, None)
        self.assertTrue(validator.check_nodes_maintenance())

    def test_check_nodes_standby(self):
        status = ClusterStatusPcs(executor=run_cmd_groups)
        validator = ClusterTestAdapter(status, None)
        self.assertTrue(validator.check_nodes_standby())

    def test_check_nodes_online(self):
        status = ClusterStatusPcs(executor=run_cmd)
        validator = ClusterTestAdapter(status, None)
        nodes = ["ssc-vm-1550.colo.seagate.com", "ssc-vm-1551.colo.seagate.com"]
        self.assertTrue(validator.check_nodes_online(nodelist=nodes))

    def test_validation_wrapper(self):
        node_list = ["localhrost", "localfrost"]
        self.assertFalse(validate_cluster(node_list=node_list,
                                          comp_files_dir=DIR_PATH, executor=run_cmd_groups))


class TestValidationWithComponentFiles(unittest.TestCase):
    """Run complex validation routines imitating real cluster."""


if __name__ == '__main__':
    Log.init(service_name="test_cluster_validation.py",
             log_path=".", level="INFO")
    unittest.main()
