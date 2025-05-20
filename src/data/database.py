import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

# Determinar ruta base según entorno
if getattr(sys, "frozen", False):
    # PyInstaller: archivos extraídos en _MEIPASS
    base_path = sys._MEIPASS
else:
    # Desarrollo: nivelar a la carpeta src
    this_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.abspath(os.path.join(this_dir, ".."))

# Rutas a base de datos y migraciones
db_path = os.path.join(base_path, "resistencia.db")
DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = scoped_session(sessionmaker(bind=engine))

def init_db():
    # 1) Crear esquema según modelos
    Base.metadata.create_all(engine)

    # 2) Ruta a migraciones: debe existir en base_path/migrations
    migrations_folder = os.path.join(base_path, "migrations")
    if not os.path.isdir(migrations_folder):
        raise FileNotFoundError(f"No existe migrations en: {migrations_folder}")

    # 3) Ejecutar .sql secuencialmente
    for fname in sorted(os.listdir(migrations_folder)):
        if not fname.lower().endswith(".sql"):
            continue
        path = os.path.join(migrations_folder, fname)
        print(f"🔄 Ejecutando {path} ...")
        raw_conn = engine.raw_connection()
        try:
            cursor = raw_conn.cursor()
            with open(path, "r", encoding="utf-8") as f:
                cursor.executescript(f.read())
            raw_conn.commit()
        finally:
            raw_conn.close()

    print("✅ Base de datos inicializada y poblada.")

def get_session():
    return Session()