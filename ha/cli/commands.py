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

#from ha.core.error import HAUnimplemented
#from  ha.cli import cluster

class Command:
    def __init__(self, args):
        self._op_type = args.op_type
        self._args = args.args

    @property
    def args(self):
        return self._args

    @property
    def op_type(self):
        return self._op_type

    #@staticmethod
    def add_args(parser, cmd_class, cmd_name):
        """Add Command args for parsing."""

        parser1 = parser.add_parser(
            cmd_class.name, help='%s operations' % cmd_name)
        # If required help can be specified individually each child class
        # by overriding add_args method
        parser1.add_argument('op_type', help='operation type')
        parser1.add_argument('args', nargs='*', default=[], help='args')

        parser1.set_defaults(command=cmd_class)

    @staticmethod
    def validate():
        print("Placeholder validate method")

    @staticmethod
    def execute():
        print("Placeholder execute method")


class clusterCommand(Command):
    """Cluster related commands."""

    name = "cluster"

    def __init__(self, args):
        super(clusterCommand, self).__init__(args)

        from cluster import Cluster

        self._cluster = Cluster()

    def execute(self):
        """Execute cluster commands """

        print("Placeholder cluster command")
        self._cluster.process(self.op_type, self.args)



class nodeCommand(Command):
    """Node related commands."""

    name = "node"

    def __init__(self, args):
        super(nodeCommand, self).__init__(args)

        #from node import Node
        #self._node = Node()

    def execute(self):

        """Eexecute node commands """
        print("Placeholder nodeCommand")
        #self._node.execute(self.op_type, self.args)


class serviceCommand(Command):
    """service related commands."""

    name = "service"

    def __init__(self, args):
        super(serviceCommand, self).__init__(args)

        #from service import Service
        #self._service = Service()

    def execute(self):
        
        """Execute service commands """
        print("Placeholder serviceCommand")
        #self._service.execute(self.op_type, self.args)
 

"""
SupportBundleCommand is currently broken, so removed the code.
This will be added when the support bundle user story is started 
"""
