# -*- mode: python ; coding: utf-8 -*-
import os
import sys

project_root = os.path.abspath(os.path.dirname(sys.argv[0]))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/migrations', 'migrations'),
        ('style.qss', '.'),
    ],
    hiddenimports=[
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'numpy.core._add_newdocs',  # ← AGREGAR ESTO
        'numpy.core._add_newdocs_scalars',  # ← Y ESTO
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SimuladorEvolutivo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='simulador_evolutivo.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SimuladorEvolutivo',
)