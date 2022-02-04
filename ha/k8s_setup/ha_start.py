#!/usr/bin/env python3

import argparse
import signal
from subprocess import Popen, PIPE # nosec
import sys

driver_process = None

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

def handle_signal(signum, frame):
    """
    Signal handler call beck function, to forward the received signal to driver process
    """
    sys.stdout.write(f"Signal {signum} at frame {frame} received.")
    # If received SIGUSR1 then restart service
    if signal.SIGUSR1.value == signum:
        print("\nCaught signal.SIGUSR1, Restarting process")
        driver_process.kill()
        set_signals()
        start_process()
        driver_process.wait()
    else:
        sys.stdout.write(f"Sending {signum} to driver process pid: {driver_process.pid}.")
        driver_process.kill()
        raise Exception(f"Received {signum} signals, terminating process.\n")

def start_process():
    """
    Start Process
    """
    global driver_process
    driver_process = Popen(
        ['/usr/bin/python3', service_entry_mapping[args.services]],
        shell=False, stdout=PIPE, stderr=PIPE) # nosec
    sys.stdout.write(f"The driver process with pid {driver_process.pid}, and args {driver_process.args} started successfully.\n")
    driver_process.wait()

def set_signals():
    # setting Signal handlers for all standard signals
    signal.signal(signal.SIGABRT, handle_signal)
    signal.signal(signal.SIGFPE, handle_signal)
    signal.signal(signal.SIGILL, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGSEGV, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGUSR1, handle_signal)

if __name__ == "__main__":
    try:
        if args.services not in service_entry_mapping:
            sys.stdout.write('Please provide a valid service name')
            usage('ha_start')
            sys.exit(22)

        set_signals()
        start_process()
        import time
        while True:
            time.sleep(1000)
    except Exception as proc_err:
        sys.stderr.write(f'Driver execution stopped because of some reason: {proc_err}\n')
