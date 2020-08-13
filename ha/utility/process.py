#!/usr/bin/env python3

"""
**************************************************************************
 **filename:          process.py
 Description:       Cluster Management

 Creation Date:     07/09/2020
 Author:            Ajay Paratmandali

 Do NOT modify or remove this copyright and confidentiality notice!
 Copyright (c) 2020 - $Date: 07/09/2020 $ Seagate Technology, LLC.
 The code contained herein is CONFIDENTIAL to Seagate Technology, LLC.
 Portions are also trade secret. Any use, duplication, derivation, distribution
 or disclosure of this code, for any reason, not expressly authorized is
 prohibited. All other rights are expressly reserved by Seagate Technology, LLC.
****************************************************************************
"""

from eos.utils.log import Log
from eos.utils.process import SimpleProcess

from ha.utility.error import HACommandTerminated

class Process:
    @staticmethod
    def _run_cmd(cmd):
        """
        Run command and throw error if cmd failed
        """
        try:
            _err = ""
            _proc = SimpleProcess(cmd)
            _output, _err, _rc = _proc.run(universal_newlines=True)
            Log.debug(f"cmd: {cmd}, output: {_output}, err: {_err}, rc: {_rc}")
            if _rc != 0:
                Log.error(f"cmd: {cmd}, output: {_output}, err: {_err}, rc: {_rc}")
                raise HACommandTerminated(f"Failed to execute {cmd}")
            return _output, _err, _rc
        except Exception as e:
            raise HACommandTerminated("Failed to execute %s Error: %s %s" %(cmd,e,_err))