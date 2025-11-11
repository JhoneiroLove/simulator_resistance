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
from src.gui.widgets.growth_curve_widget import GrowthCurveWidget


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
    ┌─────────────────────────────────────────────────┐
    │  Curvas de Crecimiento (GrowthCurveWidget)      │
    │  [Antibiótico ▼]  OD vs Tiempo  [🗑️ Limpiar]   │
    │                                                 │
    │  [Gráfico pyqtgraph con múltiples curvas]       │
    │                                                 │
    └─────────────────────────────────────────────────┘
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

        # === CURVAS DE CRECIMIENTO (Nuevo panel inferior) ===
        curves_group = QGroupBox(" Curvas de Crecimiento Bacteriano")
        curves_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #9b59b6;
            }
        """)
        curves_layout = QVBoxLayout(curves_group)

        self.growth_curve_widget = GrowthCurveWidget()
        curves_layout.addWidget(self.growth_curve_widget)

        layout.addWidget(curves_group, stretch=1)

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

        # Generar y cargar curvas de crecimiento
        growth_data = self._generate_growth_curves_from_wells(
            well_data_list, mic_results
        )
        if growth_data:
            self.growth_curve_widget.load_growth_data(growth_data)

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

    def _generate_growth_curves_from_wells(
        self, well_data_list: list, mic_results: list
    ) -> dict:
        """
        Genera datos de curvas de crecimiento a partir de los datos de pocillos.

        Args:
            well_data_list: Lista de datos de pocillos del AST
            mic_results: Lista de resultados MIC

        Returns:
            Diccionario con estructura para GrowthCurveWidget:
            {
                'antibiotico1': [
                    {
                        'concentracion': float,
                        'tiempos': List[int],
                        'ods': List[float],
                        'mic': bool
                    },
                    ...
                ],
                ...
            }
        """
        # Agrupar pocillos por antibiótico
        antibiotics_data = {}

        for well in well_data_list:
            antibiotico = well.get("antibiotico")
            if not antibiotico or antibiotico == "Control Negativo":
                continue

            concentracion = well.get("concentracion", 0)
            growth_curve = well.get("growth_curve", [])

            if antibiotico not in antibiotics_data:
                antibiotics_data[antibiotico] = {}

            # Guardar curva por concentración
            antibiotics_data[antibiotico][concentracion] = growth_curve

        # Crear MIC lookup
        mic_lookup = {}
        for mic_result in mic_results:
            antibiotico = mic_result.get("antibiotico")
            mic_value = mic_result.get("mic_value", 0)
            mic_lookup[antibiotico] = mic_value

        # Formatear datos para el widget
        growth_data = {}

        for antibiotico, concentrations in antibiotics_data.items():
            curves_list = []
            mic_value = mic_lookup.get(antibiotico, 0)

            # Ordenar concentraciones
            sorted_concs = sorted(concentrations.keys())

            for conc in sorted_concs:
                curve = concentrations[conc]

                # Extraer tiempos y ODs
                if isinstance(curve, list) and len(curve) > 0:
                    if isinstance(curve[0], dict):
                        # Formato: [{'time': 0, 'od': 0.1}, ...]
                        tiempos = [
                            point.get("time", idx) for idx, point in enumerate(curve)
                        ]
                        ods = [point.get("od", 0.1) for point in curve]
                    else:
                        # Formato: [0.1, 0.15, 0.2, ...]
                        tiempos = list(range(len(curve)))
                        ods = curve
                else:
                    # Sin datos, generar curva plana
                    tiempos = list(range(19))
                    ods = [0.1] * 19

                # Determinar si esta concentración es el MIC
                is_mic = abs(conc - mic_value) < 0.01  # Tolerancia pequeña

                curves_list.append(
                    {
                        "concentracion": conc,
                        "tiempos": tiempos,
                        "ods": ods,
                        "mic": is_mic,
                    }
                )

            growth_data[antibiotico] = curves_list

        return growth_data

    def clear_all(self):
        """Limpia todos los widgets y reinicia el workflow."""
        self.plate_viewer.clear()
        self.results_table.clear()
        self.growth_curve_widget.clear()

        # Resetear panel widget (si tiene método reset)
        if hasattr(self.panel_widget, "reset"):
            self.panel_widget.reset()
