"""
Script de diagnóstico para debug del ejecutable.
Ejecuta este script para verificar qué está fallando en el startup.
"""

import sys
import os
import traceback
from pathlib import Path


def check_environment():
    """Verifica el entorno de ejecución"""
    print("=" * 70)
    print("DIAGNÓSTICO DE STARTUP - SIMULADOR EVOLUTIVO")
    print("=" * 70)
    print()

    # 1. Información de Python
    print("[1] Información de Python:")
    print(f"    Versión: {sys.version}")
    print(f"    Ejecutable: {sys.executable}")
    print(f"    Plataforma: {sys.platform}")
    print(f"    Path: {sys.path[:3]}...")
    print()

    # 2. Directorio de trabajo
    print("[2] Directorios:")
    print(f"    CWD: {os.getcwd()}")
    print(f"    __file__: {os.path.abspath(__file__)}")
    print(f"    Script dir: {os.path.dirname(os.path.abspath(__file__))}")

    # Detectar si estamos en PyInstaller
    if getattr(sys, "frozen", False):
        print(f"    MODO: PyInstaller (frozen)")
        print(f"    _MEIPASS: {sys._MEIPASS}")
    else:
        print(f"    MODO: Python normal")
    print()

    # 3. Verificar imports críticos
    print("[3] Verificando imports críticos:")
    critical_imports = [
        "PyQt5.QtWidgets",
        "PyQt5.QtCore",
        "numpy",
        "pandas",
        "matplotlib",
        "sqlalchemy",
    ]

    for module_name in critical_imports:
        try:
            __import__(module_name)
            print(f"    ✓ {module_name}")
        except ImportError as e:
            print(f"    ✗ {module_name} - ERROR: {e}")

    print()

    # 4. Verificar estructura de archivos
    print("[4] Verificando estructura de archivos:")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS

    critical_files = [
        "style.qss",
        "src/gui/main_window.py",
        "src/data/database.py",
        "src/utils/logging_config.py",
    ]

    for file_path in critical_files:
        full_path = os.path.join(base_dir, file_path)
        exists = os.path.exists(full_path)
        symbol = "✓" if exists else "✗"
        print(f"    {symbol} {file_path}: {full_path}")

    print()

    # 5. Test de imports del proyecto
    print("[5] Test de imports del proyecto:")

    project_imports = [
        ("src.utils.logging_config", "setup_logging"),
        ("src.data.database", "init_db"),
        ("src.gui.main_window", "MainWindow"),
    ]

    for module_name, obj_name in project_imports:
        try:
            module = __import__(module_name, fromlist=[obj_name])
            obj = getattr(module, obj_name)
            print(f"    ✓ {module_name}.{obj_name}")
        except Exception as e:
            print(f"    ✗ {module_name}.{obj_name} - ERROR:")
            print(f"       {str(e)}")
            traceback.print_exc()

    print()

    # 6. Test de inicialización de componentes
    print("[6] Test de componentes:")

    try:
        print("    Configurando logging...")
        from src.utils.logging_config import setup_logging

        setup_logging()
        print("    ✓ Logging configurado")
    except Exception as e:
        print(f"    ✗ Error en logging: {e}")
        traceback.print_exc()

    try:
        print("    Inicializando base de datos...")
        from src.data.database import init_db

        init_db()
        print("    ✓ Base de datos inicializada")
    except Exception as e:
        print(f"    ✗ Error en base de datos: {e}")
        traceback.print_exc()

    print()
    print("=" * 70)
    print("DIAGNÓSTICO COMPLETADO")
    print("=" * 70)
    print()
    print("Si todos los checks son ✓, el problema puede estar en:")
    print("  - Creación de la ventana principal (MainWindow)")
    print("  - Conflictos de threading en Qt")
    print("  - Recursos de Qt no empaquetados correctamente")
    print()
    input("Presiona Enter para salir...")


if __name__ == "__main__":
    try:
        check_environment()
    except Exception as e:
        print(f"\n\nERROR FATAL: {e}")
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
