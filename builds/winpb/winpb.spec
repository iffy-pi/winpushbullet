# -*- mode: python ; coding: utf-8 -*-
pb_added_files = [('..\\..\\pb-icon.ico', '.')]
pb_a = Analysis(
    ['..\\..\\pb.py'],
    pathex=[],
    binaries=[],
    datas=pb_added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pb_pyz = PYZ(pb_a.pure)
pb_exe = EXE(
    pb_pyz,
    pb_a.scripts,
    [],
    exclude_binaries=True,
    name='pb',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='.',
    icon='..\\..\\pb-icon.ico'
)



pc_plb_added_files = [ ('..\\assets\\pushbullet-icon.png', '.'), ('..\\..\\pullbullet-icon.ico', '.') ]
pc_plb_a = Analysis(
    ['..\\..\\pc_pullbullet.py'],
    pathex=[],
    binaries=[],
    datas=pc_plb_added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pc_plb_pyz = PYZ(pc_plb_a.pure)
pc_plb_exe = EXE(
    pc_plb_pyz,
    pc_plb_a.scripts,
    [],
    exclude_binaries=True,
    name='PC_PullBullet',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='.',
    icon='..\\..\\pullbullet-icon.ico'
)


pc_psb_added_files = [ ('..\\assets\\pushbullet-icon.png', '.'), ('..\\..\\pushbullet-icon.ico', '.') ]
pc_psb_a = Analysis(
    ['..\\..\\pc_pushbullet.py'],
    pathex=[],
    binaries=[],
    datas=pc_psb_added_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pc_psb_pyz = PYZ(pc_psb_a.pure)

pc_psb_exe = EXE(
    pc_psb_pyz,
    pc_psb_a.scripts,
    [],
    exclude_binaries=True,
    name='PC_PushBullet',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='.',
    icon='..\\..\\pushbullet-icon.ico'
)



coll = COLLECT(
    pb_exe,
    pb_a.binaries,
    pb_a.datas,
    pc_plb_exe,
    pc_plb_a.binaries,
    pc_plb_a.datas,
    pc_psb_exe,
    pc_psb_a.binaries,
    pc_psb_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WinPushBullet',
)
