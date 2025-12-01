"""
Tests para módulo de seguridad - RNF-3: Seguridad

Tests unitarios para validar las funciones de seguridad
y sanitización de inputs.

Autor: Sistema AST Simulator
Fecha: 30 de noviembre de 2025
"""

import pytest
from src.utils.security import InputValidator, safe_format_error_message


class TestInputValidator:
    """Tests para InputValidator."""

    def test_sanitize_string_normal(self):
        """Test sanitización de string normal."""
        result = InputValidator.sanitize_string("Panel_Standard")
        assert result == "Panel_Standard"

    def test_sanitize_string_with_spaces(self):
        """Test sanitización con espacios extra."""
        result = InputValidator.sanitize_string("  Panel Test  ")
        assert result == "Panel Test"

    def test_sanitize_string_max_length(self):
        """Test límite de longitud."""
        long_string = "A" * 300
        result = InputValidator.sanitize_string(long_string, max_length=100)
        assert len(result) == 100

    def test_sanitize_string_sql_injection_select(self):
        """Test detección de SQL injection con SELECT."""
        with pytest.raises(ValueError, match="Patrón peligroso"):
            InputValidator.sanitize_string("Panel'; SELECT * FROM users--")

    def test_sanitize_string_sql_injection_drop(self):
        """Test detección de SQL injection con DROP."""
        with pytest.raises(ValueError, match="Patrón peligroso"):
            InputValidator.sanitize_string("Panel'; DROP TABLE panels;--")

    def test_sanitize_string_sql_injection_or(self):
        """Test detección de SQL injection con OR."""
        with pytest.raises(ValueError, match="Patrón peligroso"):
            InputValidator.sanitize_string("Panel' OR '1'='1")

    def test_sanitize_string_html_injection(self):
        """Test detección de patrones peligrosos con HTML."""
        with pytest.raises(ValueError, match="Patrón peligroso"):
            InputValidator.sanitize_string("<script>alert('xss')</script>")

    def test_validate_panel_name_valid(self):
        """Test validación de nombre de panel válido."""
        result = InputValidator.validate_panel_name("Pseudomonas_Standard_Panel")
        assert result == "Pseudomonas_Standard_Panel"

    def test_validate_panel_name_with_spaces(self):
        """Test validación de nombre con espacios."""
        result = InputValidator.validate_panel_name("Panel Test 123")
        assert result == "Panel Test 123"

    def test_validate_panel_name_empty(self):
        """Test validación de nombre vacío."""
        with pytest.raises(ValueError, match="no puede estar vacío"):
            InputValidator.validate_panel_name("")

    def test_validate_panel_name_special_chars(self):
        """Test rechazo de caracteres especiales."""
        with pytest.raises(ValueError, match="Nombre de panel inválido"):
            InputValidator.validate_panel_name("Panel@#$%")

    def test_validate_numeric_range_valid(self):
        """Test validación de rango numérico válido."""
        result = InputValidator.validate_numeric_range(5.0, min_val=0.0, max_val=10.0)
        assert result == 5.0

    def test_validate_numeric_range_below_min(self):
        """Test valor por debajo del mínimo."""
        with pytest.raises(ValueError, match="por debajo del mínimo"):
            InputValidator.validate_numeric_range(0.2, min_val=0.3, max_val=0.7)

    def test_validate_numeric_range_above_max(self):
        """Test valor por encima del máximo."""
        with pytest.raises(ValueError, match="por encima del máximo"):
            InputValidator.validate_numeric_range(0.8, min_val=0.3, max_val=0.7)

    def test_validate_numeric_range_not_number(self):
        """Test validación con tipo incorrecto."""
        with pytest.raises(ValueError, match="se esperaba número"):
            InputValidator.validate_numeric_range("not_a_number", min_val=0, max_val=10)

    def test_validate_inoculum_valid(self):
        """Test validación de inóculo válido."""
        result = InputValidator.validate_inoculum(0.5)
        assert result == 0.5

    def test_validate_inoculum_too_low(self):
        """Test inóculo muy bajo."""
        with pytest.raises(ValueError, match="Inóculo"):
            InputValidator.validate_inoculum(0.2)

    def test_validate_inoculum_too_high(self):
        """Test inóculo muy alto."""
        with pytest.raises(ValueError, match="Inóculo"):
            InputValidator.validate_inoculum(0.8)

    def test_validate_temperature_valid(self):
        """Test validación de temperatura válida."""
        result = InputValidator.validate_temperature(37.0)
        assert result == 37.0

    def test_validate_temperature_too_low(self):
        """Test temperatura muy baja."""
        with pytest.raises(ValueError, match="Temperatura"):
            InputValidator.validate_temperature(34.0)

    def test_validate_temperature_too_high(self):
        """Test temperatura muy alta."""
        with pytest.raises(ValueError, match="Temperatura"):
            InputValidator.validate_temperature(38.0)

    def test_validate_bacteria_profile_id_valid(self):
        """Test validación de ID válido."""
        result = InputValidator.validate_bacteria_profile_id(42)
        assert result == 42

    def test_validate_bacteria_profile_id_string(self):
        """Test conversión desde string."""
        result = InputValidator.validate_bacteria_profile_id("123")
        assert result == 123

    def test_validate_bacteria_profile_id_none(self):
        """Test ID None."""
        with pytest.raises(ValueError, match="no puede ser None"):
            InputValidator.validate_bacteria_profile_id(None)

    def test_validate_bacteria_profile_id_negative(self):
        """Test ID negativo."""
        with pytest.raises(ValueError, match="debe ser positivo"):
            InputValidator.validate_bacteria_profile_id(-5)

    def test_validate_bacteria_profile_id_zero(self):
        """Test ID cero."""
        with pytest.raises(ValueError, match="debe ser positivo"):
            InputValidator.validate_bacteria_profile_id(0)

    def test_validate_bacteria_profile_id_invalid_string(self):
        """Test string no numérico."""
        with pytest.raises(ValueError, match="Debe ser un número entero"):
            InputValidator.validate_bacteria_profile_id("not_a_number")

    def test_sanitize_database_string_normal(self):
        """Test sanitización de string de BD normal."""
        result = InputValidator.sanitize_database_string("Panel Name")
        assert result == "Panel Name"

    def test_sanitize_database_string_control_chars(self):
        """Test eliminación de caracteres de control."""
        result = InputValidator.sanitize_database_string("Panel\x00\x01Name")
        assert result == "PanelName"

    def test_sanitize_database_string_long(self):
        """Test truncamiento de strings largos."""
        long_string = "A" * 1500
        result = InputValidator.sanitize_database_string(long_string)
        assert len(result) <= 1003  # 1000 + "..."

    def test_sanitize_database_string_non_string(self):
        """Test conversión de no-strings."""
        result = InputValidator.sanitize_database_string(123)
        assert result == "123"

    def test_validate_file_path_valid(self):
        """Test validación de ruta válida."""
        result = InputValidator.validate_file_path("export.csv", [".csv", ".xlsx"])
        assert result == "export.csv"

    def test_validate_file_path_traversal(self):
        """Test detección de path traversal."""
        with pytest.raises(ValueError, match="potencialmente insegura"):
            InputValidator.validate_file_path("../../../etc/passwd")

    def test_validate_file_path_invalid_extension(self):
        """Test extensión no permitida."""
        with pytest.raises(ValueError, match="Extensión de archivo no permitida"):
            InputValidator.validate_file_path("export.exe", [".csv", ".xlsx"])

    def test_validate_file_path_empty(self):
        """Test ruta vacía."""
        with pytest.raises(ValueError, match="no puede estar vacía"):
            InputValidator.validate_file_path("")


class TestSafeFormatErrorMessage:
    """Tests para safe_format_error_message."""

    def test_format_short_error(self):
        """Test formateo de error corto."""
        error = ValueError("Error simple")
        result = safe_format_error_message(error)
        assert "Error simple" in result

    def test_format_long_error(self):
        """Test truncamiento de error largo."""
        long_message = "A" * 300
        error = ValueError(long_message)
        result = safe_format_error_message(error)
        assert len(result) <= 203  # 200 + "..."

    def test_format_html_escape(self):
        """Test escape de HTML en error."""
        error = ValueError("<script>alert('xss')</script>")
        result = safe_format_error_message(error)
        assert "&lt;" in result
        assert "&gt;" in result
