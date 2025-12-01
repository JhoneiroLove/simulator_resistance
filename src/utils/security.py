"""
Security and Validation Module - RNF: Seguridad

Proporciona funciones de validación y sanitización para garantizar
la seguridad de los datos ingresados y recuperados de la base de datos.

Autor: Sistema AST Simulator
Fecha: 30 de noviembre de 2025
"""

import re
from typing import Any, Optional, Union
import html


class InputValidator:
    """Validador de inputs del usuario para RNF-3: Seguridad."""

    # Patrones seguros para validación
    SAFE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\s]+$")
    SAFE_ALPHANUMERIC_PATTERN = re.compile(r"^[a-zA-Z0-9]+$")
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(;|\-\-|\/\*|\*\/|xp_|sp_)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r'(\'|"|\`)',
    ]

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """
        Sanitiza un string eliminando caracteres peligrosos.

        Args:
            value: String a sanitizar
            max_length: Longitud máxima permitida

        Returns:
            String sanitizado

        Raises:
            ValueError: Si el string contiene patrones peligrosos
        """
        if not isinstance(value, str):
            raise ValueError(f"Se esperaba string, se recibió {type(value).__name__}")

        # Eliminar espacios al inicio/fin
        sanitized = value.strip()

        # Limitar longitud
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        # Detectar intentos de SQL injection
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError(
                    f"Patrón peligroso detectado en input: {value[:50]}..."
                )

        # Escapar HTML para prevenir XSS (aunque PyQt no es vulnerable, es buena práctica)
        sanitized = html.escape(sanitized)

        return sanitized

    @staticmethod
    def validate_panel_name(name: str) -> str:
        """
        Valida y sanitiza un nombre de panel de antibióticos.

        Args:
            name: Nombre del panel

        Returns:
            Nombre validado y sanitizado

        Raises:
            ValueError: Si el nombre no es válido
        """
        if not name:
            raise ValueError("El nombre del panel no puede estar vacío")

        sanitized = InputValidator.sanitize_string(name, max_length=100)

        # Validar que solo contenga caracteres seguros
        if not InputValidator.SAFE_NAME_PATTERN.match(sanitized):
            raise ValueError(
                f"Nombre de panel inválido: '{name}'. "
                "Solo se permiten letras, números, guiones y espacios."
            )

        return sanitized

    @staticmethod
    def validate_numeric_range(
        value: Union[int, float],
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        field_name: str = "valor",
    ) -> Union[int, float]:
        """
        Valida que un valor numérico esté en el rango permitido.

        Args:
            value: Valor a validar
            min_val: Valor mínimo permitido
            max_val: Valor máximo permitido
            field_name: Nombre del campo para mensajes de error

        Returns:
            Valor validado

        Raises:
            ValueError: Si el valor está fuera de rango
        """
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"{field_name}: se esperaba número, se recibió {type(value).__name__}"
            )

        if min_val is not None and value < min_val:
            raise ValueError(
                f"{field_name}: {value} está por debajo del mínimo permitido ({min_val})"
            )

        if max_val is not None and value > max_val:
            raise ValueError(
                f"{field_name}: {value} está por encima del máximo permitido ({max_val})"
            )

        return value

    @staticmethod
    def validate_inoculum(value: float) -> float:
        """
        Valida el valor de inóculo según estándares CLSI.

        Args:
            value: Valor en McFarland

        Returns:
            Valor validado

        Raises:
            ValueError: Si está fuera del rango CLSI
        """
        return InputValidator.validate_numeric_range(
            value, min_val=0.3, max_val=0.7, field_name="Inóculo (McFarland)"
        )

    @staticmethod
    def validate_temperature(value: float) -> float:
        """
        Valida la temperatura de incubación según estándares CLSI.

        Args:
            value: Temperatura en °C

        Returns:
            Valor validado

        Raises:
            ValueError: Si está fuera del rango CLSI
        """
        return InputValidator.validate_numeric_range(
            value, min_val=35.0, max_val=37.0, field_name="Temperatura (°C)"
        )

    @staticmethod
    def validate_bacteria_profile_id(profile_id: Any) -> int:
        """
        Valida un ID de perfil bacteriano.

        Args:
            profile_id: ID a validar

        Returns:
            ID validado como entero

        Raises:
            ValueError: Si el ID no es válido
        """
        if profile_id is None:
            raise ValueError("ID de perfil bacteriano no puede ser None")

        try:
            id_int = int(profile_id)
        except (ValueError, TypeError):
            raise ValueError(
                f"ID de perfil inválido: '{profile_id}'. Debe ser un número entero."
            )

        if id_int <= 0:
            raise ValueError(f"ID de perfil debe ser positivo, se recibió: {id_int}")

        return id_int

    @staticmethod
    def sanitize_database_string(value: str) -> str:
        """
        Sanitiza strings provenientes de la base de datos.

        Args:
            value: String de la BD

        Returns:
            String sanitizado y seguro para mostrar en UI
        """
        if not isinstance(value, str):
            return str(value)

        # Eliminar caracteres de control
        sanitized = "".join(char for char in value if ord(char) >= 32 or char == "\n")

        # Limitar longitud para prevenir DoS en UI
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000] + "..."

        # Escapar HTML
        sanitized = html.escape(sanitized)

        return sanitized

    @staticmethod
    def validate_file_path(path: str, allowed_extensions: Optional[list] = None) -> str:
        """
        Valida una ruta de archivo para exportación.

        Args:
            path: Ruta del archivo
            allowed_extensions: Lista de extensiones permitidas (ej: ['.csv', '.xlsx'])

        Returns:
            Ruta validada

        Raises:
            ValueError: Si la ruta no es segura
        """
        if not path:
            raise ValueError("La ruta del archivo no puede estar vacía")

        # Detectar path traversal
        if ".." in path or path.startswith("/") or ":" in path[1:]:
            raise ValueError("Ruta de archivo potencialmente insegura detectada")

        # Validar extensión si se especifica
        if allowed_extensions:
            if not any(path.lower().endswith(ext) for ext in allowed_extensions):
                raise ValueError(
                    f"Extensión de archivo no permitida. "
                    f"Permitidas: {', '.join(allowed_extensions)}"
                )

        return path


class SecurityLogger:
    """Logger para eventos de seguridad."""

    @staticmethod
    def log_validation_error(field: str, value: Any, error: str):
        """
        Registra un error de validación.

        Args:
            field: Campo que falló la validación
            value: Valor que causó el error
            error: Mensaje de error
        """
        # En producción, esto debería escribir a un log file
        print(f"[SECURITY] Validación fallida - Campo: {field}, Error: {error}")

    @staticmethod
    def log_suspicious_activity(activity: str, details: str):
        """
        Registra actividad sospechosa.

        Args:
            activity: Tipo de actividad
            details: Detalles de la actividad
        """
        # En producción, esto debería escribir a un log file y alertar
        print(f"[SECURITY ALERT] {activity}: {details}")


def safe_format_error_message(error: Exception) -> str:
    """
    Formatea un mensaje de error de manera segura para mostrar al usuario.

    Args:
        error: Excepción capturada

    Returns:
        Mensaje seguro para mostrar
    """
    # No exponer detalles internos del sistema
    error_str = str(error)

    # Limitar longitud
    if len(error_str) > 200:
        error_str = error_str[:200] + "..."

    # Sanitizar
    error_str = html.escape(error_str)

    return error_str
