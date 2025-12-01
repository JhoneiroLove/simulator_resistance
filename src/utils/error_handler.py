"""
Error Handler - RNF-4: Protección

Manejo centralizado de errores con logging estructurado,
rollback automático y recuperación de fallos.

Autor: Sistema AST Simulator
Fecha: 1 de diciembre de 2025
"""

import logging
import traceback
from datetime import datetime
from typing import Optional, Callable, Any
from functools import wraps
from PyQt5.QtWidgets import QMessageBox


class ErrorHandler:
    """Manejador centralizado de errores para RNF-4."""

    @staticmethod
    def setup_logging():
        """Configura logging estructurado para toda la aplicación."""
        log_format = "[%(asctime)s] %(levelname)-8s | %(name)-20s | %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler("logs/app.log", encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        # Logger específico para errores
        error_logger = logging.getLogger("error")
        error_handler = logging.FileHandler("logs/errors.log", encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(log_format, date_format))
        error_logger.addHandler(error_handler)

    @staticmethod
    def log_error(
        component: str,
        error: Exception,
        context: Optional[dict] = None,
        critical: bool = False,
    ):
        """
        Registra un error con contexto completo.

        Args:
            component: Componente donde ocurrió el error
            error: Excepción capturada
            context: Datos adicionales del contexto
            critical: Si True, marca como error crítico
        """
        logger = logging.getLogger("error")

        error_info = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
        }

        if critical:
            logger.critical(
                f"CRITICAL ERROR in {component}: {error}\n"
                f"Context: {context}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
        else:
            logger.error(
                f"ERROR in {component}: {error}\n"
                f"Context: {context}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )

    @staticmethod
    def safe_execute(
        func: Callable,
        component: str,
        fallback_value: Any = None,
        show_message: bool = True,
        parent_widget=None,
    ) -> Any:
        """
        Ejecuta una función de forma segura con manejo de errores.

        Args:
            func: Función a ejecutar
            component: Nombre del componente para logging
            fallback_value: Valor a retornar si falla
            show_message: Si True, muestra mensaje de error al usuario
            parent_widget: Widget padre para el mensaje de error

        Returns:
            Resultado de func() o fallback_value si falla
        """
        try:
            return func()
        except Exception as e:
            ErrorHandler.log_error(component, e)

            if show_message and parent_widget:
                QMessageBox.critical(
                    parent_widget,
                    "Error",
                    f"Ocurrió un error en {component}:\n\n{str(e)}\n\n"
                    "El error ha sido registrado. Por favor revise los logs.",
                )

            return fallback_value


def safe_method(component: str = None, fallback_value: Any = None):
    """
    Decorador para métodos que requieren manejo de errores.

    Args:
        component: Nombre del componente (por defecto usa el nombre del método)
        fallback_value: Valor a retornar si falla

    Usage:
        @safe_method(component="ASTPanelWidget", fallback_value=[])
        def _load_panels(self):
            # código que puede fallar
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            comp_name = component or f"{func.__qualname__}"
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(
                    comp_name,
                    e,
                    context={"args": str(args)[:200], "kwargs": str(kwargs)[:200]},
                )
                return fallback_value

        return wrapper

    return decorator


class DatabaseErrorHandler:
    """Manejador de errores específico para operaciones de BD."""

    @staticmethod
    def safe_transaction(session, operations: Callable, component: str) -> bool:
        """
        Ejecuta una transacción de BD con rollback automático.

        Args:
            session: Sesión de SQLAlchemy
            operations: Función que ejecuta las operaciones
            component: Nombre del componente para logging

        Returns:
            True si éxito, False si falla
        """
        try:
            operations()
            session.commit()
            logging.info(f"[{component}] Transacción completada exitosamente")
            return True
        except Exception as e:
            session.rollback()
            ErrorHandler.log_error(
                component,
                e,
                context={"action": "database_transaction"},
                critical=True,
            )
            logging.warning(f"[{component}] Rollback ejecutado por error: {e}")
            return False
        finally:
            # Asegurar que la sesión se cierra
            if session:
                session.close()

    @staticmethod
    def safe_query(session, query_func: Callable, component: str, default=None):
        """
        Ejecuta una query de BD de forma segura.

        Args:
            session: Sesión de SQLAlchemy
            query_func: Función que ejecuta la query
            component: Nombre del componente
            default: Valor por defecto si falla

        Returns:
            Resultado de la query o default si falla
        """
        try:
            return query_func()
        except Exception as e:
            ErrorHandler.log_error(component, e, context={"action": "database_query"})
            return default


class ThreadErrorHandler:
    """Manejador de errores para QThread workers."""

    @staticmethod
    def safe_run(worker_func: Callable, component: str, error_signal=None):
        """
        Envuelve el método run() de un QThread con manejo de errores.

        Args:
            worker_func: Función run() del worker
            component: Nombre del worker
            error_signal: pyqtSignal para emitir errores

        Returns:
            Función wrapper que maneja errores
        """

        @wraps(worker_func)
        def wrapper(*args, **kwargs):
            try:
                return worker_func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.log_error(
                    component, e, context={"worker": component}, critical=True
                )

                if error_signal:
                    error_signal.emit(f"Error en {component}: {str(e)[:100]}...")
                else:
                    logging.critical(
                        f"[{component}] Worker falló sin signal de error configurado"
                    )

        return wrapper
