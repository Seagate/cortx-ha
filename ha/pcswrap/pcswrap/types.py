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

from abc import ABC, abstractmethod
from typing import List, NamedTuple, Optional

Credentials = NamedTuple('Credentials', [('username', str), ('password', str)])

Node = NamedTuple('Node', [('name', str), ('online', bool), ('standby', bool),
                           ('unclean', bool), ('resources_running', int)])

Resource = NamedTuple('Resource', [('id', str), ('resource_agent', str),
                                   ('role', str), ('target_role', str),
                                   ('active', bool), ('orphaned', bool),
                                   ('blocked', bool), ('managed', bool),
                                   ('failed', bool), ('failure_ignored', bool),
                                   ('nodes_running_on', int)])

StonithResource = NamedTuple('StonithResource',
                             [('klass', str), ('typename', str),
                              ('pcmk_host_list', str), ('ipaddr', str),
                              ('login', str), ('passwd', str)])


class PcsConnector(ABC):
    credentials = None

    @abstractmethod
    def get_nodes(self) -> List[Node]:
        pass

    @abstractmethod
    def standby_node(self, node_name: str) -> None:
        pass

    @abstractmethod
    def unstandby_node(self, node_name: str) -> None:
        pass

    @abstractmethod
    def get_cluster_name(self) -> str:
        pass

    @abstractmethod
    def standby_all(self) -> None:
        pass

    @abstractmethod
    def unstandby_all(self) -> None:
        pass

    @abstractmethod
    def shutdown_node(self, node_name: str) -> None:
        pass

    @abstractmethod
    def get_resources(self) -> List[Resource]:
        pass

    @abstractmethod
    def get_stonith_resources(self) -> List[Resource]:
        pass

    @abstractmethod
    def disable_resource(self, resource: Resource) -> None:
        pass

    @abstractmethod
    def enable_resource(self, resource: Resource) -> None:
        pass

    @abstractmethod
    def ensure_authorized(self) -> None:
        pass

    def set_credentials(self, credentials: Credentials):
        self.credentials = credentials

    def get_credentials(self) -> Optional[Credentials]:
        return self.credentials

    @abstractmethod
    def manual_shutdown_node(self, node_name: str) -> None:
        '''
        Powers off the given node by name using explicit ipmitool invocation.
        The necessary IPMI parameters are extracted from the corresponding
        stonith resource which is registered in Pacemaker
        '''
        pass

    @abstractmethod
    def ensure_shutdown_possible(self, node_name: str) -> None:
        pass

    @abstractmethod
    def get_eligible_resource_count(self) -> int:
        '''
        Looks into "summary" information provided by Pacemaker and extracts the
        number of resources that are expected to run with respect to disabled
        and blocked resources.
        '''
        pass

    @abstractmethod
    def get_stopped_resource_count(self) -> int:
        '''
        Looks into "summary" information provided by Pacemaker and extracts the
        number of resources that are stopped for sure in the cluster (i.e. it
        is equal to blocked + disabled).
        '''
        pass
