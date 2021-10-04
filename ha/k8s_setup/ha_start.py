#!/usr/bin/env python3

import argparse
import subprocess

my_parser = argparse.ArgumentParser(prog="ha_start",
                                    description='Entrypoint for HA containerization',
                                    epilog='Fault tolerance is containerized! :)'
                                    )

my_parser.add_argument('-s', help='service_name', required=True, action='store')
my_parser.add_argument('-c', help='config file', required=False, action='store')
args = my_parser.parse_args()

driver_process= subprocess.Popen(['python3', '/opt/seagate/cortx/ha/fault_tolerance/fault_tolerance_driver.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
driver_process.communicate()

