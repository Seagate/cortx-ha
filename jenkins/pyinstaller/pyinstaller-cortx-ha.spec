# -*- mode: python ; coding: utf-8 -*-
#!/usr/bin/env python3
import sys
import os
import re
import yaml

block_cipher = None

ha_path="<HA_PATH>"

# Analysis
hw_comp_ra = Analysis([ha_path + '/resource/hw_comp_ra.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

MERGE( (hw_comp_ra, 'hw_comp_ra', 'hw_comp_ra'))

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

coll = COLLECT(
               # hw_comp_ra
               hw_comp_ra_exe,
               hw_comp_ra.binaries,
               hw_comp_ra.zipfiles,
               hw_comp_ra.datas,

               strip=False,
               upx=True,
               upx_exclude=[],
               name='lib')
