from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

# Configurar engine y sesión global
engine = create_engine("sqlite:///resistencia.db")
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine))


def get_session():
    """Retorna una nueva sesión de base de datos."""
    return Session()