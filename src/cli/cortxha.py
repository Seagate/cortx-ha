#!/usr/bin/env python3

"""
 ****************************************************************************
 Filename:          cortxha.py
 Description:       Entry point for cortxha CLI

 Creation Date:     07/09/2020
 Author:            Ajay Paratmandali

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2001 - $Date: 2015/01/14 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
 ****************************************************************************
"""

import os
import sys
import traceback
import argparse
import pathlib
import json

from datetime import datetime
from eos.utils.schema.conf import Conf
from eos.utils.log import Log
from eos.utils.schema.payload import *

#TODO - Move the cli to cortxcli frameowrk once cortxcli is created as a separate module.
class HACli:

    def __init__(self):
        """
        Initialize HACLI
        """
        self._provider = {
            "cleanup": ""
        }
        Conf.init()
        Conf.load(const.RESOURCE_GLOBAL_INDEX, Json(const.RESOURCE_SCHEMA))
        log_level = Conf.get(const.RESOURCE_GLOBAL_INDEX, "log", "INFO")
        Log.init(service_name='cortxha', log_path=const.RA_LOG_DIR, level=log_level)

    def _usage(self):
        return """

    Example:
    cortxha cleanup db --node <node_minion_id>
    """

    def command(self):
        try:
            argParser = argparse.ArgumentParser(
                usage = "%(prog)s\n\n" +  self._usage(),
                formatter_class = argparse.RawDescriptionHelpFormatter)

            component_parser = argParser.add_subparsers(
                help = "Select one of given component.")

            cleanup_parser = component_parser.add_parser("cleanup",
                                help = "Cleanup db and resource")
            cleanup_parser.add_argument("cleanup",
                help = "Select singlenode or multinode.",
                choices = ["db"])

            cleanup_parser.add_argument("-n", "--node",
                help="Cleanup data for node")

            args = argParser.parse_args()
            Cleanup(args).cleanup_db()
        except Exception as e:
            Log.error(f"{traceback.format_exc()}")
            sys.exit(1)

if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__).resolve()), '..', '..'))
    from ha import const
    from ha.core.cleanup import Cleanup
    ha_cli = HACli()
    ha_cli.command()
