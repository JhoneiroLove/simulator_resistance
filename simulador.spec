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
        (os.path.join(project_root, 'src', 'migrations'), 'migrations'),
        (os.path.join(project_root, 'splash_screen.py'), '.'),
    ],
    hiddenimports=[
        'splash_screen',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        # NumPy completo
        'numpy',
        'numpy.core',
        'numpy.core._methods',
        'numpy.core._multiarray_umath',
        'numpy.core._dtype_ctypes',
        'numpy.lib',
        'numpy.lib.format',
        'numpy.linalg',
        'numpy.linalg._umath_linalg',
        'numpy.random',
        'numpy.random._common',
        'numpy.random._bounded_integers',
        'numpy.random._mt19937',
        'numpy.random._pcg64',
        'numpy.random._philox',
        'numpy.random._sfc64',
        'numpy.random._generator',
        'numpy.random.bit_generator',
        # SciPy
        'scipy',
        'scipy.sparse',
        'scipy.sparse.csgraph',
        'scipy.sparse.csgraph._validation',
        'scipy.special',
        'scipy.special._ufuncs_cxx',
        'scipy.integrate',
        'scipy.interpolate',
        # Pandas
        'pandas',
        'pandas._libs',
        'pandas._libs.tslibs',
        'pandas._libs.tslibs.timedeltas',
        # Matplotlib
        'matplotlib',
        'matplotlib.backends',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_agg',
        'matplotlib.figure',
        'matplotlib.pyplot',
        # Otros
        'seaborn',
        'pyqtgraph',
        'pyqtgraph.graphicsItems',
        'sqlalchemy',
        'sqlalchemy.ext',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.orm',
        'sqlalchemy.sql',
        'sqlalchemy.sql.default_comparator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'test', 'unittest'],
    noarchive=False,
    optimize=2,
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
    console=True,  # CAMBIAR A False después de debug
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