"""
Configuración de pytest para tests del Simulador Evolutivo AST.

Este archivo configura fixtures globales para todos los tests.
Todas las fixtures usan base de datos en memoria (SQLite :memory:).
"""

import os
import pytest
from src.data.database import get_session, engine, Base


@pytest.fixture(scope="session", autouse=True)
def set_sqlite_memory():
    """
    Configura SQLite en memoria para toda la sesión de tests.

    Las migraciones NO se ejecutan automáticamente en tests.
    Cada test debe crear las tablas que necesite manualmente.
    """
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

    # Crear todas las tablas definidas en models.py
    Base.metadata.create_all(engine)

    yield

    # Cleanup
    Base.metadata.drop_all(engine)
