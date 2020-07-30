#!/usr/bin/env python3

"""
 ****************************************************************************
 Filename:          hw_comp_ra.py
 Description:       hw_comp_ra resource agent

 Creation Date:     04/15/2020
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
import pathlib

if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(pathlib.Path(__file__)), '..', '..'))
    from ha.resource import resource_agent
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit(resource_agent.main(resource_agent.HardwareResourceAgent, action))