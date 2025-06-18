import os
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

def force_recreate_db():
    """Elimina la base de datos existente en AppData para forzar la recreación."""
    if os.path.exists(db_path):
        print(f"🗑️ Eliminando base de datos antigua en: {db_path}")
        try:
            os.remove(db_path)
            print("✅ Base de datos antigua eliminada.")
        except OSError as e:
            print(f"❌ Error al eliminar la base de datos: {e}")


def init_db():
    print(f"Creando BD en: {db_path}")
    # Crear tablas si no existen
    Base.metadata.create_all(engine)

    # Carpeta migrations dentro del bundle (base_path)
    migrations_folder = os.path.join(base_path, "migrations")
    if not os.path.isdir(migrations_folder):
        raise FileNotFoundError(f"No existe migrations en: {migrations_folder}")

    raw_conn = engine.raw_connection()
    try:
        cursor = raw_conn.cursor()
        for fname in sorted(os.listdir(migrations_folder)):
            if not fname.lower().endswith(".sql"):
                continue
            path = os.path.join(migrations_folder, fname)
            print(f"🔄 Ejecutando {path} ...")
            with open(path, "r", encoding="utf-8") as f:
                cursor.executescript(f.read())
        raw_conn.commit()
    except Exception as ex:
        print(f"❌ Error ejecutando migraciones: {ex}")
    finally:
        raw_conn.close()

    print("✅ Base de datos inicializada y poblada.")

def get_session():
    return Session()