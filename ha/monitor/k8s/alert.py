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

from collections import namedtuple


class K8sAlert:
    def __init__(self):
        self._resource_type = None
        self._resource_name = None
        self._event_type = None
        self._k8s_container = None
        self._generation_id = None
        self._node = None
        self._is_status = False
        self._timestamp = None

    @property
    def resource_type(self):
        return self._resource_type

    @resource_type.setter
    def resource_type(self, res_type):
        self._resource_type = f"{res_type}"

    @property
    def resource_name(self):
        return self._resource_name

    @resource_name.setter
    def resource_name(self, res_name):
        self._resource_name = res_name

    @property
    def event_type(self):
        return self._event_type

    @event_type.setter
    def event_type(self, event_type):
        self._event_type = event_type

    @property
    def k8s_container(self):
        return self._k8s_container

    @k8s_container.setter
    def k8s_container(self, name):
        self._k8s_container = name

    @property
    def generation_id(self):
        return self._generation_id

    @generation_id.setter
    def generation_id(self, name):
        self._generation_id = name

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, name):
        self._node = name

    @property
    def is_status(self):
        return self._is_status

    @is_status.setter
    def is_status(self, status):
        self._is_status = status

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, time):
        self._timestamp = time

    def to_dict(self):
        return vars(self)

    @staticmethod
    def to_alert(obj_dict):
        return namedtuple('K8sAlert', obj_dict.keys())(*obj_dict.values())
