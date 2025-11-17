"""
Workflow Event Handlers - Manejadores de eventos del workflow AST

Responsabilidad única: Procesar eventos y coordinar respuestas entre componentes.
Principio Dependency Inversion: Depende de abstracciones, no de implementaciones.

Autor: Sistema AST Simulator
Fecha: 17 de noviembre de 2025
"""

from typing import Dict, Callable, Optional
from PyQt5.QtWidgets import QWidget


class WorkflowEventHandler:
    """
    Maneja eventos del workflow AST y coordina respuestas.

    Responsabilidades:
    - Procesar eventos de widgets
    - Coordinar actualizaciones entre componentes
    - Notificar a observadores (status bar, etc.)

    Principio: Single Responsibility + Observer Pattern
    """

    def __init__(self, parent_widget: QWidget):
        """
        Inicializa el manejador de eventos.

        Args:
            parent_widget: Widget padre (para acceder a window/statusBar)
        """
        self.parent_widget = parent_widget
        self.observers: Dict[str, list[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        """
        Suscribe un callback a un evento específico.

        Args:
            event_name: Nombre del evento
            callback: Función a llamar cuando ocurra el evento
        """
        if event_name not in self.observers:
            self.observers[event_name] = []
        self.observers[event_name].append(callback)

    def notify(self, event_name: str, **kwargs):
        """
        Notifica a todos los observadores de un evento.

        Args:
            event_name: Nombre del evento
            **kwargs: Datos del evento
        """
        if event_name in self.observers:
            for callback in self.observers[event_name]:
                callback(**kwargs)

    def show_status_message(self, message: str, timeout: int = 5000):
        """
        Muestra un mensaje en la barra de estado.

        Args:
            message: Mensaje a mostrar
            timeout: Tiempo en milisegundos antes de limpiar
        """
        main_window = self.parent_widget.window()
        if hasattr(main_window, "statusBar"):
            main_window.statusBar().showMessage(message, timeout)

    def handle_identification_completed(
        self, organism: str, sample_origin: str, confidence: float
    ):
        """
        Maneja la finalización de identificación bacteriana.

        Args:
            organism: Organismo identificado
            sample_origin: Origen de la muestra
            confidence: Nivel de confianza (0.0-1.0)
        """
        # Notificar a observadores
        self.notify(
            "identification_completed",
            organism=organism,
            origin=sample_origin,
            confidence=confidence,
        )

        # Mostrar mensaje
        self.show_status_message(
            f"✓ Identificación completada: {organism} ({confidence * 100:.1f}% confianza) - "
            f"Muestra: {sample_origin} - Puede pasar al Paso 1",
            8000,
        )

    def handle_profile_generated(self, bacteria_profile_id: int, genotype: dict):
        """
        Maneja la generación de perfil bacteriano.

        Args:
            bacteria_profile_id: ID del perfil en BD
            genotype: Diccionario gen → estado
        """
        # Contar mutaciones
        mutations_count = len(
            [
                g
                for g in genotype.values()
                if g not in ["wild-type", "functional", "basal", "absent"]
            ]
        )

        # Notificar a observadores
        self.notify(
            "profile_generated",
            profile_id=bacteria_profile_id,
            genotype=genotype,
            mutations=mutations_count,
        )

        # Mostrar mensaje
        self.show_status_message(
            f"✓ Perfil bacteriano cargado (ID: {bacteria_profile_id}, "
            f"{mutations_count} mutaciones) - Puede pasar al Paso 2",
            8000,
        )

    def handle_ast_completed(self, results: dict):
        """
        Maneja la finalización de simulación AST.

        Args:
            results: Diccionario con resultados (well_data_list, mic_results, etc.)
        """
        total_wells = len(results.get("well_data_list", []))
        total_antibiotics = len(results.get("mic_results", []))

        # Notificar a observadores
        self.notify(
            "ast_completed",
            results=results,
            wells=total_wells,
            antibiotics=total_antibiotics,
        )

        # Mostrar mensaje
        self.show_status_message(
            f"✅ AST completado: {total_wells} pocillos, {total_antibiotics} antibióticos",
            5000,
        )

    def handle_ast_failed(self, error_message: str):
        """
        Maneja el fallo de simulación AST.

        Args:
            error_message: Descripción del error
        """
        # Notificar a observadores
        self.notify("ast_failed", error=error_message)

        # Mostrar mensaje
        self.show_status_message(f"❌ Error en AST: {error_message}", 10000)
