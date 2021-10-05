#!/usr/bin/env python3

import argparse
from subprocess import Popen, PIPE # nosec
import sys


my_parser = argparse.ArgumentParser(prog="ha_start",
                                    description='Entrypoint for HA containerization',
                                    epilog='Fault tolerance is containerized! :)'
                                    )

my_parser.add_argument('-s', help='service_name', required=True, action='store')
my_parser.add_argument('-c', help='config file', required=False, action='store')
args = my_parser.parse_args()

try:
    driver_process= Popen(['/usr/bin/python3', '/usr/lib/python3.6/site-packages/ha/fault_tolerance/fault_tolerance_driver.py'], shell=False, stdout=PIPE, stderr=PIPE) # nosec
except Exception as proc_err:
    sys.stderr.write(f'Driver execution stopped because of some reason: {proc_err}')

