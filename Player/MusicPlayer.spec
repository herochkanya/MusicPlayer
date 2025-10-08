# MusicPlayer.spec
# -*- mode: python -*-

import sys
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.building.build_main import Analysis

# включаємо всі файли з core та interface + bin
datas = [
    ('interface', 'interface'),  # папка HTML/JS/CSS
    ('bin', 'bin'),              # папка з іконками/ресурсами
]

# Якщо є інші пакети з ресурсами:
datas += collect_data_files('core')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
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
    icon='bin/app.ico'  # твоя іконка
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
