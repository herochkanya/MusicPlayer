# MusicPlayerWin.spec

# Paste 
# python -m PyInstaller MusicPlayerWin.spec
# to create an .exe program

import sys
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

datas = [
    ('interface', 'interface'),  # HTML/JS/CSS
    ('bin', 'bin'),              # resources (icons, etc.)
]

binaries = [
    ('bin/vlc/libvlc.dll', 'bin/vlc'),
    ('bin/vlc/libvlccore.dll', 'bin/vlc'),
]

import os
vlc_plugins_path = os.path.join('bin', 'vlc', 'plugins')
if os.path.exists(vlc_plugins_path):
    binaries.append((vlc_plugins_path, 'bin/vlc/plugins'))

# Python
datas += collect_data_files('core')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    icon='bin/app.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='MusicPlayer'
)
