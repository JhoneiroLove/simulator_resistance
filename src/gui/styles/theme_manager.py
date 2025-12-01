"""
Theme Manager - Gestión de estilos adaptables multiplataforma

Proporciona estilos que se adaptan al tema del sistema operativo (claro/oscuro)
y son compatibles con Windows, Linux y macOS.

RNF-8: Portabilidad
Autor: Sistema AST Simulator
Fecha: 30 de noviembre de 2025
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import sys


class ThemeManager:
    """Gestor de temas multiplataforma que se adapta al SO."""

    def __init__(self):
        self.app = QApplication.instance()
        self.is_dark_theme = self._detect_dark_theme()

    def _detect_dark_theme(self) -> bool:
        """Detecta si el sistema usa tema oscuro."""
        if self.app is None:
            return False

        palette = self.app.palette()
        bg_color = palette.color(QPalette.Window)

        # Si el fondo es oscuro (luminosidad < 128), es tema oscuro
        return bg_color.lightness() < 128

    def get_colors(self) -> dict:
        """Obtiene la paleta de colores adaptada al tema del sistema."""
        if self.is_dark_theme:
            return {
                # Tema oscuro
                "primary": "#3498db",
                "primary_dark": "#2980b9",
                "primary_light": "#5dade2",
                "success": "#27ae60",
                "success_dark": "#229954",
                "warning": "#f39c12",
                "danger": "#e74c3c",
                "text": "#ecf0f1",
                "text_secondary": "#bdc3c7",
                "text_muted": "#95a5a6",
                "bg_primary": "#2c3e50",
                "bg_secondary": "#34495e",
                "bg_tertiary": "#1a252f",
                "border": "#4a5f7f",
                "border_focus": "#5dade2",
            }
        else:
            return {
                # Tema claro (actual)
                "primary": "#3498db",
                "primary_dark": "#2980b9",
                "primary_light": "#85c1e9",
                "success": "#27ae60",
                "success_dark": "#229954",
                "warning": "#f39c12",
                "danger": "#e74c3c",
                "text": "#2c3e50",
                "text_secondary": "#7f8c8d",
                "text_muted": "#95a5a6",
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa",
                "bg_tertiary": "#ecf0f1",
                "border": "#bdc3c7",
                "border_focus": "#3498db",
            }

    def get_combo_style(self) -> str:
        """Estilo para QComboBox adaptable."""
        colors = self.get_colors()
        return f"""
            QComboBox {{
                padding: 8px;
                border: 2px solid {colors["border"]};
                border-radius: 5px;
                font-size: 13px;
                background-color: {colors["bg_primary"]};
                color: {colors["text"]};
            }}
            QComboBox:focus {{
                border-color: {colors["border_focus"]};
                border-width: 3px;
            }}
            QComboBox:disabled {{
                background-color: {colors["bg_tertiary"]};
                color: {colors["text_muted"]};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {colors["bg_primary"]};
                color: {colors["text"]};
                selection-background-color: {colors["primary_light"]};
                border: 1px solid {colors["border"]};
            }}
        """

    def get_spinbox_style(self) -> str:
        """Estilo para QDoubleSpinBox/QSpinBox adaptable."""
        colors = self.get_colors()
        return f"""
            QDoubleSpinBox, QSpinBox {{
                padding: 8px;
                border: 2px solid {colors["border"]};
                border-radius: 5px;
                font-size: 13px;
                background-color: {colors["bg_primary"]};
                color: {colors["text"]};
            }}
            QDoubleSpinBox:focus, QSpinBox:focus {{
                border-color: {colors["border_focus"]};
                border-width: 3px;
            }}
            QDoubleSpinBox:disabled, QSpinBox:disabled {{
                background-color: {colors["bg_tertiary"]};
                color: {colors["text_muted"]};
            }}
        """

    def get_button_style(self, button_type: str = "primary") -> str:
        """
        Estilo para QPushButton adaptable.

        Args:
            button_type: 'primary', 'success', 'secondary', 'danger'
        """
        colors = self.get_colors()

        if button_type == "success":
            bg = colors["success"]
            bg_hover = colors["success_dark"]
            border_focus = "#1e8449"
        elif button_type == "secondary":
            bg = colors["text_muted"]
            bg_hover = colors["text_secondary"]
            border_focus = colors["border"]
        elif button_type == "danger":
            bg = colors["danger"]
            bg_hover = "#c0392b"
            border_focus = "#a93226"
        else:  # primary
            bg = colors["primary"]
            bg_hover = colors["primary_dark"]
            border_focus = colors["primary_light"]

        return f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
            }}
            QPushButton:disabled {{
                background-color: {colors["text_muted"]};
            }}
            QPushButton:focus {{
                border: 3px solid {border_focus};
            }}
        """

    def get_progress_bar_style(self) -> str:
        """Estilo para QProgressBar adaptable."""
        colors = self.get_colors()
        return f"""
            QProgressBar {{
                border: 2px solid {colors["success"]};
                border-radius: 5px;
                text-align: center;
                background-color: {colors["bg_secondary"]};
                font-weight: bold;
                color: {colors["text"]};
            }}
            QProgressBar::chunk {{
                background-color: {colors["success"]};
                border-radius: 3px;
            }}
        """

    def get_groupbox_style(self) -> str:
        """Estilo para QGroupBox adaptable."""
        colors = self.get_colors()
        return f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {colors["primary"]};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: {colors["bg_primary"]};
                color: {colors["text"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {colors["primary"]};
            }}
        """

    def get_label_style(self, style_type: str = "normal") -> str:
        """
        Estilo para QLabel adaptable.

        Args:
            style_type: 'normal', 'muted', 'bold', 'info', 'warning'
        """
        colors = self.get_colors()

        if style_type == "muted":
            return f"color: {colors['text_muted']};"
        elif style_type == "bold":
            return f"color: {colors['text']}; font-weight: bold;"
        elif style_type == "info":
            return f"""
                background-color: {colors["bg_tertiary"]};
                color: {colors["text"]};
                padding: 5px;
                border-radius: 3px;
            """
        elif style_type == "warning":
            return f"""
                background-color: #fef5e7;
                color: #7d6608;
                padding: 14px 16px;
                border-left: 5px solid {colors["warning"]};
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            """
        else:
            return f"color: {colors['text']};"

    def apply_to_app(self):
        """Aplica estilos globales a la aplicación para mejor portabilidad."""
        if self.app is None:
            return

        # Configurar fuente base según plataforma
        font = self.app.font()

        if sys.platform == "darwin":  # macOS
            font.setFamily("SF Pro Text")
            font.setPointSize(13)
        elif sys.platform == "win32":  # Windows
            font.setFamily("Segoe UI")
            font.setPointSize(9)
        else:  # Linux
            font.setFamily("Ubuntu")
            font.setPointSize(10)

        self.app.setFont(font)


# Instancia global
_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """Obtiene la instancia global del theme manager."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
