import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

def get_paths():
    """
    Devuelve dos rutas:
    - base_path: ruta donde PyInstaller extrae recursos (migrations).
    - user_data_dir: ruta persistente para base de datos (APPDATA).
    """
    if getattr(sys, "frozen", False):
        # Ruta temporal donde PyInstaller extrae el bundle
        base_path = sys._MEIPASS

        # Ruta persistente del usuario para datos que cambian (BD)
        user_data_dir = os.path.join(
            os.environ.get("APPDATA", ""), "SimuladorEvolutivo"
        )
        os.makedirs(user_data_dir, exist_ok=True)

        return base_path, user_data_dir
    else:
        # En modo desarrollo todo en proyecto
        this_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.abspath(os.path.join(this_dir, ".."))
        user_data_dir = base_path
        return base_path, user_data_dir

base_path, user_data_dir = get_paths()

# Base de datos se almacena en carpeta persistente del usuario
db_path = os.path.join(user_data_dir, "resistencia.db")
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = scoped_session(sessionmaker(bind=engine))

def init_db():
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
    finally:
        raw_conn.close()

    print("✅ Base de datos inicializada y poblada.")

def get_session():
    return Session()