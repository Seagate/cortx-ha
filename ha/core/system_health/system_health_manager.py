#!/usr/bin/env python3

# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

class SystemHealthManager:
    """
    System Health Manager. This class provides low level get/put methods
    for storing/reading health keys to/from the store.
    """

    def __init__(self, store):
        """
        Init method.
        """
        self._store = store

    def get_key(self, key):
        """
        Get key method.
        """
        return self.store.get(key)

    def set_key(self, key, value):
    """
        Set key method.
        """
    self.store.put(value, key)
