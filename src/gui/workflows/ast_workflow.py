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
from src.gui.widgets.bacteria_identification_widget import BacteriaIdentificationWidget

# Controladores SOLID
from src.gui.workflows.tab_navigation_controller import TabNavigationController
from src.gui.workflows.workflow_event_handler import WorkflowEventHandler
from src.gui.workflows.workflow_data_manager import WorkflowDataManager


class ASTWorkflow(QWidget):
    """
    Workflow completo para simulación AST con flujo guiado por pestañas.

    Sistema de 6 pestañas secuenciales:

    ┌──────────────────────────────────────────────────────────────────┐
    │  🧬 Simulador de Antibiograma (AST)                             │
    ├──────────────────────────────────────────────────────────────────┤
    │ [0️⃣ ID] [1️⃣ Perfil] [2️⃣ Configurar] [3️⃣ Placa] [4️⃣ Resultados] [5️⃣ Curvas] │
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

    0️⃣ IDENTIFICACIÓN BACTERIANA (Obligatorio - NUEVO)
       - Seleccionar origen de muestra clínica
       - Cultivo en MacConkey
       - Pruebas bioquímicas (Oxidasa, Lactosa)
       - Características fenotípicas (Pigmento, Olor, 42°C)
       - Confirmar identificación de P. aeruginosa
       - Habilita Tab 1 al completar

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

        # Inicializar controladores SOLID (Dependency Injection)
        self.nav_controller: Optional[TabNavigationController] = None
        self.event_handler = WorkflowEventHandler(self)
        self.data_manager = WorkflowDataManager()

        self._init_ui()
        self._connect_signals()
        self._setup_controllers()

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

        # === TAB 0: Identificación Bacteriana ===
        id_tab = QWidget()
        id_layout = QVBoxLayout(id_tab)
        id_layout.setContentsMargins(15, 15, 15, 15)
        id_layout.setSpacing(15)

        # Instrucciones
        id_instructions_label = QLabel(
            "⚕️ <b>PASO 0:</b> Identifique el organismo antes de realizar el AST (flujo clínico real)"
        )
        id_instructions_label.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                color: #856404;
                padding: 12px;
                border-left: 5px solid #ffc107;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        id_layout.addWidget(id_instructions_label)

        # Widget de identificación
        self.identification_widget = BacteriaIdentificationWidget()
        self.identification_widget.identification_completed.connect(
            self._on_identification_completed
        )
        id_layout.addWidget(self.identification_widget, stretch=1)

        # Botón siguiente (inicialmente deshabilitado)
        id_nav_layout = QHBoxLayout()
        id_nav_layout.addStretch()

        self.next_profile_btn = QPushButton("Siguiente: Generar Perfil ➔")
        self.next_profile_btn.setStyleSheet("""
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
        self.next_profile_btn.setEnabled(False)
        self.next_profile_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(1))
        id_nav_layout.addWidget(self.next_profile_btn)

        id_layout.addLayout(id_nav_layout)

        self.main_tabs.addTab(id_tab, "0️⃣ Identificación")

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
        next_config_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(2))
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
        back_profile_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(1))
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
        next_plate_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(3))
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
        back_config_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(2))
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
        next_results_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(4))
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
        back_plate_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(3))
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
        next_curves_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(5))
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
        back_results_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(4))
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
        self.main_tabs.setTabEnabled(1, False)  # Perfil Bacteriano
        self.main_tabs.setTabEnabled(2, False)  # Configurar AST
        self.main_tabs.setTabEnabled(3, False)  # Placa
        self.main_tabs.setTabEnabled(4, False)  # Resultados
        self.main_tabs.setTabEnabled(5, False)  # Curvas

    def _setup_controllers(self):
        """
        Configura los controladores SOLID (Dependency Injection).

        Separa responsabilidades siguiendo principios SOLID:
        - TabNavigationController: Gestión de navegación
        - WorkflowEventHandler: Procesamiento de eventos
        - WorkflowDataManager: Gestión de datos
        """
        # Inicializar controlador de navegación
        self.nav_controller = TabNavigationController(self.main_tabs)

        # Registrar botones de navegación
        self.nav_controller.register_button("next_profile", self.next_profile_btn)
        self.nav_controller.register_button("next_config", self.next_config_btn)
        self.nav_controller.register_button("next_plate", self.next_plate_btn)

        # Suscribir event handler a eventos del workflow
        self.event_handler.subscribe(
            "identification_completed",
            lambda **kw: self.nav_controller.enable_workflow_step("identification"),
        )

        self.event_handler.subscribe(
            "profile_generated",
            lambda **kw: self._handle_profile_generated_event(**kw),
        )

        self.event_handler.subscribe(
            "ast_completed", lambda **kw: self._handle_ast_completed_event(**kw)
        )

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

    def _on_identification_completed(
        self, organism: str, sample_origin: str, confidence: float
    ):
        """
        Maneja la identificación completada de la bacteria.

        Args:
            organism: Organismo identificado (e.g., "Pseudomonas aeruginosa")
            sample_origin: Origen de la muestra clínica
            confidence: Confianza en la identificación (0.0-1.0)
        """
        # Habilitar siguiente tab y botón
        self.main_tabs.setTabEnabled(1, True)
        self.next_profile_btn.setEnabled(True)

        # Actualizar status bar
        main_window = self.window()
        if hasattr(main_window, "statusBar"):
            main_window.statusBar().showMessage(
                f"✓ Identificación completada: {organism} ({confidence * 100:.1f}% confianza) - "
                f"Muestra: {sample_origin} - Puede pasar al Paso 1",
                8000,
            )

    def _on_profile_generated(self, bacteria_profile_id: int, genotype: dict):
        """
        Maneja la generación exitosa de un perfil bacteriano.

        Delegación SOLID: Usa event_handler y data_manager.
        """
        # Almacenar perfil en data manager
        self.data_manager.set_bacteria_profile(bacteria_profile_id)

        # Establecer perfil en panel AST
        self.panel_widget.set_bacteria_profile(bacteria_profile_id)

        # Delegar a event handler
        self.event_handler.handle_profile_generated(bacteria_profile_id, genotype)

    def _handle_profile_generated_event(
        self, profile_id: int, genotype: dict, mutations: int
    ):
        """Maneja evento de perfil generado desde event handler."""
        self.nav_controller.enable_workflow_step("profile")

    def _on_ast_completed(self, results: dict):
        """
        Maneja la finalización exitosa de la simulación AST.

        Delegación SOLID: Usa data_manager para transformar datos.
        """
        # Almacenar resultados en data manager
        self.data_manager.set_ast_results(results)

        # Obtener datos procesados
        well_data_list = self.data_manager.get_well_data()
        mic_results = self.data_manager.get_mic_results()

        # Cargar datos en widgets de visualización
        self.plate_viewer.load_well_data(well_data_list)
        self.results_table.load_results(mic_results)

        # Generar y cargar curvas de crecimiento (delegado a data_manager)
        growth_data = self.data_manager.generate_growth_curves_data(
            well_data_list, mic_results
        )

        # DEBUG: Verificar datos generados
        print(f"[DEBUG] growth_data type: {type(growth_data)}")
        print(
            f"[DEBUG] growth_data keys: {list(growth_data.keys()) if growth_data else 'None'}"
        )
        if growth_data:
            for ab, curves in growth_data.items():
                print(f"[DEBUG] {ab}: {len(curves)} curves")

        if growth_data:
            self.growth_curve_widget.load_growth_data(growth_data)
        else:
            print("[WARNING] No growth data generated!")

        # Delegar a event handler
        self.event_handler.handle_ast_completed(results)

    def _handle_ast_completed_event(self, results: dict, wells: int, antibiotics: int):
        """Maneja evento de AST completado desde event handler."""
        self.nav_controller.enable_workflow_step("visualization")

    def _on_ast_failed(self, error_message: str):
        """
        Maneja el fallo de la simulación AST.

        Delegación SOLID: Usa event_handler para notificación.
        """
        self.event_handler.handle_ast_failed(error_message)

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

    def _restart_workflow(self):
        """
        Reinicia el flujo de trabajo completo.

        Delegación SOLID: Usa nav_controller para resetear navegación.
        """
        from PyQt5.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Reiniciar simulación",
            "¿Está seguro que desea reiniciar?\n\nSe perderán todos los datos actuales.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Limpiar todos los widgets y datos
            self.clear_all()

            # Resetear navegación usando controlador SOLID
            self.nav_controller.reset_navigation()

            # Mensaje status bar
            main_window = self.window()
            if hasattr(main_window, "statusBar"):
                main_window.statusBar().showMessage(
                    "🔄 Simulación reiniciada - Comience desde el Paso 1", 5000
                )

    def clear_all(self):
        """
        Limpia todos los widgets y datos.

        Delegación SOLID: Usa data_manager para limpiar datos.
        """
        # Limpiar datos del workflow
        self.data_manager.clear_all()

        # Limpiar widgets de entrada
        if hasattr(self.identification_widget, "reset"):
            self.identification_widget.reset()
        if hasattr(self.profile_widget, "reset"):
            self.profile_widget.reset()
        if hasattr(self.panel_widget, "reset"):
            self.panel_widget.reset()

        # Limpiar widgets de visualización
        self.plate_viewer.clear()
        self.results_table.clear()
        self.growth_curve_widget.clear()
