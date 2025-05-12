import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

DATABASE_URL = "sqlite:///resistencia.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = scoped_session(sessionmaker(bind=engine))

def init_db():
    # 1) Crear esquema según modelos
    Base.metadata.create_all(engine)

    # 2) Ruta a migrations
    migrations_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "migrations")
    )
    if not os.path.isdir(migrations_folder):
        raise FileNotFoundError(f"No existe migrations en: {migrations_folder}")

    # 3) Ejecutar cada .sql con cursor.executescript()
    for fname in sorted(os.listdir(migrations_folder)):
        if not fname.lower().endswith(".sql"):
            continue
        path = os.path.join(migrations_folder, fname)
        print(f"🔄 Ejecutando {path} ...")

        # raw_connection() no es context manager
        raw_conn = engine.raw_connection()
        try:
            cursor = raw_conn.cursor()
            with open(path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            raw_conn.commit()
        finally:
            raw_conn.close()

    print("✅ Base de datos inicializada y poblada.")

def get_session():
    return Session()