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

import sys
import json

class Output:
    """Class representing a generic framework for output handling. """

    JSON = "json"
    TEXT = "text"
    TABULAR = "tabular"

    def __init__(self):
        self.output_format = Output.TEXT
        self.rc = 0

    def set_output(self, output):
        self.output = output

    def set_rc(self, rc):
        self.rc = rc

    def set_format(self, output_format):
        self.output_format = output_format

    # print the output in json format
    def print_json(self):
        # sys.stdout.write as it also help to print as buffer
        # sys.stdout.write restrict user to only print string not object.
        parse = json.loads(self.output)
        sys.stdout.write(json.dumps(parse, indent=4, sort_keys=False))

    def print_text(self):
        sys.stdout.write(self.output)

    # TBD print in  tabular format
    def print_string(self):
        parse = json.loads(self.output)
        sys.stdout.write(json.dumps(parse, indent=4, sort_keys=False))

    def dump_output(self):
        if self.output_format == Output.JSON:
            self.print_json()
        elif self.output_format == Output.TABULAR:
            self.print_string()
        else:
            self.print_text()
        sys.exit(self.rc)