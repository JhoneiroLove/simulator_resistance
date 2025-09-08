import os
import pytest
from src.data.database import get_session
from src.data.database import engine, Base
from src.data.models import Gen, Antibiotico

@pytest.fixture(scope="session", autouse=True)
def set_sqlite_memory():
    """
    Esta fixture configura la variable de entorno DATABASE_URL
    para que toda la sesión de pruebas use SQLite en memoria.
    Inicializa la base de datos antes de cualquier test.
    """
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    Base.metadata.create_all(engine)
    yield

@pytest.fixture(autouse=True)
def populate_basic_data():
    """
    Población mínima de genes y antibióticos antes de cada test.
    """
    session = get_session()
    # Elimina todo para garantizar base limpia
    session.query(Gen).delete()
    session.query(Antibiotico).delete()
    session.commit()
    # Agrega datos base necesarios
    genes = [
        Gen(nombre="A", peso_resistencia=0.7, descripcion="Gen A"),
        Gen(nombre="B", peso_resistencia=0.3, descripcion="Gen B"),
    ]
    ab = Antibiotico(
        nombre="Antib1",
        concentracion_minima=0.2,
        concentracion_maxima=1.0,
        tipo="Penicilina",
    )
    session.add_all(genes + [ab])
    session.commit()
    session.close()