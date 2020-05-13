# -*- mode: python ; coding: utf-8 -*-
#!/usr/bin/env python3
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

MERGE( (hw_comp_ra, 'hw_comp_ra', 'hw_comp_ra'),
        (iem_comp_ra, 'iem_comp_ra', 'iem_comp_ra'))

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

# hw_comp_ra
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

               strip=False,
               upx=True,
               upx_exclude=[],
               name='lib')
