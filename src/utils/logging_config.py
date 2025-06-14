import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Determinar el directorio adecuado para los registros en función del sistema operativo.
    app_name = "SrbSimulator"  # Nombre de la carpeta específica de la aplicación
    if os.name == 'nt':  # Windows
        base_path = os.getenv('APPDATA')
        if not base_path:  # Recurso alternativo si APPDATA no está configurado 
            base_path = os.path.expanduser('~')
        log_dir = os.path.join(base_path, app_name, "logs")
    else:  # macOS, Linux (utilizando una carpeta oculta en el directorio de inicio del usuario)
        log_dir = os.path.join(os.path.expanduser('~'), f".{app_name.lower()}_logs")

    # Crear el directorio de logs si no existe; maneja también los directorios padre
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "app.log")

    # Obtener el nivel de log desde una variable de entorno, con INFO como valor por defecto.
    log_level_str = os.environ.get("LOG_LEVEL", "DEBUG").upper() # DEBUG, INFO, WARNING, ERROR, CRITICAL
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
