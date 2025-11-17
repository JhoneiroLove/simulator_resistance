"""
Tab Navigation Controller - Gestión de navegación entre pestañas

Responsabilidad única: Controlar la habilitación y navegación entre tabs.
Principio Open/Closed: Extensible para nuevos tabs sin modificar código existente.

Autor: Sistema AST Simulator
Fecha: 17 de noviembre de 2025
"""

from typing import Dict, List, Optional
from PyQt5.QtWidgets import QTabWidget, QPushButton


class TabNavigationController:
    """
    Controla la navegación secuencial entre tabs del workflow AST.

    Responsabilidades:
    - Habilitar/deshabilitar tabs según flujo
    - Gestionar estado de botones de navegación
    - Validar transiciones entre tabs

    Principio: Single Responsibility (gestión de navegación solamente)
    """

    def __init__(self, tab_widget: QTabWidget):
        """
        Inicializa el controlador de navegación.

        Args:
            tab_widget: Widget de pestañas a controlar
        """
        self.tab_widget = tab_widget
        self.navigation_buttons: Dict[str, QPushButton] = {}
        self.tab_count = tab_widget.count()

    def register_button(self, button_name: str, button: QPushButton):
        """
        Registra un botón de navegación para ser controlado.

        Args:
            button_name: Identificador único del botón
            button: Instancia del botón
        """
        self.navigation_buttons[button_name] = button

    def enable_tab(self, tab_index: int, enable_buttons: Optional[List[str]] = None):
        """
        Habilita un tab y opcionalmente sus botones de navegación asociados.

        Args:
            tab_index: Índice del tab a habilitar (0-based)
            enable_buttons: Lista de nombres de botones a habilitar
        """
        if 0 <= tab_index < self.tab_count:
            self.tab_widget.setTabEnabled(tab_index, True)

            if enable_buttons:
                for btn_name in enable_buttons:
                    if btn_name in self.navigation_buttons:
                        self.navigation_buttons[btn_name].setEnabled(True)

    def disable_tab(self, tab_index: int):
        """
        Deshabilita un tab.

        Args:
            tab_index: Índice del tab a deshabilitar
        """
        if 0 <= tab_index < self.tab_count:
            self.tab_widget.setTabEnabled(tab_index, False)

    def navigate_to_tab(self, tab_index: int) -> bool:
        """
        Navega a un tab específico si está habilitado.

        Args:
            tab_index: Índice del tab destino

        Returns:
            True si la navegación fue exitosa, False si el tab está deshabilitado
        """
        if self.tab_widget.isTabEnabled(tab_index):
            self.tab_widget.setCurrentIndex(tab_index)
            return True
        return False

    def reset_navigation(self):
        """
        Reinicia la navegación al estado inicial.

        Deshabilita todos los tabs excepto el primero (índice 0).
        Deshabilita todos los botones de navegación.
        Vuelve al primer tab.
        """
        # Deshabilitar todos excepto el primero
        for i in range(1, self.tab_count):
            self.disable_tab(i)

        # Deshabilitar todos los botones
        for button in self.navigation_buttons.values():
            button.setEnabled(False)

        # Volver al inicio
        self.navigate_to_tab(0)

    def enable_workflow_step(self, step_name: str):
        """
        Habilita un paso completo del workflow (tab + botones asociados).

        Args:
            step_name: Nombre del paso del workflow
        """
        step_config = {
            "identification": {"tab": 1, "buttons": ["next_profile"]},
            "profile": {"tab": 2, "buttons": ["next_config"]},
            "ast_config": {"tab": 3, "buttons": ["next_plate"]},
            "visualization": {"tabs": [3, 4, 5], "buttons": ["next_plate"]},
        }

        if step_name in step_config:
            config = step_config[step_name]

            # Habilitar tab(s)
            if "tab" in config:
                self.enable_tab(config["tab"], config.get("buttons"))
            elif "tabs" in config:
                for tab_idx in config["tabs"]:
                    self.enable_tab(tab_idx)
                # Habilitar botones
                for btn_name in config.get("buttons", []):
                    if btn_name in self.navigation_buttons:
                        self.navigation_buttons[btn_name].setEnabled(True)
