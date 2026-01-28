# MusicPlayerWin.spec
# Build with: python -m PyInstaller --clean MusicPlayerWin.spec

import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = collect_dynamic_libs('soundfile')
binaries += collect_dynamic_libs('numpy')
binaries += collect_dynamic_libs('scipy')

datas = [
    ('interface', 'interface'),
    ('bin', 'bin'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'scipy.signal', 
        'numpy', 
        'sounddevice', 
        'pynput.keyboard._win32', 
        'pynput.mouse._win32'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['winrt', 'winsdk', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MusicPlayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, 
    icon='bin/app.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MusicPlayer',
)
