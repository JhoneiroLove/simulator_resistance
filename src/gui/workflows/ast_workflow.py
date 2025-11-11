"""
AST Workflow - Flujo completo de pruebas de sensibilidad antimicrobiana

Integra:
- ASTPanelWidget: Configuración y ejecución de paneles AST
- ASTPlateViewer: Visualización de placa 96 pocillos
- ASTResultsTable: Tabla de resultados MIC con exportación

Autor: Sistema AST Simulator
Fecha: 11 de noviembre de 2025
"""

from typing import Optional

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QGroupBox,
    QLabel,
)
from PyQt5.QtCore import Qt

from src.gui.widgets.ast_panel_widget import ASTPanelWidget
from src.gui.widgets.ast_plate_viewer import ASTPlateViewer
from src.gui.widgets.ast_results_table import ASTResultsTable


class ASTWorkflow(QWidget):
    """
    Workflow completo para simulación AST.

    Layout:
    ┌─────────────────────────────────────────────────┐
    │  Panel de Control (ASTPanelWidget)              │
    │  [Panel ▼] [Inóculo] [Temp] [▶ Ejecutar]       │
    └─────────────────────────────────────────────────┘
    ┌────────────────────┬────────────────────────────┐
    │                    │                            │
    │  Placa 96 Pocillos │  Tabla de Resultados MIC   │
    │  (ASTPlateViewer)  │  (ASTResultsTable)         │
    │                    │                            │
    │  [Slider tiempo]   │  [Filtro] [CSV] [PDF]      │
    │                    │                            │
    └────────────────────┴────────────────────────────┘
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # === TÍTULO ===
        title_label = QLabel(" Simulador de Antibiograma (AST)")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        layout.addWidget(title_label)

        # === PANEL DE CONTROL ===
        control_group = QGroupBox("Configuración del Panel AST")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        control_layout = QVBoxLayout(control_group)

        self.panel_widget = ASTPanelWidget()
        control_layout.addWidget(self.panel_widget)

        layout.addWidget(control_group)

        # === VISUALIZACIÓN: SPLITTER HORIZONTAL ===
        splitter = QSplitter(Qt.Horizontal)

        # Grupo Placa
        plate_group = QGroupBox("Visualización de Placa (96 Pocillos)")
        plate_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #3498db;
            }
        """)
        plate_layout = QVBoxLayout(plate_group)

        self.plate_viewer = ASTPlateViewer()
        plate_layout.addWidget(self.plate_viewer)

        splitter.addWidget(plate_group)

        # Grupo Resultados
        results_group = QGroupBox("Resultados MIC e Interpretación")
        results_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #27ae60;
            }
        """)
        results_layout = QVBoxLayout(results_group)

        self.results_table = ASTResultsTable()
        results_layout.addWidget(self.results_table)

        splitter.addWidget(results_group)

        # Configurar tamaños iniciales del splitter (40% placa, 60% tabla)
        splitter.setSizes([400, 600])

        layout.addWidget(splitter, stretch=1)

    def _connect_signals(self):
        """Conecta las señales entre widgets."""
        # Cuando se completa la simulación AST
        self.panel_widget.ast_completed.connect(self._on_ast_completed)

        # Cuando falla la simulación AST
        self.panel_widget.ast_failed.connect(self._on_ast_failed)

        # Cuando se hace clic en un pocillo de la placa
        self.plate_viewer.well_clicked.connect(self._on_well_clicked)

        # Cuando se selecciona un antibiótico en la tabla
        self.results_table.antibiotic_selected.connect(self._on_antibiotic_selected)

    def _on_ast_completed(self, results: dict):
        """
        Maneja la finalización exitosa de la simulación AST.

        Args:
            results: Diccionario con resultados de la simulación
                - well_data_list: Lista de datos de pocillos
                - mic_results: Lista de resultados MIC
                - qc_report: Reporte de control de calidad
        """
        # Cargar datos en el visor de placa
        well_data_list = results.get("well_data_list", [])
        self.plate_viewer.load_well_data(well_data_list)

        # Cargar resultados MIC en la tabla
        mic_results = results.get("mic_results", [])
        self.results_table.load_results(mic_results)

        # Mostrar mensaje de éxito en status bar (si existe)
        total_wells = len(well_data_list)
        total_antibiotics = len(mic_results)
        status_msg = (
            f" AST completado: {total_wells} pocillos, {total_antibiotics} antibióticos"
        )

        # Intentar mostrar en status bar del parent (MainWindow)
        main_window = self.window()
        if hasattr(main_window, "statusBar"):
            main_window.statusBar().showMessage(status_msg, 5000)

    def _on_ast_failed(self, error_message: str):
        """
        Maneja el fallo de la simulación AST.

        Args:
            error_message: Mensaje de error descriptivo
        """
        # Mostrar mensaje de error en status bar
        status_msg = f" Error en AST: {error_message}"

        main_window = self.window()
        if hasattr(main_window, "statusBar"):
            main_window.statusBar().showMessage(status_msg, 10000)

    def _on_well_clicked(self, well_id: str, well_data: dict):
        """
        Maneja el clic en un pocillo de la placa.

        Args:
            well_id: ID del pocillo (ej: 'A1', 'H12')
            well_data: Datos completos del pocillo
        """
        # Por ahora solo mostramos en status bar
        # En futuro podría abrir un diálogo con curva de crecimiento
        antibiotico = well_data.get("antibiotico", "Control")
        concentracion = well_data.get("concentracion", 0)
        od_final = well_data.get("od_final", 0)

        status_msg = f" Pocillo {well_id}: {antibiotico} ({concentracion:.2f} µg/mL) - OD: {od_final:.3f}"

        main_window = self.window()
        if hasattr(main_window, "statusBar"):
            main_window.statusBar().showMessage(status_msg, 3000)

    def _on_antibiotic_selected(self, antibiotico: str, data: dict):
        """
        Maneja la selección de un antibiótico en la tabla de resultados.

        Args:
            antibiotico: Nombre del antibiótico seleccionado
            data: Datos completos del antibiótico
        """
        # Mostrar información en status bar
        mic = data.get("mic_value", 0)
        interpretacion = data.get("interpretacion", "N/A")

        status_msg = (
            f" {antibiotico}: MIC = {mic:.2f} µg/mL, Interpretación: {interpretacion}"
        )

        main_window = self.window()
        if hasattr(main_window, "statusBar"):
            main_window.statusBar().showMessage(status_msg, 3000)

    def clear_all(self):
        """Limpia todos los widgets y reinicia el workflow."""
        self.plate_viewer.clear()
        self.results_table.clear()

        # Resetear panel widget (si tiene método reset)
        if hasattr(self.panel_widget, "reset"):
            self.panel_widget.reset()
