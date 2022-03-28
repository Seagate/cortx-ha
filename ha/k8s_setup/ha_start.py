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
my_parser.add_argument('--config', '-c', help='config file url', required=False, action='store')
my_parser.add_argument('--debug', '-d', help='debug level {0|1}', type=int, nargs='?', const=1, default=0, required=False, action='store')
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
        print(
            f"usage: {prog} [-h] <-s/--services service to start> <-c/--config url> [-d/--debug [0|1]]...\n"
            f"where:\n"
            f"-s --services health_monitor, fault_tolerance, k8s_monitor\n"
            f"[-c --config   Config file URL : yaml://<file_path>] E.g. yaml:///etc/cortx/cluster.conf\n"
            f"[-d --debug   [level]] (if level is not provided, then it considered as 1)"
            f"\n\t\t0 : No debug.\n\t\t1 : Auto restarts child process if it dia.", file=sys.stderr, flush=True)

def handle_signal(signum, frame):
    """
    Signal handler call beck function, to forward the received signal to driver process
    """
    print(f"Signal {signum} at frame {frame} received.", flush=True)
    print(f"Sending {signum} to driver process pid: {driver_process.pid}.", flush=True)
    driver_process.send_signal(signum)

def start_driver_process():
    global driver_process
    driver_process = Popen(['/usr/bin/python3', service_entry_mapping[args.services]], shell=False, stdout=PIPE, stderr=STDOUT) # nosec
    print(f"The driver process with pid {driver_process.pid}, and args {driver_process.args} started successfully.", flush=True)

def is_debug_build():
    # TODO: find out if it is debug build
    return False

def handle_debug_option():
    if((args.debug&AUTO_RESTART)!=0):
        print(f'Warning: Driver \'{args.services}\' exited with return code: {driver_process.poll()}, restarting again.', flush=True)
        start_driver_process()

def main(argv: list):
    try:
        print(str(args))
        if args.debug not in [0,1]:
            sys.stderr.write('Please provide a valid debug value.')
            usage('ha_start')
            sys.exit(22)
        if args.services not in service_entry_mapping:
            print('Please provide a valid service name', flush=True)
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
            if output:
                print(output.strip().decode("utf-8"), flush=True)

            if driver_process.poll() is not None:
                if is_debug_build():
                    handle_debug_option()
                else:
                    break

        exit(driver_process.poll())
    except Exception as proc_err:
        print(f'Driver execution stopped because of some reason: {proc_err}', file=sys.stderr, flush=True)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
