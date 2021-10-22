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


from ha.monitor.k8s.error import NotSupportedObjectError


class ObjectMap:
    _function_map = {
        'node': 'list_node',
        'pod': 'list_pod_for_all_namespaces'
    }

    @staticmethod
    def get_subscriber_func(object):
        if object in ObjectMap._function_map:
            return ObjectMap._function_map[object]

        raise NotSupportedObjectError(f"object = {object}")

    @staticmethod
    def get_all_objects():
        return ObjectMap._function_map.keys()
