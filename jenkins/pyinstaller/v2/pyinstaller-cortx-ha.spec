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

def import_list(ha_path, walk_path):
    import_list = []
    for root, directories, filenames in os.walk(walk_path):
        for filename in filenames:
            if re.match(r'.*.\.py$', filename) and filename != '__init__.py':
                file = os.path.join(root, filename).rsplit('.', 1)[0]\
                    .replace(ha_path + "/", "").replace("/", ".")
                import_list.append(file)
    return import_list

block_cipher = None

ha_path="<HA_PATH>"
cmd_hidden_import = ["ha.cli.exec.clusterExecutor", "ha.cli.exec.nodeExecutor", "ha.cli.exec.serviceExecutor", "ha.cli.exec.storagesetExecutor", "ha.cli.exec.supportBundleExecutor"]
product_module_list = import_list(ha_path, ha_path + "/ha/core/controllers")
product_module_list.extend(cmd_hidden_import)

# Analysis
cortxha =  Analysis([ha_path + '/ha/cli/cortxha.py'],
        pathex=[ha_path],
        binaries=[],
        datas=[],
        hiddenimports=product_module_list,
        hookspath=[],
        runtime_hooks=[],
        excludes=['numpy', 'matplotlib'],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False)

dynamic_fid_service_ra =  Analysis([ha_path + '/ha/resource/dynamic_fid_service_ra.py'],
        pathex=[ha_path],
        binaries=[],
        datas=[],
        hiddenimports=product_module_list,
        hookspath=[],
        runtime_hooks=[],
        excludes=['numpy', 'matplotlib'],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False)

ha_setup =  Analysis([ha_path + '/ha/setup/ha_setup.py'],
        pathex=[ha_path],
        binaries=[],
        datas=[],
        hiddenimports=product_module_list,
        hookspath=[],
        runtime_hooks=[],
        excludes=['numpy', 'matplotlib'],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False)

pre_disruptive_upgrade =  Analysis([ha_path + '/ha/setup/pre_disruptive_upgrade.py'],
        pathex=[ha_path],
        binaries=[],
        datas=[],
        hiddenimports=product_module_list,
        hookspath=[],
        runtime_hooks=[],
        excludes=['numpy', 'matplotlib'],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False)

post_disruptive_upgrade =  Analysis([ha_path + '/ha/setup/post_disruptive_upgrade.py'],
        pathex=[ha_path],
        binaries=[],
        datas=[],
        hiddenimports=product_module_list,
        hookspath=[],
        runtime_hooks=[],
        excludes=['numpy', 'matplotlib'],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False)

remote_execution =  Analysis([ha_path + '/ha/remote_execution/ssh_communicator.py', ha_path + '/ha/remote_execution/remote_executor.py'],
        pathex=[ha_path],
        binaries=[],
        datas=[],
        hiddenimports=product_module_list,
        hookspath=[],
        runtime_hooks=[],
        excludes=['numpy', 'matplotlib'],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False)

event_analyzerd =  Analysis([ha_path + '/ha/core/event_analyzer/event_analyzerd.py'],
        pathex=[ha_path],
        binaries=[],
        datas=[],
        hiddenimports=product_module_list,
        hookspath=[],
        runtime_hooks=[],
        excludes=['numpy', 'matplotlib'],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False)

pcmk_alert =  Analysis([ha_path + '/ha/alert/pcmk_alert.py'],
        pathex=[ha_path],
        binaries=[],
        datas=[],
        hiddenimports=product_module_list,
        hookspath=[],
        runtime_hooks=[],
        excludes=['numpy', 'matplotlib'],
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=False)

MERGE((cortxha, 'cortxha', 'cortxha'),
        (dynamic_fid_service_ra, 'dynamic_fid_service_ra', 'dynamic_fid_service_ra'),
        (ha_setup, 'ha_setup', 'ha_setup'),
        (pre_disruptive_upgrade, 'pre_disruptive_upgrade', 'pre_disruptive_upgrade'),
        (event_analyzerd, 'event_analyzerd', 'event_analyzerd'),
        (pcmk_alert, 'pcmk_alert', 'pcmk_alert'),
        (post_disruptive_upgrade, 'post_disruptive_upgrade', 'post_disruptive_upgrade'),
        (remote_execution, 'remote_execution', 'remote_execution')
        )

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

