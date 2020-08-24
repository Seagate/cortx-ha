# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>. For any questions
# about this software or licensing, please email opensource@seagate.com or
# cortx-questions@seagate.com.

# flake8: noqa: E401
import sys
sys.path.insert(0, '..')
from unittest.mock import MagicMock, call
from pcswrap.types import StonithResource
from pcswrap.internal.connector import StonithParser
from typing import Tuple
import unittest


class StonithParserTest(unittest.TestCase):
    def test_parser_works(self):
        p = StonithParser()
        raw_text = '''
 Resource: stonith-c1 (class=stonith type=fence_ipmilan)
  Attributes: delay=5 ipaddr=10.230.244.112 login=ADMIN passwd=adminBMC! pcmk_host_check=static-list pcmk_host_list=srvnode-1 power_timeout=40
  Operations: monitor interval=10s (stonith-c1-monitor-interval-10s)
'''        
        result = p.parse(raw_text)
        self.assertIsNotNone(result)
        self.assertEqual('stonith', result.klass)
        self.assertEqual('fence_ipmilan', result.typename)
        self.assertEqual('10.230.244.112', result.ipaddr)
        self.assertEqual('ADMIN', result.login)
        self.assertEqual('adminBMC!', result.passwd)

    def test_only_ipmi_supported(self):
        p = StonithParser()
        raw_text = '''
 Resource: stonith-c1 (class=stonith type=fence_dummy)
  Attributes: delay=5 ipaddr=10.230.244.112 login=ADMIN passwd=adminBMC! pcmk_host_check=static-list pcmk_host_list=srvnode-1 power_timeout=40
  Operations: monitor interval=10s (stonith-c1-monitor-interval-10s)
'''        
        with self.assertRaises(AssertionError):
            p.parse(raw_text)

    def test_emptyilnes_ignored(self):
        p = StonithParser()
        raw_text = '''

 Resource: stonith-c1 (class=stonith type=fence_ipmilan)

  Attributes: delay=5 ipaddr=10.230.244.112 login=ADMIN passwd=adminBMC! pcmk_host_check=static-list pcmk_host_list=test-2 power_timeout=40
  Operations: monitor interval=10s (stonith-c1-monitor-interval-10s)
'''        
        result = p.parse(raw_text)
        self.assertIsNotNone(result)
        self.assertEqual('stonith', result.klass)
        self.assertEqual('fence_ipmilan', result.typename)
        self.assertEqual('10.230.244.112', result.ipaddr)
        self.assertEqual('ADMIN', result.login)
        self.assertEqual('adminBMC!', result.passwd)
        self.assertEqual('test-2', result.pcmk_host_list)
