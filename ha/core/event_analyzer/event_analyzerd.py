#!/usr/bin/python3.6
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
 ****************************************************************************
  Description:       Entry point for the event analyzer daemon service
 ****************************************************************************
"""

import time
import sys

from cortx.utils.log import Log
from ha.core.config.config_manager import ConfigManager

class Service:

    def init(self):
        ConfigManager.init("event_analyzer_d")
        Log.info("Event analyzer daemon initializations")

    def run(self):
        Log.info("Running the daemon for HA event analyzer...")
        while 1:
            #TODO remove this message and sleep once appropriate code is added here
            Log.info("Running the daemon for HA event analyzer")
            time.sleep(600)


def main(argv):
    """
    Entry point for event analyzer daemon
    """
    # argv can be used later when config parameters are needed
    event_analyser_service = Service()
    event_analyser_service.init()
    event_analyser_service.run()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
