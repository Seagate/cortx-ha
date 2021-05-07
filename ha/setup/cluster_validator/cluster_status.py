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
Module to provide standalone interface to cluster status.
"""

import re
from typing import Callable, List, NamedTuple, Union, Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from ha.core.error import SetupError, HA_CLUSTER_CONFIG_ERROR
from ha.execute import SimpleCommand


class ValidationStatusError(SetupError):
    """Cluster status format is invalid."""
    def __init__(self, desc=None):
        _desc = "Error when parsing cluster status" if desc is None else desc
        _message_id = HA_CLUSTER_CONFIG_ERROR
        _rc = 1
        super().__init__(rc=_rc, desc=_desc, message_id=_message_id)


ClusterSummary = NamedTuple("ClusterSummary", [
    ("maintenance_mode", bool),
    ("quorum", bool),
    ("stonith_enabled", bool),
    ("num_nodes", int),
    ("num_resources_configured", int),
    ("num_resources_disabled", int)
])

ClusterNode = NamedTuple("ClusterNode", [
    ("name", str),
    ("online", bool),
    ("standby", bool),
    ("maintenance", bool),
    ("unclean", bool),
    ("resources_running", int),
])

ClusterResource = NamedTuple("ClusterResource", [
    ("name", str),
    ("clone", bool),
    ("resource_agent", str),
    ("role", str),  # Enum may be needed here
    ("enabled", bool),
    ("failed", bool),
    ("managed", bool),
    ("failure_ignored", bool),
    ("location", List[str]),
    ("group", str),
])

# NOTE: Non-empty group attribute indicates that it is not a resource, but a cloned group
ClusterCloneResource = NamedTuple("ClusterCloneResource", [
    ("name", str),
    ("managed", bool),
    ("unique", bool),
    ("failed", bool),
    ("failure_ignored", bool),
    ("copies", List[ClusterResource]),
    ("group", str),
])


class ClusterStatusPcs():
    """Implementation of interface for pcs status --xml command."""

    def __init__(self, executor: Callable[[str], tuple] = None):
        """Call `pcs status` and init XML object for further parsing"""
        if not executor:
            executor = SimpleCommand().run_cmd
        output, _, _ = executor("pcs status --full xml")
        self.tree = ElementTree.fromstring(output)

    @staticmethod
    def _to_bool(value: str) -> bool:
        return value == "true"

    def get_nodes(self) -> List[ClusterNode]:
        """Return list of nodes."""
        node_elements = self.tree.findall("./nodes/node")
        nodes = []
        try:
            b = self._to_bool
            for n in node_elements:
                nodes.append(ClusterNode(
                    name=n.attrib["name"],
                    online=b(n.attrib["online"]),
                    maintenance=b(n.attrib["maintenance"]),
                    standby=b(n.attrib["standby"]),
                    unclean=b(n.attrib["unclean"]),
                    resources_running=int(n.attrib["resources_running"]),
                ))
        except Exception as err:
            raise ValidationStatusError(
                "Parsed XML doesn't contain required attributes") from err
        return nodes

    def get_summary(self) -> ClusterSummary:
        """Return summary information about cluster for further checks."""
        b = self._to_bool
        e = self.tree.find("./summary")
        try:
            res = ClusterSummary(
                maintenance_mode=b(
                    e.find("./cluster_options").attrib["maintenance-mode"]),
                quorum=b(e.find("./current_dc").attrib["with_quorum"]),
                stonith_enabled=b(
                    e.find("./cluster_options").attrib["stonith-enabled"]),
                num_nodes=int(e.find("./nodes_configured").attrib["number"]),
                num_resources_configured=int(
                    e.find("./resources_configured").attrib["number"]),
                num_resources_disabled=int(
                    e.find("./resources_configured").attrib["disabled"]),
            )
        except Exception as err:
            raise ValidationStatusError(
                "Parsed XML contains unexpected summary format") from err
        return res

    def _resource_from_xml(self, elem: Element, is_clone: bool = False, group: str = "") -> ClusterResource:
        """Convert XML element to ClusterResource."""
        assert elem.tag == "resource"
        b = self._to_bool
        try:
            locations: List[str] = []
            if int(elem.attrib["nodes_running_on"]) > 0:
                locations = elem.find("./node").attrib["name"]
            #  "ocf::heartbeat:Dummy" -> "ocf:heartbeat:Dummy"
            res_agent = elem.attrib["resource_agent"].split(":")
            res_agent = "{}:{}:{}".format(res_agent[0], res_agent[2], res_agent[3])
            return ClusterResource(
                name=elem.attrib["id"],
                clone=is_clone,
                resource_agent=res_agent,
                role=elem.attrib["role"],
                enabled=b(elem.attrib["active"]),
                failed=b(elem.attrib["failed"]),
                managed=b(elem.attrib["managed"]),
                failure_ignored=b(elem.attrib["failure_ignored"]),
                location=locations,
                group=group,
            )
        except Exception as err:
            raise ValidationStatusError(
                "Parsed XML doesn't contain expected attributes") from err

    def get_resource_from_cloned_group_by_name(self, name: str) -> Optional[ClusterResource]:
        """Get resource that is located in cloned group."""

        for group in self.tree.findall("./resources/clone/group"):
            res = group.find(f"./resource[@id='{name}']")
            if res is not None:
                return self._resource_from_xml(res, is_clone=True, group=group.get("id").split(":")[0])
        return None

    def get_unique_resource_by_name(self, name: str) -> Optional[ClusterResource]:
        """
        Get resource info by name.

        This works with normal resources, resources within groups.
        """
        paths = [f"./resources/resource[@id='{name}']",
                 f"./resources/group/resource[@id='{name}']",
                 f"./resources/clone/group/resource[@id='{name}']"]
        res_elems = []
        for xpath in paths:
            elems = self.tree.findall(xpath) or []
            res_elems.extend(elems)

        if len(res_elems) > 1:
            raise ValidationStatusError(
                f"Unique resource {name} requested, but several matches found")
        if not res_elems:
            return None

        # To determine group name - we need to find parent node
        group_name = ""
        is_clone = False
        parent = self.tree.find(f"./resources//resource[@id='{name}']/..")
        if parent and parent.tag == "group":
            group_name = parent.get("id")
            clone = self.tree.find(f"./resources//group[@id='{group_name}']/..")
            is_clone = clone is not None

        return self._resource_from_xml(res_elems[0], is_clone=is_clone, group=group_name)

    def _group_from_xml(self,
                        elem: Element,
                        is_clone: bool = False
                        ) -> List[ClusterResource]:
        assert elem.tag == "group"
        rcs: List[Union[ClusterCloneResource, ClusterResource]] = []
        for e in elem:
            if e.tag == "clone":
                # rcs.append(self._clone_from_xml(e, elem.attrib["id"]))
                raise NotImplementedError("Clones are not supposred within groups")
            group_name = elem.attrib["id"].split(":")[0]
            if e.tag == "resource":
                rcs.append(self._resource_from_xml(
                           e, group=group_name, is_clone=is_clone))
            else:
                raise NotImplementedError(f"Group subelement {e.tag} is not supported")
        return rcs

    def _clone_from_xml(self, elem: Element, group: str = "") -> ClusterCloneResource:
        """Convert XML status to ClusterCloneResource"""
        assert elem.tag == "clone"
        rcs = []
        b = self._to_bool
        for r in elem:
            if r.tag == "resource":
                rcs.append(self._resource_from_xml(r, is_clone=True, group=group))
            elif r.tag == "group":
                rcs.extend(self._group_from_xml(r, is_clone=True))
                # Cloned group XML contains several groups inside - interested only in one copy
                group = group or r.attrib["id"].split(":")[0]
                break
            else:
                raise NotImplementedError(f"Clone subelement {r.tag} is not supported")

        return ClusterCloneResource(
            name=re.sub("-clone$", "", elem.attrib["id"]),
            managed=b(elem.attrib["managed"]),
            unique=b(elem.attrib["unique"]),
            failed=b(elem.attrib["failed"]),
            failure_ignored=b(elem.attrib["failure_ignored"]),
            copies=rcs,
            group=group,
        )

    def get_clone_resource_by_name(self, name: str) -> Optional[ClusterCloneResource]:
        """Get clone resource full info."""
        clone_name = name + "-clone"
        clone_elem = self.tree.findall(
            f"./resources/clone[@id='{clone_name}']")
        if len(clone_elem) > 1:
            raise ValidationStatusError(
                f"One clone {name} is expected, but several matches found")
        if not clone_elem:
            return None
        return self._clone_from_xml(clone_elem[0])

    def get_all_resources(self) -> List[Union[ClusterResource, ClusterCloneResource]]:
        """Parse all resources from status XML."""
        resources = self.tree.find("./resources")
        resources = resources or []
        result: List[Union[ClusterResource, ClusterCloneResource]] = []
        for res in resources:
            if res.tag == "clone":
                result.append(self._clone_from_xml(res))
            elif res.tag == "group":
                result.extend(self._group_from_xml(res))
            elif res.tag == "resource":
                result.append(self._resource_from_xml(res))
            else:
                raise NotImplementedError(f"Resource with type {res.tag} is not supported")
        return result
