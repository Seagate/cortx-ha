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


class COMMNANDS:
    PCS_STATUS_XML = "pcs status --full xml"


class CLUSTER_ATTRIBUTES:
    NAME = "name"
    ONLINE = "online"
    MAINTENANCE = "maintenance"
    STANDBY = "standby"
    UNCLEAN = "unclean"
    RESOURCES_RUNNING = "resources_running"
    SUMMARY = "summary"
    CLUSTER_SUMMARY = "ClusterSummary"
    CLUSTER_NODE = "ClusterNode"
    CLUSTER_RESOURCE = "ClusterResource"
    CLUSTER_CLONE_RESOURCE = "ClusterCloneResource"
    CLUSTER_OPTIONS = "cluster_options"
    RESOURCES_CONFIGURED = "resources_configured"
    NODES_CONFIGURED = "nodes_configured"
    NUM_RESOURCES_CONFIGURED = "num_resources_configured"
    NUM_RESOURCES_DISABLED = "num_resources_disabled"
    MAINTENANCE_MODE = "maintenance-mode"
    QUORUM = "quorum"
    WITH_QUORUM = "with_quorum"
    STONITH_ENABLED = "stonith-enabled"
    NUMBER = "number"
    DISABLED = "disabled"
    NODE = "node"
    NUM_NODES = "num_nodes"
    RESOURCE = "resource"
    RESOURCES = "resources"
    CURRENT_DC = "current_dc"


class RESOURCE_ATTRIBUTES:
    ID = "id"
    NAME = "name"
    ROLE = "role"
    ENABLED = "enabled"
    ACTIVE = "active"
    FAILED = "failed"
    MANAGED = "managed"
    FAILURE_IGNORED = "failure_ignored"
    GROUP = "group"
    CLONE = "clone"
    UNIQUE = "unique"
    RESOURCE_AGENT = "resource_agent"
    LOCATION = "location"
    COPIES = "copies"
    NODES_RUNNING_ON = "nodes_running_on"
    PROVIDER = "provider"
    SERVICE = "service"
    COUNTERS = "counters"
    STARTED = "Started"
    HA = "ha"
    MODE = "mode"
    ACTIVE_ACTIVE = "active_active"


