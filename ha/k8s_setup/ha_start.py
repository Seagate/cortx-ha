#!/usr/bin/env python3

import argparse
from subprocess import Popen, PIPE # nosec
import sys


my_parser = argparse.ArgumentParser(prog="ha_start",
                                    description='Entrypoint for HA containerization',
                                    epilog='Fault tolerance is containerized! :)'
                                    )

my_parser.add_argument('--services', '-s', help='service_name', required=True, action='store')
my_parser.add_argument('--config', '-c', help='config file', required=False, action='store')
args = my_parser.parse_args()

service_entry_mapping = {
                        'health_monitor': '/usr/lib/python3.6/site-packages/ha/core/health_monitor/health_monitord.py',
                        'fault_tolerance': '/usr/lib/python3.6/site-packages/ha/fault_tolerance/fault_tolerance_driver.py',
                        'k8s_monitor': '/usr/lib/python3.6/site-packages/ha/monitor/k8s/monitor.py'
                        }

def usage(prog: str):
        """
        Print usage instructions
        """
        sys.stderr.write(
            f"usage: {prog} [-h] <--config url> <--services service to start>...\n"
            f"where:\n"
            f"--services health_monitor, fault_tolerance, k8s_monitor\n"
            f"--config   Config URL\n")

try:
    if args.services not in service_entry_mapping:
        print('Please provide a valid service name')
        usage('ha_start')
        sys.exit(22)
    driver_process = Popen(['/usr/bin/python3', service_entry_mapping[args.services]], shell=False, stdout=PIPE, stderr=PIPE) # nosec
except Exception as proc_err:
    sys.stderr.write(f'Driver execution stopped because of some reason: {proc_err}')
