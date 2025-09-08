# -*- mode: python ; coding: utf-8 -*-
import os
import sys

project_root = os.path.abspath(os.path.dirname(sys.argv[0]))

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'simulador_evolutivo.ico'), '.'),
        (os.path.join(project_root, 'style.qss'), '.'),
        (os.path.join(project_root, 'data', 'resistencia.db'), 'data'),
        (os.path.join(project_root, 'src', 'migrations'), 'migrations'),
        (os.path.join(project_root, 'splash_screen.py'), '.'),
    ],
    hiddenimports=[
        'splash_screen',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
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
    console=False,
    icon='simulador_evolutivo.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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