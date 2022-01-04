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


import os
import sys
import time
import pathlib
sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..', '..', '..'))
from itertools import filterfalse
from subprocess import Popen, PIPE # nosec
import unittest

class TestSigtermHandling(unittest.TestCase):
    """
    Unit test for sigterm handling
    """

    def start_all_services(self):
        print("Starting all services.")
        self.k8s_monitor     = Popen(['/usr/bin/python3', '/usr/lib/python3.6/site-packages/ha/monitor/k8s/monitor.py'],
                                     shell=False,
                                     stdout=PIPE,
                                     stderr=PIPE)
        print(f"Started: k8s monitor, pid: {self.k8s_monitor.pid}")
        self.fault_tolerance = Popen(['/usr/bin/python3', '/usr/lib/python3.6/site-packages/ha/fault_tolerance/fault_tolerance_driver.py'],
                                    shell=False,
                                    stdout=PIPE,
                                    stderr=PIPE)
        print(f"Started: fault monitor, pid: {self.fault_tolerance.pid}")
        self.health_monitor  = Popen(['/usr/bin/python3', '/usr/lib/python3.6/site-packages/ha/core/health_monitor/health_monitord.py'],
                                    shell=False,
                                    stdout=PIPE,
                                    stderr=PIPE)
        print(f"Started: health monitor, pid: {self.health_monitor.pid}")
        self.services = [self.k8s_monitor, self.fault_tolerance, self.health_monitor]


    def send_sigterm(self):
        print("sending sigterm to all services.")
        for service in self.services:
            service.send_signal(15)

    def check_for_stop(self, wait_time=20):
        print(f"polling services for {wait_time} seconds, to check whether all are stopping.")
        print("Total started services:")
        services = [service for service in self.services]
        print([service.args for service in services])

        # check how many services are running
        services[:] = filterfalse(lambda service : service.poll() != None, services)
        print(f"Running service: {[service.args for service in services]}")
        self.assertTrue(len(services) == len(self.services), "Not all HA services are running.")
        timeout = wait_time
        # loop till timeout and check for services are running
        while timeout:
            timeout-=1
            time.sleep(1)
            if len(services):
                services[:] = filterfalse(lambda service : service.poll() != None, services)
                print(f"services left: {[service.args for service in services]}")
            else:
                print(f"All services are successfully stopped {wait_time - timeout} seconds after receiving sigterm.")
                break # all services are successfully stopped
        # After timeout check how many services are running, and if yes, then raise an exception.
        if len(services):
            print(f"Not all services are successfully stopped withing timeout {wait_time} after receiving sigterm.")
            for service in services:
                print(f"service: pid: {service.pid} args: {service.args} is not stopped in provided time {wait_time}.")
                print(f"Service with pid: {service.pid} is Killing now.")
                service.kill()
            self.assertTrue(len(services) == 0, f"Not all HA services are not stopped within provided timeout:{wait_time} seconds.")

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sigterm(self):
        self.start_all_services()
        print("Waiting for 10 seconds to let run all services.")
        time.sleep(10)
        self.send_sigterm()
        self.check_for_stop()

if __name__ == "__main__":
    unittest.main()