# dynamic_fid_service_ra
dynamic_fid_service_ra_pyz = PYZ(dynamic_fid_service_ra.pure, dynamic_fid_service_ra.zipped_data,
        cipher=block_cipher)

dynamic_fid_service_ra_exe = EXE(dynamic_fid_service_ra_pyz,
        dynamic_fid_service_ra.scripts,
        [],
        exclude_binaries=True,
        name='dynamic_fid_service_ra',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True )

# ha_setup
ha_setup_pyz = PYZ(ha_setup.pure, ha_setup.zipped_data,
        cipher=block_cipher)

ha_setup_exe = EXE(ha_setup_pyz,
        ha_setup.scripts,
        [],
        exclude_binaries=True,
        name='ha_setup',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True )

# pre_disruptive_upgrade
pre_disruptive_upgrade_pyz = PYZ(pre_disruptive_upgrade.pure, pre_disruptive_upgrade.zipped_data,
        cipher=block_cipher)

pre_disruptive_upgrade_exe = EXE(pre_disruptive_upgrade_pyz,
        pre_disruptive_upgrade.scripts,
        [],
        exclude_binaries=True,
        name='pre_disruptive_upgrade',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True )

# post_disruptive_upgrade
post_disruptive_upgrade_pyz = PYZ(post_disruptive_upgrade.pure, post_disruptive_upgrade.zipped_data,
        cipher=block_cipher)

post_disruptive_upgrade_exe = EXE(post_disruptive_upgrade_pyz,
        post_disruptive_upgrade.scripts,
        [],
        exclude_binaries=True,
        name='post_disruptive_upgrade',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True )

# remote_execution
remote_execution_pyz = PYZ(remote_execution.pure, remote_execution.zipped_data,
        cipher=block_cipher)

remote_execution_exe = EXE(remote_execution_pyz,
        remote_execution.scripts,
        [],
        exclude_binaries=True,
        name='remote_execution',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True )

# event_analyzerd
event_analyzerd_pyz = PYZ(event_analyzerd.pure, event_analyzerd.zipped_data,
        cipher=block_cipher)

event_analyzerd_exe = EXE(event_analyzerd_pyz,
        event_analyzerd.scripts,
        [],
        exclude_binaries=True,
        name='event_analyzerd',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True )

# pcmk_alert
pcmk_alert_pyz = PYZ(pcmk_alert.pure, pcmk_alert.zipped_data,
        cipher=block_cipher)

pcmk_alert_exe = EXE(pcmk_alert_pyz,
        pcmk_alert.scripts,
        [],
        exclude_binaries=True,
        name='pcmk_alert',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True )

coll = COLLECT(
        # cortxha
        cortxha_exe,
        cortxha.binaries,
        cortxha.zipfiles,
        cortxha.datas,

        # dynamic_fid_service_ra
        dynamic_fid_service_ra_exe,
        dynamic_fid_service_ra.binaries,
        dynamic_fid_service_ra.zipfiles,
        dynamic_fid_service_ra.datas,

        # ha_setup
        ha_setup_exe,
        ha_setup.binaries,
        ha_setup.zipfiles,
        ha_setup.datas,

        # pre_disruptive_upgrade
        pre_disruptive_upgrade_exe,
        pre_disruptive_upgrade.binaries,
        pre_disruptive_upgrade.zipfiles,
        pre_disruptive_upgrade.datas,

        # post_disruptive_upgrade
        post_disruptive_upgrade_exe,
        post_disruptive_upgrade.binaries,
        post_disruptive_upgrade.zipfiles,
        post_disruptive_upgrade.datas,

        # remote_execution
        remote_execution_exe,
        remote_execution.binaries,
        remote_execution.zipfiles,
        remote_execution.datas,

        # event_analyzerd
        event_analyzerd_exe,
        event_analyzerd.binaries,
        event_analyzerd.zipfiles,
        event_analyzerd.datas,

        # pcmk_alert
        pcmk_alert_exe,
        pcmk_alert.binaries,
        pcmk_alert.zipfiles,
        pcmk_alert.datas,

        strip=False,
        upx=True,
        upx_exclude=[],
        name='lib')
