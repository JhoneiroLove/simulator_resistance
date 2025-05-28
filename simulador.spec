# -*- mode: python ; coding: utf-8 -*-
import os

project_root = r'C:\Tesis\SImulador evolutivo'  # ruta absoluta a tu proyecto

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'style.qss'), '.'),
        (os.path.join(project_root, 'resistencia.db'), '.'),
        (os.path.join(project_root, 'src', 'migrations'), 'migrations'),  # <--- incluye migraciones
    ],
    hiddenimports=[],
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