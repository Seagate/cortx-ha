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

from cortx.utils.conf_store import Conf
from ha import const
from ha.util.message_bus import MessageBus
from ha.core.config.config_manager import ConfigManager

class TestSigtermHandling(unittest.TestCase):
    """
    Unit test for sigterm handling
    """

    def start_all_services(self):
        """
        Start all services to test sigterm
        """
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

    def send_start_cluster_shutdown_message(self):
        """
        Sends the "start_cluster_shutdown" message for cluster stop monitor
        """
        producer_id="csm_producer"
        self.message_type = Conf.get(const.HA_GLOBAL_INDEX, f'CLUSTER_STOP_MON{const._DELIM}message_type')
        self.producer = MessageBus.get_producer(producer_id=producer_id, message_type=self.message_type)
        self.producer.publish({"start_cluster_shutdown":"1"})
        # The consumer 'ClusterStopMonitor' will checking this message/key as cluster_alert["start_cluster_shutdown"] == '1'

    def check_cluster_stop_key(self, should_exists):
        """
        This checks if const.CLUSTER_STOP_KEY is exist or not in confsore and assert on failure
        should_exists : if it is true and key doen not exist then assert (it raise failure exception) and vice versa.
        This key should be added by cluster stop monitor (falult tolerance monitor service) and
        should be get deleted by k8s monitor after receiving sigterm.
        """
        key_exists = self.confstore.key_exists(const.CLUSTER_STOP_KEY)
        self.assertTrue(key_exists == should_exists, f"Error: The Key {const.CLUSTER_STOP_KEY} must should be deleted by k8s monitor only after sigterm is received.")

    def cleanup_cluster_stop(self):
        """
        Cleanup the key const.CLUSTER_STOP_KEY from confstore.
        """
        if self.confstore.key_exists(const.CLUSTER_STOP_KEY):
            print(f"The Key {const.CLUSTER_STOP_KEY} is exist in confstore so deleting now.")
            self.confstore.delete(const.CLUSTER_STOP_KEY)

    def send_sigterm(self):
        """
        Send sigterm (15) signal to all services
        """
        print("Sending SIGTERM to all services.")
        for service in self.services:
            service.send_signal(15)

    def check_running_services(self):
        """
        Check if all services are running if not then assert
        """
        services = [service for service in self.services]

        # filter out the running services
        print("Check running services.")
        services[:] = filterfalse(lambda service : service.poll() != None, services)
        print(f"Running service: {[service.args for service in services]}")
        self.assertTrue(len(services) == len(self.services), "Not all HA services are running.")

    def check_for_stop(self, wait_time=20):
        """
        keep polling for provided wait_time with 1 seconds sleep in between
        asster for below checks and close all popen resources after test
        1. Assert if all services are not running before sigterm
        2. Assert if not all services stop in provided wait_time
        """
        print(f"Pulling services for {wait_time} seconds, to check whether all are stopping.")
        print("Total started services:")
        services = [service for service in self.services]
        print([service.args for service in services])

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
            print(f"Not all services are successfully stopped withing timeout {wait_time} after start pulling.")
            for service in services:
                print(f"Service: pid: {service.pid} args: {service.args} is not stopped in provided time.")
            self.assertTrue(len(services) == 0, f"Not all HA services are not stopped within provided timeout:{wait_time} seconds.")

    def cleanup_stop_and_release_all_resources(self):
        """
        Cleanup: try closing all remaining services
        and Release/close aquired resouces by Popen object
        """
        # Release/close aquired resouces by Popen object (stdout/stderr)
        for service in self.services:
            try:
                try:
                    print(f"Cleaning resources for service: pid: {service.pid} args: {service.args}.")
                    service.kill()
                except Exception as ex:
                    print(f"Exception while closing service {service.args}: {ex}")
                service.stderr.close()
                service.stdout.close()
            except Exception as ex:
                print(f"Exception while closing service {service.args} resources (stderr, stdout): {ex}")

    def setUp(self):
        """
        Setup the prerequisit of tests
        """
        print("Setup")
        ConfigManager.init("test_Cluster_stop_sigterm")
        self.confstore = ConfigManager.get_confstore()
        MessageBus.init()

    def tearDown(self):
        """
        cleanup after all tests
        """
        print("tearDown")
        MessageBus.deregister(self.message_type)

    def ignore_test_sigterm(self):
        """
        Test call to test sigterm functionality to know more about check
        refer to function check_for_stop()
        """
        try:
            self.start_all_services()
            print("After starting services waiting for 10 seconds to let run all services.")
            time.sleep(10)

            # Check if all services are running
            self.check_running_services()

            self.send_sigterm()
            self.check_for_stop()
        finally:
            self.cleanup_stop_and_release_all_resources()

    def test_cluster_stop_and_sigterm(self):
        """
        Test call to test sigterm functionality to know more about check
        refer to function check_for_stop()
        """
        try:
            # Start all HA services
            self.start_all_services()
            print("After starting services waiting for 10 seconds to let run all services.")
            time.sleep(10)

            # Check if all services are running
            self.check_running_services()

            # send start_cluster_shutdown message which will recived by
            self.send_start_cluster_shutdown_message()
            print("After sending (start_cluster_shutdown) message waiting for 15 seconds to process it by cluster stop monitor.")
            time.sleep(15)

            # check if cluster stop monitor has added the key to confstore
            self.check_cluster_stop_key(True)

            # now send sigterm message to all services
            self.send_sigterm()
            print("After sending SIGTERM waiting for 5 seconds to make sure whether the signal is received.")
            time.sleep(5)

            # check if k8s monitor has deleted the key from confstore
            self.check_cluster_stop_key(False)

            # Check if due to sigterm is all services are exiting
            self.check_for_stop()
        finally:
            self.cleanup_stop_and_release_all_resources()
            self.cleanup_cluster_stop()


if __name__ == "__main__":
    unittest.main()
