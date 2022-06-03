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


class K8SEventsConst:
    TYPE = 'type'
    RAW_OBJECT = 'raw_object'
    METADATA = 'metadata'
    NAME = 'name'
    LABELS ='labels'
    # cortx specific key for fetching machine id from event.
    # k8s event: ['raw_object']['metadata']['labels']['cortx.io/machine-id']
    LABEL_MACHINEID = 'cortx.io/machine-id'
    # TODO: CORTX-31875: check if pod has same label 'statefulset.kubernetes.io/pod-name'
    # k8s event: ['raw_object']['metadata']['labels']['statefulset.kubernetes.io/pod-name']
    LABEL_PODNAME = 'statefulset.kubernetes.io/pod-name'
    SPEC = 'spec'
    NODE_NAME = 'nodeName'
    PHASE = 'phase'
    RUNNING = 'Running'
    STATUS = 'status'
    CONDITIONS = 'conditions'
    READY = 'Ready'
    true = 'true'


class EventStates:
    ADDED = 'ADDED'
    MODIFIED = 'MODIFIED'
    DELETED = 'DELETED'


class AlertStates:
    ONLINE = 'online'
    OFFLINE = 'offline'
    FAILED = 'failed'

class K8SClientConst:
    PRETTY = 'pretty'
    LABEL_SELECTOR = 'label_selector'
    TIMEOUT_SECONDS = 'timeout_seconds'
    NODE = 'node'
    POD = 'pod'

    VAL_WATCH_TIMEOUT_DEFAULT = 5
