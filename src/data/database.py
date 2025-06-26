import os
import re
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

def get_paths():
    """
    - base_path: ruta donde PyInstaller extrae recursos (migrations).
    - user_data_dir: ruta persistente para base de datos (APPDATA).
    """
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS

        user_data_dir = os.path.join(
            os.environ.get("APPDATA", ""), "SimuladorEvolutivo"
        )
        os.makedirs(user_data_dir, exist_ok=True)

        return base_path, user_data_dir
    else:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        base_path = os.path.join(project_root, "src")
        data_dir = os.path.join(project_root, "data")
        os.makedirs(data_dir, exist_ok=True)
        return base_path, data_dir

base_path, user_data_dir = get_paths()

db_path = os.path.join(user_data_dir, "resistencia.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{db_path}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = scoped_session(sessionmaker(bind=engine))

def init_db():
    """
    Inicializa la base de datos y aplica las migraciones pendientes de forma inteligente.
    """
    migrations_folder = os.path.join(base_path, "migrations")
    if not os.path.isdir(migrations_folder):
        print(f"⚠️  No se encontró la carpeta de migraciones: {migrations_folder}")
        return

    raw_conn = engine.raw_connection()
    cursor = raw_conn.cursor()

    try:
        # 1. Obtener la versión actual de la BD
        current_version = 0
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='db_version'")
            if cursor.fetchone():
                cursor.execute("SELECT version_num FROM db_version WHERE id = 1")
                version_row = cursor.fetchone()
                if version_row:
                    current_version = version_row[0]
        except Exception:
            current_version = 0
        
        print(f"ℹ️ Versión actual de la BD: {current_version}")

        # 2. Aplicar migraciones pendientes
        migration_files = sorted(os.listdir(migrations_folder))
        for fname in migration_files:
            match = re.match(r"(\d+)_.*\.sql", fname)
            if not match:
                continue

            file_version = int(match.group(1))

            if file_version > current_version:
                path = os.path.join(migrations_folder, fname)
                print(f"🆙 Aplicando migración v{file_version}: {fname}...")
                
                with open(path, "r", encoding="utf-8") as f:
                    script_content = f.read()
                    cursor.executescript(script_content)
                
                cursor.execute("UPDATE db_version SET version_num = ? WHERE id = 1", (file_version,))
                raw_conn.commit()
                print(f"✅ Migración v{file_version} aplicada exitosamente.")

    except Exception as e:
        print(f"❌ Error crítico durante la migración en '{fname}': {e}")
        raw_conn.rollback()
        raise
    finally:
        cursor.close()
        raw_conn.close()

    print("✅ Proceso de migración de base de datos completado.")

def get_session():
    return Session()