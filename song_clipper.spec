# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Song Clipper
# Run with: pyinstaller song_clipper.spec

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

# Path to tkinterdnd2 native DLLs
TKDND_DIR = os.path.join(
    os.environ.get('APPDATA', ''),
    r'Python\Python314\site-packages\tkinterdnd2\tkdnd'
)

# Fallback to site-packages if APPDATA path doesn't exist
if not os.path.exists(TKDND_DIR):
    import site
    for sp in site.getsitepackages():
        candidate = os.path.join(sp, 'tkinterdnd2', 'tkdnd')
        if os.path.exists(candidate):
            TKDND_DIR = candidate
            break

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['app'],
    binaries=[],
    datas=[
        # Bundle tkinterdnd2 native DLL and Tcl scripts
        (os.path.join(TKDND_DIR, 'win-x64', '*'), 'tkinterdnd2/tkdnd/win-x64'),
        (os.path.join(TKDND_DIR, 'win-arm64', '*'), 'tkinterdnd2/tkdnd/win-arm64'),
    ],
    hiddenimports=[
        'tkinterdnd2',
        'tkinterdnd2.TkinterDnD',
        'ui',
        'cutter',
        'validation',
        'theme',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SongClipper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SongClipper',
)
