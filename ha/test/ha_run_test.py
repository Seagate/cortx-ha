#!/usr/bin/env python3

"""
 ****************************************************************************
 Filename:          ha_run_test.py
 Description:       ha_run_test

 Creation Date:     04/15/2020
 Author:            Ajay Paratmandali

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2020 - $Date: 04/15/2020 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 ****************************************************************************
"""

import os
import sys
import pytest
import time
import re
import yaml
import argparse
import pathlib
import traceback

from eos.utils.log import Log
from eos.utils.schema.conf import Conf
from eos.utils.schema.payload import Json

def test_main(arg_param, argv):

    # Perform validation and Initialization
    try:
        Conf.init()
        Conf.load(const.RESOURCE_GLOBAL_INDEX, Json(const.RESOURCE_SCHEMA))
        Conf.load(const.RULE_GLOBAL_INDEX, Json(const.RULE_ENGINE_SCHAMA))
        log_level = Conf.get(const.RESOURCE_GLOBAL_INDEX, "log", "INFO")
        Log.init(service_name='ha_test', log_path=const.RA_LOG_DIR, level=log_level)
        args = yaml.safe_load(open(arg_param.file, 'r').read()) if arg_param.file is not None else {}
        if args is None: args = {}
    except Exception as e:
        raise HATestFailedError('Test Pre-condition failed. %s' %e)

    # Prepare to run the test, all or subset per command line args
    ts_list = []
    if arg_param.test_plan is not None:
        if not os.path.exists(arg_param.test_plan):
            raise HATestFailedError('Missing file %s' %arg_param.test_plan)
        with open(arg_param.test_plan) as file:
            content = file.readlines()
            for x in content:
                if not x.startswith('#'):
                    ts_list.append(x.strip())
    else:
        file_path = os.path.dirname(os.path.realpath(__file__))
        for root, _, filenames in os.walk(os.getcwd()):
            for filename in filenames:
                if re.match(r'test_.*\.py$', filename):
                    file = os.path.join(root, filename).rsplit('.', 1)[0]\
                        .replace(file_path + "/", "").replace("/", ".")
                    ts_list.append(file)

    ts_count = test_count = pass_count = fail_count = 0
    ts_start_time = time.time()
    for ts in ts_list:
        print('\n####### Test Suite: %s ######' %ts)
        ts_count += 1
        try:
            ts_module = __import__('ha.test.integration.%s' %ts, fromlist=[ts])
            # Initialization
            init = getattr(ts_module, 'init')
            init(args)
        except Exception as e:
            traceback.print_exc()
            print('FAILED: Error: %s #@#@#@' %e)
            fail_count += 1
            Log.exception(e)
            continue

        # Actual test execution
        for test in ts_module.test_list:
            test_count += 1
            try:
                start_time = time.time()
                test(args)
                duration = time.time() - start_time
                print('%s:%s: PASSED (Time: %ds)' %(ts, test.__name__, duration))
                pass_count += 1
            except (HATestFailedError, Exception) as e:
                Log.exception(e)
                print('%s:%s: FAILED #@#@#@' %(ts, test.__name__))
                print('    %s\n' %e)
                fail_count += 1

    duration = time.time() - ts_start_time
    print('\n***************************************')
    print('TestSuite:%d Tests:%d Passed:%d Failed:%d TimeTaken:%ds' \
        %(ts_count, test_count, pass_count, fail_count, duration))
    print('***************************************')
    if arg_param.output is not None:
        with open(arg_param.output, "w") as f:
            status = "Failed" if fail_count != 0 else "Passed"
            f.write(status)

if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..'))
    """
    ha_run_test integration --test_plan ha/test/plans/self_test.pln
    ha_run_test unit --path
    """
    from ha import const
    from ha.utility.error import HATestFailedError
    try:
        argParser = argparse.ArgumentParser(
            usage = "%(prog)s",
            formatter_class = argparse.RawDescriptionHelpFormatter)
        test_parser = argParser.add_subparsers(
                help = "Select one of given component.")

        # Unit
        unit_parser = test_parser.add_parser("unit",
                            help = "Unit test.")
        unit_parser.add_argument("-p", "--path",
                help="Enter path of testlist file")

        # Integration
        integration_parser = test_parser.add_parser("integration",
                        help = "Integration test.")
        integration_parser.add_argument("-t", "--test_plan",
                help="Enter path of testlist file")
        integration_parser.add_argument("-f", "--file",
                help="Enter path of args.yaml")
        integration_parser.add_argument("-o", "--output",
                help="Print final result in file return fail if any one of test failed.")
        args = argParser.parse_args()

        if len(sys.argv) <= 1:
            argParser.print_help(sys.stderr)
        elif sys.argv[1] == "unit":
            path = args.path if args.path is not None else \
                os.path.join(os.path.dirname(pathlib.Path(__file__)), 'unit')
            pytest.main(['-v', path])
        elif sys.argv[1] == "integration":
            test_main(args, sys.argv[0])
        else:
            argParser.print_help(sys.stderr)
    except Exception as e:
        Log.error(traceback.format_exc())
        print(e)