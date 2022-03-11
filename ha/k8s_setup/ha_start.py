#!/usr/bin/env python3

import argparse
import signal
from subprocess import Popen, PIPE, STDOUT # nosec
import sys

AUTO_RESTART = 1

driver_process = None

my_parser = argparse.ArgumentParser(prog="ha_start",
                                    description='Entrypoint for HA containerization',
                                    epilog='Fault tolerance is containerized! :)'
                                    )

my_parser.add_argument('--services', '-s', help='service_name', required=True, action='store')
my_parser.add_argument('--config', '-c', help='config file', required=False, action='store')
my_parser.add_argument('--debug', '-d', help='debug mode {0|1}', type=int, nargs='?', const=1, default=0, required=False, action='store')
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
            f"--config   Config URL\n"
            f"--debug debug levels\n\t0 : no debug\n\t1 : auto restart child service")

def handle_signal(signum, frame):
    """
    Signal handler call beck function, to forward the received signal to driver process
    """
    sys.stdout.write(f"Signal {signum} at frame {frame} received.")
    sys.stdout.write(f"Sending {signum} to driver process pid: {driver_process.pid}.")
    driver_process.send_signal(signum)

def start_driver_process():
    global driver_process
    driver_process = Popen(['/usr/bin/python3', service_entry_mapping[args.services]], shell=False, stdout=PIPE, stderr=STDOUT) # nosec
    sys.stdout.write(f"The driver process with pid {driver_process.pid}, and args {driver_process.args} started successfully.")

try:
    sys.stdout.write("Starting driver process with arguments: "+str(args))
    if args.debug not in [0,1]:
        sys.stderr.write('Please provide a valid debug value.')
        usage('ha_start')
        sys.exit(22)
    if args.services not in service_entry_mapping:
        sys.stdout.write('Please provide a valid service name')
        usage('ha_start')
        sys.exit(22)
    # setting Signal handlers for all standered signals
    signal.signal(signal.SIGABRT, handle_signal)
    signal.signal(signal.SIGFPE, handle_signal)
    signal.signal(signal.SIGILL, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGSEGV, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    start_driver_process()

    # Poll process.stdout to show stdout live
    while True:
        output = driver_process.stdout.readline()
        if driver_process.poll() is not None:
            if((args.debug&AUTO_RESTART)!=0):
                if output:
                    print(output.strip().decode("utf-8"))
                sys.stdout.write(f'Warning: Driver \'{args.services}\' exited with return code: {driver_process.poll()}, restarting again.')
                start_driver_process()
            else:
                break
        if output:
            print(output.strip().decode("utf-8"))
    exit(driver_process.poll())
except Exception as proc_err:
    sys.stderr.write(f'Driver execution stopped because of some reason: {proc_err}')
