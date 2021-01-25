# -*- mode: python ; coding: utf-8 -*-
#!/usr/bin/env python3

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


import sys
import os
import re
import yaml

block_cipher = None

ha_path="<HA_PATH>"

# Analysis
hw_comp_ra = Analysis([ha_path + '/ha/resource/hw_comp_ra.py'],
             pathex=[ha_path],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['numpy', 'matplotlib'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

iem_comp_ra = Analysis([ha_path + '/ha/resource/iem_comp_ra.py'],
             pathex=[ha_path],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['numpy', 'matplotlib'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

cortxha =  Analysis([ha_path + '/ha/cli/cortxha.py'],
             pathex=[ha_path],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['numpy', 'matplotlib'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)


MERGE( (hw_comp_ra, 'hw_comp_ra', 'hw_comp_ra'),
        (iem_comp_ra, 'iem_comp_ra', 'iem_comp_ra'),
        (cortxha, 'cortxha', 'cortxha'))

# hw_comp_ra
hw_comp_ra_pyz = PYZ(hw_comp_ra.pure, hw_comp_ra.zipped_data,
             cipher=block_cipher)

hw_comp_ra_exe = EXE(hw_comp_ra_pyz,
          hw_comp_ra.scripts,
          [],
          exclude_binaries=True,
          name='hw_comp_ra',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

# iem_comp_ra
iem_comp_ra_pyz = PYZ(iem_comp_ra.pure, iem_comp_ra.zipped_data,
             cipher=block_cipher)

iem_comp_ra_exe = EXE(iem_comp_ra_pyz,
          iem_comp_ra.scripts,
          [],
          exclude_binaries=True,
          name='iem_comp_ra',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

# cortxha
cortxha_pyz = PYZ(cortxha.pure, cortxha.zipped_data,
             cipher=block_cipher)

cortxha_exe = EXE(cortxha_pyz,
          cortxha.scripts,
          [],
          exclude_binaries=True,
          name='cortxha',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(
               # hw_comp_ra
               hw_comp_ra_exe,
               hw_comp_ra.binaries,
               hw_comp_ra.zipfiles,
               hw_comp_ra.datas,

               # iem_comp_ra
               iem_comp_ra_exe,
               iem_comp_ra.binaries,
               iem_comp_ra.zipfiles,
               iem_comp_ra.datas,

               # cortxha
               cortxha_exe,
               cortxha.binaries,
               cortxha.zipfiles,
               cortxha.datas,

               strip=False,
               upx=True,
               upx_exclude=[],
               name='lib')
