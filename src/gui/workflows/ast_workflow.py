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
    QHBoxLayout,
    QSplitter,
    QGroupBox,
    QLabel,
    QTabWidget,
    QPushButton,
)
from PyQt5.QtCore import Qt

from src.gui.widgets.ast_panel_widget import ASTPanelWidget
from src.gui.widgets.ast_plate_viewer import ASTPlateViewer
from src.gui.widgets.ast_results_table import ASTResultsTable
from src.gui.widgets.growth_curve_widget import GrowthCurveWidget
from src.gui.widgets.bacteria_profile_widget import BacteriaProfileWidget


class ASTWorkflow(QWidget):
    """
    Workflow completo para simulación AST con flujo guiado por pestañas.

    Sistema de 5 pestañas secuenciales:

    ┌──────────────────────────────────────────────────────────────────┐
    │  🧬 Simulador de Antibiograma (AST)                             │
    ├──────────────────────────────────────────────────────────────────┤
    │ [1️⃣ Perfil] [2️⃣ Configurar] [3️⃣ Placa] [4️⃣ Resultados] [5️⃣ Curvas] │
    ├──────────────────────────────────────────────────────────────────┤
    │                                                                  │
    │  PASO 1: Perfil Bacteriano                                      │
    │  ┌────────────────────────────────────────────────────────────┐ │
    │  │ 📋 Genere un perfil bacteriano para comenzar              │ │
    │  │                                                            │ │
    │  │ 🦠 Perfil Bacteriano                                       │ │
    │  │   ○ Wild-type (sensible)                                  │ │
    │  │   ○ Resistente (seleccione antibióticos previos)          │ │
    │  │                                                            │ │
    │  │   [Antibióticos previos: Lista multiselección]            │ │
    │  │   [⚡ Generar Perfil]                                      │ │
    │  │                                                            │ │
    │  │   [Resumen del genotipo y MICs calculados]                │ │
    │  │                                                            │ │
    │  │                             [Siguiente: Configurar AST ➔] │ │
    │  └────────────────────────────────────────────────────────────┘ │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘

    Flujo de trabajo guiado:

    1️⃣ PERFIL BACTERIANO (Obligatorio)
       - Generar wild-type o resistente
       - Habilita Tab 2 al completar

    2️⃣ CONFIGURAR AST (Obligatorio)
       - Seleccionar panel
       - Ajustar parámetros (inóculo, temperatura)
       - Ejecutar simulación
       - Habilita Tabs 3, 4, 5 al completar

    3️⃣ PLACA AST (Visualización)
       - Placa 96 pocillos interactiva
       - Slider temporal (0-18h)
       - Colores por densidad óptica

    4️⃣ RESULTADOS MIC (Análisis)
       - Tabla con interpretación S/I/R
       - Breakpoints EUCAST/CLSI
       - Exportar CSV/PDF

    5️⃣ CURVAS DE CRECIMIENTO (Análisis avanzado)
       - Gráficos OD vs Tiempo
       - Por antibiótico y concentración
       - Marcador de MIC
       - Botón "Nueva Simulación" para reiniciar

    Ventajas del flujo guiado:
    - ✅ Navegación intuitiva paso a paso
    - ✅ Tabs bloqueados hasta completar pasos previos
    - ✅ Botones de navegación "Siguiente" y "Volver"
    - ✅ Instrucciones visuales en cada paso
    - ✅ Máximo espacio para cada componente
    - ✅ Flujo unidireccional con opción de reinicio
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # === TÍTULO ===
        title_label = QLabel("🧬 Simulador de Antibiograma (AST)")
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
        main_layout.addWidget(title_label)

        # === SISTEMA DE PESTAÑAS PRINCIPAL ===
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #3498db;
                border-radius: 5px;
                background-color: white;
                padding: 5px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 12px 24px;
                margin-right: 3px;
                border: 2px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #3498db;
                border-color: #3498db;
                margin-bottom: -2px;
            }
            QTabBar::tab:hover {
                background-color: #d5dbdb;
            }
            QTabBar::tab:disabled {
                color: #95a5a6;
                background-color: #f8f9fa;
            }
        """)

        # === TAB 1: Generar Perfil Bacteriano ===
        profile_tab = QWidget()
        profile_layout = QVBoxLayout(profile_tab)
        profile_layout.setContentsMargins(15, 15, 15, 15)
        profile_layout.setSpacing(15)

        # Instrucciones
        instructions_label = QLabel(
            "📋 <b>PASO 1:</b> Genere un perfil bacteriano para comenzar la simulación AST"
        )
        instructions_label.setStyleSheet("""
            QLabel {
                background-color: #e8f4f8;
                color: #2c3e50;
                padding: 12px;
                border-left: 5px solid #3498db;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        profile_layout.addWidget(instructions_label)

        self.profile_widget = BacteriaProfileWidget()
        profile_layout.addWidget(self.profile_widget)

        # Botón siguiente
        next_config_btn = QPushButton("Siguiente: Configurar AST ➔")
        next_config_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        next_config_btn.setEnabled(False)
        next_config_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(1))
        profile_layout.addWidget(next_config_btn)

        self.main_tabs.addTab(profile_tab, "1️⃣ Perfil Bacteriano")

        # Guardar referencia al botón
        self.next_config_btn = next_config_btn

        # === TAB 2: Configurar AST ===
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        config_layout.setContentsMargins(15, 15, 15, 15)
        config_layout.setSpacing(15)

        # Instrucciones
        config_instructions = QLabel(
            "⚙️ <b>PASO 2:</b> Configure los parámetros del panel AST y ejecute la simulación"
        )
        config_instructions.setStyleSheet("""
            QLabel {
                background-color: #fef5e7;
                color: #2c3e50;
                padding: 12px;
                border-left: 5px solid #f39c12;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        config_layout.addWidget(config_instructions)

        self.panel_widget = ASTPanelWidget()
        config_layout.addWidget(self.panel_widget)

        # Botones navegación
        nav_layout = QHBoxLayout()

        back_profile_btn = QPushButton("◀ Volver: Perfil")
        back_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-size: 12px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        back_profile_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(0))
        nav_layout.addWidget(back_profile_btn)

        nav_layout.addStretch()

        next_plate_btn = QPushButton("Siguiente: Ver Placa ➔")
        next_plate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        next_plate_btn.setEnabled(False)
        next_plate_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(2))
        nav_layout.addWidget(next_plate_btn)

        config_layout.addLayout(nav_layout)

        self.main_tabs.addTab(config_tab, "2️⃣ Configurar AST")

        # Guardar referencia
        self.next_plate_btn = next_plate_btn

        # === TAB 3: Visualizar Placa ===
        plate_tab = QWidget()
        plate_layout = QVBoxLayout(plate_tab)
        plate_layout.setContentsMargins(15, 15, 15, 15)
        plate_layout.setSpacing(10)

        # Instrucciones
        plate_instructions = QLabel(
            "🔬 <b>PASO 3:</b> Visualice la placa de 96 pocillos y el crecimiento bacteriano"
        )
        plate_instructions.setStyleSheet("""
            QLabel {
                background-color: #eaf2f8;
                color: #2c3e50;
                padding: 12px;
                border-left: 5px solid #5dade2;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        plate_layout.addWidget(plate_instructions)

        self.plate_viewer = ASTPlateViewer()
        plate_layout.addWidget(self.plate_viewer, stretch=1)

        # Botones navegación
        plate_nav_layout = QHBoxLayout()

        back_config_btn = QPushButton("◀ Volver: Configuración")
        back_config_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-size: 12px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        back_config_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(1))
        plate_nav_layout.addWidget(back_config_btn)

        plate_nav_layout.addStretch()

        next_results_btn = QPushButton("Siguiente: Ver Resultados ➔")
        next_results_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        next_results_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(3))
        plate_nav_layout.addWidget(next_results_btn)

        plate_layout.addLayout(plate_nav_layout)

        self.main_tabs.addTab(plate_tab, "3️⃣ Placa AST")

        # === TAB 4: Resultados MIC ===
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        results_layout.setContentsMargins(15, 15, 15, 15)
        results_layout.setSpacing(10)

        # Instrucciones
        results_instructions = QLabel(
            "📊 <b>PASO 4:</b> Analice los resultados MIC con interpretación clínica"
        )
        results_instructions.setStyleSheet("""
            QLabel {
                background-color: #eafaf1;
                color: #2c3e50;
                padding: 12px;
                border-left: 5px solid #27ae60;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        results_layout.addWidget(results_instructions)

        self.results_table = ASTResultsTable()
        results_layout.addWidget(self.results_table, stretch=1)

        # Botones navegación
        results_nav_layout = QHBoxLayout()

        back_plate_btn = QPushButton("◀ Volver: Placa")
        back_plate_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-size: 12px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        back_plate_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(2))
        results_nav_layout.addWidget(back_plate_btn)

        results_nav_layout.addStretch()

        next_curves_btn = QPushButton("Siguiente: Ver Curvas ➔")
        next_curves_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        next_curves_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(4))
        results_nav_layout.addWidget(next_curves_btn)

        results_layout.addLayout(results_nav_layout)

        self.main_tabs.addTab(results_tab, "4️⃣ Resultados MIC")

        # === TAB 5: Curvas de Crecimiento ===
        curves_tab = QWidget()
        curves_layout = QVBoxLayout(curves_tab)
        curves_layout.setContentsMargins(15, 15, 15, 15)
        curves_layout.setSpacing(10)

        # Instrucciones
        curves_instructions = QLabel(
            "📈 <b>PASO 5:</b> Explore las curvas de crecimiento por antibiótico y concentración"
        )
        curves_instructions.setStyleSheet("""
            QLabel {
                background-color: #f4ecf7;
                color: #2c3e50;
                padding: 12px;
                border-left: 5px solid #9b59b6;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        curves_layout.addWidget(curves_instructions)

        self.growth_curve_widget = GrowthCurveWidget()
        curves_layout.addWidget(self.growth_curve_widget, stretch=1)

        # Botones navegación
        curves_nav_layout = QHBoxLayout()

        back_results_btn = QPushButton("◀ Volver: Resultados")
        back_results_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-size: 12px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        back_results_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(3))
        curves_nav_layout.addWidget(back_results_btn)

        curves_nav_layout.addStretch()

        restart_btn = QPushButton("🔄 Nueva Simulación")
        restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        restart_btn.clicked.connect(self._restart_workflow)
        curves_nav_layout.addWidget(restart_btn)

        curves_layout.addLayout(curves_nav_layout)

        self.main_tabs.addTab(curves_tab, "5️⃣ Curvas de Crecimiento")

        # Agregar tabs al layout principal
        main_layout.addWidget(self.main_tabs, stretch=1)

        # Deshabilitar tabs hasta que se complete el flujo
        self.main_tabs.setTabEnabled(1, False)  # Configurar AST
        self.main_tabs.setTabEnabled(2, False)  # Placa
        self.main_tabs.setTabEnabled(3, False)  # Resultados
        self.main_tabs.setTabEnabled(4, False)  # Curvas

    def _connect_signals(self):
        """Conecta las señales entre widgets."""
        # Cuando se genera un perfil bacteriano
        self.profile_widget.profile_generated.connect(self._on_profile_generated)

        # Cuando se completa la simulación AST
        self.panel_widget.ast_completed.connect(self._on_ast_completed)

        # Cuando falla la simulación AST
        self.panel_widget.ast_failed.connect(self._on_ast_failed)

        # Cuando se hace clic en un pocillo de la placa
        self.plate_viewer.well_clicked.connect(self._on_well_clicked)

        # Cuando se selecciona un antibiótico en la tabla
        self.results_table.antibiotic_selected.connect(self._on_antibiotic_selected)

    def _on_profile_generated(self, bacteria_profile_id: int, genotype: dict):
        """
        Maneja la generación exitosa de un perfil bacteriano.

        Args:
            bacteria_profile_id: ID del perfil en la base de datos
            genotype: Diccionario gen → estado
        """
        # Establecer el perfil en el panel AST
        self.panel_widget.set_bacteria_profile(bacteria_profile_id)

        # Habilitar siguiente tab y botón
        self.main_tabs.setTabEnabled(1, True)
        self.next_config_btn.setEnabled(True)

        # Actualizar status bar
        main_window = self.window()
        if hasattr(main_window, "statusBar"):
            mutations_count = len(
                [
                    g
                    for g in genotype.values()
                    if g not in ["wild-type", "functional", "basal", "absent"]
                ]
            )
            main_window.statusBar().showMessage(
                f"✓ Perfil bacteriano cargado (ID: {bacteria_profile_id}, {mutations_count} mutaciones) - Puede pasar al Paso 2",
                8000,
            )

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

        # Habilitar todos los tabs de visualización
        self.main_tabs.setTabEnabled(2, True)  # Placa
        self.main_tabs.setTabEnabled(3, True)  # Resultados
        self.main_tabs.setTabEnabled(4, True)  # Curvas
        self.next_plate_btn.setEnabled(True)

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

    def _restart_workflow(self):
        """Reinicia el flujo de trabajo completo."""
        from PyQt5.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Reiniciar simulación",
            "¿Está seguro que desea reiniciar?\n\nSe perderán todos los datos actuales.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Limpiar todos los widgets
            self.clear_all()

            # Volver al primer tab
            self.main_tabs.setCurrentIndex(0)

            # Deshabilitar tabs excepto el primero
            self.main_tabs.setTabEnabled(1, False)
            self.main_tabs.setTabEnabled(2, False)
            self.main_tabs.setTabEnabled(3, False)
            self.main_tabs.setTabEnabled(4, False)

            # Deshabilitar botones siguiente
            self.next_config_btn.setEnabled(False)
            self.next_plate_btn.setEnabled(False)

            # Mensaje status bar
            main_window = self.window()
            if hasattr(main_window, "statusBar"):
                main_window.statusBar().showMessage(
                    "🔄 Simulación reiniciada - Comience desde el Paso 1", 5000
                )

    def clear_all(self):
        """Limpia todos los widgets y reinicia el workflow."""
        self.plate_viewer.clear()
        self.results_table.clear()
        self.growth_curve_widget.clear()

        # Resetear panel widget (si tiene método reset)
        if hasattr(self.panel_widget, "reset"):
            self.panel_widget.reset()
