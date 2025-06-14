import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "app.log")

    # Obtener el nivel de log desde una variable de entorno, con INFO como valor por defecto.
    log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Obtener el logger raíz y limpiarle los manejadores para evitar duplicados.
    logger = logging.getLogger()
    logger.setLevel(log_level)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Crear un formateador estándar.
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configurar un manejador para la consola.
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)

    # Configurar un manejador de archivos rotativo (5MB por archivo, hasta 5 archivos de respaldo).
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, mode="w"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Añadir los manejadores al logger.
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logging.info(f"Logging configured with level {log_level_str}.")
