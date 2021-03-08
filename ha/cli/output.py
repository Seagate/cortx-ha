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

import json
#import sys


class Output():
    """Class representing a generic framework for output handling. """

    #def __init__(self, rc, desc):
        #self.output_string = "output"

    # print the output in json format
    def print_json(self, output_data):
        # we should be okay with using print instead of sys.stdout.write
        # since print writes to stdout only.
        print(json.dumps(output_data, indent=4, sort_keys=False))

        # TBD check if exit required at this point
        #sys.exit()
            
    # TBD print in  tabular format
    def print_string(self, output_data):
        print(json.dumps(output_data, indent=4, sort_keys=False))
        
