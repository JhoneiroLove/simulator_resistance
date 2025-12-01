"""
Green Software Optimization - RNF-5: Sostenibilidad

Optimizaciones para reducir consumo de recursos (CPU, memoria, I/O)
siguiendo principios de Green Software Engineering.

Autor: Sistema AST Simulator
Fecha: 1 de diciembre de 2025
"""

from functools import lru_cache
import logging
from typing import Any, Callable
from contextlib import contextmanager


class ResourceOptimizer:
    """Optimizador de recursos para reducir consumo energético."""

    # Cache global para resultados repetitivos
    _cache_enabled = True

    @staticmethod
    @contextmanager
    def database_session(session_factory):
        """
        Context manager para garantizar cierre de sesiones BD.

        RNF-5: Cierra automáticamente conexiones para liberar recursos.

        Usage:
            with ResourceOptimizer.database_session(get_session) as session:
                # usar session
                pass
            # session cerrado automáticamente
        """
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()  # RNF-5: Liberar conexión

    @staticmethod
    def cache_calculation(max_size=128):
        """
        Decorador para cachear cálculos costosos.

        RNF-5: Evita recalcular genotipo-fenotipo idénticos.

        Args:
            max_size: Tamaño máximo del cache LRU

        Usage:
            @ResourceOptimizer.cache_calculation(max_size=256)
            def calculate_mic(genotype, antibiotic):
                # cálculo pesado
                return mic_value
        """

        def decorator(func):
            if ResourceOptimizer._cache_enabled:
                return lru_cache(maxsize=max_size)(func)
            return func

        return decorator

    @staticmethod
    def lazy_import(module_path: str):
        """
        Import lazy de módulos pesados.

        RNF-5: Reduce tiempo de inicio cargando solo lo necesario.

        Args:
            module_path: Ruta del módulo (ej: "numpy.linalg")

        Returns:
            Módulo importado
        """
        import importlib

        return importlib.import_module(module_path)

    @staticmethod
    def batch_database_operations(
        session, items: list, operation: Callable, batch_size: int = 100
    ):
        """
        Ejecuta operaciones BD en lotes para reducir I/O.

        RNF-5: Reduce roundtrips a BD agrupando operaciones.

        Args:
            session: Sesión SQLAlchemy
            items: Lista de items a procesar
            operation: Función que procesa cada item
            batch_size: Tamaño del lote

        Usage:
            def save_profile(session, profile):
                session.add(profile)

            ResourceOptimizer.batch_database_operations(
                session, profiles, save_profile, batch_size=50
            )
        """
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            for item in batch:
                operation(session, item)
            session.flush()  # Flush cada lote
            logging.info(f"[GreenSW] Procesado lote {i // batch_size + 1}")

        session.commit()


class MemoryOptimizer:
    """Optimizador de uso de memoria."""

    @staticmethod
    def cleanup_large_objects(*objects):
        """
        Limpia objetos grandes de memoria.

        RNF-5: Libera memoria explícitamente para reducir presión en GC.

        Args:
            *objects: Objetos a limpiar
        """
        import gc

        for obj in objects:
            del obj
        gc.collect()  # Force garbage collection
        logging.debug("[GreenSW] Memoria liberada")

    @staticmethod
    def use_generator(data_source: Callable):
        """
        Convierte funciones que retornan listas grandes a generators.

        RNF-5: Reduce memory footprint usando iteradores lazy.

        Args:
            data_source: Función que genera datos

        Returns:
            Generator en lugar de lista

        Usage:
            @MemoryOptimizer.use_generator
            def get_large_dataset():
                for i in range(1000000):
                    yield calculate(i)
        """
        return (item for item in data_source())


class QueryOptimizer:
    """Optimizador de queries de base de datos."""

    @staticmethod
    def add_indexes(session, model, columns: list):
        """
        Agrega índices a columnas frecuentemente consultadas.

        RNF-5: Acelera queries reduciendo I/O de disco.

        Args:
            session: Sesión SQLAlchemy
            model: Modelo SQLAlchemy
            columns: Lista de nombres de columnas a indexar

        Note:
            Debe ejecutarse una sola vez durante setup inicial.
        """
        from sqlalchemy import Index

        for col_name in columns:
            index_name = f"idx_{model.__tablename__}_{col_name}"
            col = getattr(model, col_name)
            index = Index(index_name, col)

            # Crear índice solo si no existe
            try:
                index.create(session.bind, checkfirst=True)
                logging.info(f"[GreenSW] Índice creado: {index_name}")
            except Exception as e:
                logging.debug(f"[GreenSW] Índice ya existe: {index_name}")

    @staticmethod
    def eager_load(query, *relationships):
        """
        Carga relaciones en una sola query (evita N+1).

        RNF-5: Reduce queries múltiples a BD.

        Args:
            query: Query SQLAlchemy
            *relationships: Nombres de relaciones a cargar

        Returns:
            Query con joinedload aplicado

        Usage:
            query = session.query(BacteriaProfile)
            query = QueryOptimizer.eager_load(query, 'mutations', 'mics')
        """
        from sqlalchemy.orm import joinedload

        for rel in relationships:
            query = query.options(joinedload(rel))

        return query


# RNF-5: Cache global para genotipo-fenotipo
@ResourceOptimizer.cache_calculation(max_size=256)
def cached_genotype_phenotype(genotype_json: str, antibiotic: str) -> float:
    """
    Calcula MIC cacheado para evitar recalcular combinaciones repetidas.

    Args:
        genotype_json: JSON string del genotipo (hasheable)
        antibiotic: Nombre del antibiótico

    Returns:
        MIC calculado

    Note:
        Esta es una función helper. El cálculo real debe delegarse
        a GenotypePhenotypeCalculator.
    """
    import json
    from src.core.genotype_phenotype_calculator import GenotypePhenotypeCalculator

    genotype_dict = json.loads(genotype_json)
    calculator = GenotypePhenotypeCalculator()
    mic = calculator.calculate_mic(genotype_dict, antibiotic)

    logging.debug(f"[GreenSW] MIC calculado (cacheado): {antibiotic} = {mic}")
    return mic


def optimize_database_connection(engine):
    """
    Configura connection pooling para reducir overhead de conexiones.

    RNF-5: Reutiliza conexiones en lugar de crear nuevas.

    Args:
        engine: SQLAlchemy engine

    Usage:
        engine = create_engine(...)
        optimize_database_connection(engine)
    """
    from sqlalchemy.pool import QueuePool

    # Configurar pool
    engine.pool = QueuePool(
        engine.pool._creator,
        pool_size=5,  # Máximo 5 conexiones simultáneas
        max_overflow=10,  # +10 en picos
        timeout=30,
        recycle=3600,  # Reciclar conexiones cada hora
    )

    logging.info("[GreenSW] Connection pooling optimizado")
