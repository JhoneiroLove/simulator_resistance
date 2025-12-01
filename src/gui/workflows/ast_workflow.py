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
    QSizePolicy,
    QScrollArea,
    QFrame,
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
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === TÍTULO ===
        title_widget = QWidget()
        title_widget.setStyleSheet(
            "background-color: #FFFFFF; border-bottom: 2px solid #E1E8ED;"
        )
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(20, 12, 20, 12)

        title_label = QLabel("🧬 Simulador de Antibiograma (AST)")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #1A252F;
                background: transparent;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        main_layout.addWidget(title_widget)

        # === SISTEMA DE PESTAÑAS PRINCIPAL ===
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #F5F7FA;
            }
            QTabBar::tab {
                background-color: #FFFFFF;
                color: #5A6C7D;
                padding: 12px 24px;
                margin-right: 2px;
                border: none;
                border-bottom: 3px solid transparent;
                font-size: 13px;
                font-weight: 500;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #841C1C;
                border-bottom: 3px solid #841C1C;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background-color: #F8F9FA;
                color: #2C3E50;
            }
            QTabBar::tab:disabled {
                color: #BDC3C7;
                background-color: #F5F7FA;
            }
        """)

        # === TAB 0: Identificación Bacteriana ===
        id_tab = self._create_identification_tab()
        self.main_tabs.addTab(id_tab, "Identificación")

        # === TAB 1: Generar Perfil Bacteriano ===
        profile_tab = self._create_profile_tab()
        self.main_tabs.addTab(profile_tab, "Perfil Bacteriano")

        # === TAB 2: Configurar AST ===
        config_tab = self._create_config_tab()
        self.main_tabs.addTab(config_tab, "Configurar AST")

        # === TAB 3: Visualizar Placa ===
        plate_tab = self._create_plate_tab()
        self.main_tabs.addTab(plate_tab, "Placa AST")

        # === TAB 4: Resultados MIC ===
        results_tab = self._create_results_tab()
        self.main_tabs.addTab(results_tab, "Resultados MIC")

        # === TAB 5: Curvas de Crecimiento ===
        curves_tab = self._create_curves_tab()
        self.main_tabs.addTab(curves_tab, "Curvas Crecimiento")

        # Agregar tabs al layout principal
        main_layout.addWidget(self.main_tabs, stretch=1)

        # Deshabilitar tabs hasta que se complete el flujo
        self.main_tabs.setTabEnabled(1, False)  # Perfil Bacteriano
        self.main_tabs.setTabEnabled(2, False)  # Configurar AST
        self.main_tabs.setTabEnabled(3, False)  # Placa
        self.main_tabs.setTabEnabled(4, False)  # Resultados
        self.main_tabs.setTabEnabled(5, False)  # Curvas

    def _create_identification_tab(self):
        """Crea la pestaña de identificación bacteriana."""
        # Crear scroll area para el tab
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Widget de identificación
        self.identification_widget = BacteriaIdentificationWidget()
        self.identification_widget.identification_completed.connect(
            self._on_identification_completed
        )
        layout.addWidget(self.identification_widget, stretch=1)

        # Botón siguiente
        nav_layout = QHBoxLayout()

        self.next_profile_btn = QPushButton("Siguiente: Generar Perfil ➔")
        self.next_profile_btn.setEnabled(False)
        self.next_profile_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(1))
        nav_layout.addWidget(self.next_profile_btn)
        nav_layout.addStretch()

        layout.addLayout(nav_layout)

        scroll_area.setWidget(tab_widget)
        return scroll_area

    def _create_profile_tab(self):
        """Crea la pestaña de perfil bacteriano."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Instrucciones
        instructions_label = QLabel(
            "📋 <b>PASO 1:</b> Genere un perfil bacteriano para comenzar la simulación AST"
        )
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet("""
            QLabel {
                background-color: #E8F4F8;
                color: #1A5276;
                padding: 14px 16px;
                border-left: 5px solid #3498DB;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        instructions_label.setToolTip(
            "Genere un perfil de Pseudomonas aeruginosa seleccionando\n"
            "entre bacteria sensible (wild-type) o con resistencias adquiridas."
        )
        instructions_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(instructions_label)

        self.profile_widget = BacteriaProfileWidget()
        layout.addWidget(self.profile_widget, stretch=1)

        # Botón siguiente
        next_config_layout = QHBoxLayout()

        self.next_config_btn = QPushButton("Siguiente: Configurar AST ➔")
        self.next_config_btn.setEnabled(False)
        self.next_config_btn.setToolTip(
            "Continúe al paso de configuración del panel AST\n"
            "(Disponible después de generar un perfil bacteriano)"
        )
        self.next_config_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(2))
        next_config_layout.addWidget(self.next_config_btn)
        next_config_layout.addStretch()

        layout.addLayout(next_config_layout)

        scroll_area.setWidget(tab_widget)
        return scroll_area

    def _create_config_tab(self):
        """Crea la pestaña de configuración AST."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Agregar espacio superior para centrar verticalmente
        layout.addStretch(1)

        # Instrucciones
        config_instructions = QLabel(
            "⚙️ <b>PASO 2:</b> Configure los parámetros del panel AST y ejecute la simulación"
        )
        config_instructions.setWordWrap(True)
        config_instructions.setStyleSheet("""
            QLabel {
                background-color: #FEF5E7;
                color: #7D6608;
                padding: 14px 16px;
                border-left: 5px solid #F39C12;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        config_instructions.setToolTip(
            "Configure el panel de prueba, inóculo y condiciones de incubación.\n"
            "Después ejecute la simulación para obtener resultados MIC."
        )
        config_instructions.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(config_instructions)

        self.panel_widget = ASTPanelWidget()
        layout.addWidget(self.panel_widget, stretch=1)

        # Botones navegación
        nav_layout = QHBoxLayout()

        back_profile_btn = QPushButton("◀ Volver: Perfil")
        back_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-size: 14px;
                padding: 12px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        back_profile_btn.setFixedWidth(150)
        # Botones navegación
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)

        back_profile_btn = QPushButton("◀ Volver")
        back_profile_btn.setProperty("secondary", True)
        back_profile_btn.setToolTip(
            "Regresar al paso de generación de perfil bacteriano"
        )
        back_profile_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(1))
        nav_layout.addWidget(back_profile_btn)

        self.next_plate_btn = QPushButton("Siguiente: Ver Placa ➔")
        self.next_plate_btn.setEnabled(False)
        self.next_plate_btn.setToolTip(
            "Visualizar la placa de 96 pocillos con resultados\n"
            "(Disponible después de ejecutar la simulación AST)"
        )
        self.next_plate_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(3))
        nav_layout.addWidget(self.next_plate_btn)

        nav_layout.addStretch()

        layout.addLayout(nav_layout)

        # Agregar espacio inferior para centrar verticalmente
        layout.addStretch(1)

        return tab_widget

    def _create_plate_tab(self):
        """Crea la pestaña de visualización de placa."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Instrucciones
        plate_instructions = QLabel(
            "🔬 <b>PASO 3:</b> Visualice la placa de 96 pocillos y el crecimiento bacteriano"
        )
        plate_instructions.setWordWrap(True)
        plate_instructions.setStyleSheet("""
            QLabel {
                background-color: #EAF2F8;
                color: #1B4F72;
                padding: 14px 16px;
                border-left: 5px solid #5DADE2;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        plate_instructions.setToolTip(
            "Haga clic en cualquier pocillo para ver detalles de\n"
            "antibiótico, concentración y densidad óptica final."
        )
        plate_instructions.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(plate_instructions)

        self.plate_viewer = ASTPlateViewer()
        layout.addWidget(self.plate_viewer, stretch=1)

        # Botones navegación
        plate_nav_layout = QHBoxLayout()
        plate_nav_layout.setSpacing(10)

        back_config_btn = QPushButton("◀ Volver")
        back_config_btn.setProperty("secondary", True)
        back_config_btn.setToolTip("Regresar a la configuración del panel AST")
        back_config_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(2))
        plate_nav_layout.addWidget(back_config_btn)

        next_results_btn = QPushButton("Siguiente: Ver Resultados ➔")
        next_results_btn.setToolTip(
            "Continuar a la tabla de resultados MIC con interpretaciones clínicas"
        )
        next_results_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(4))
        plate_nav_layout.addWidget(next_results_btn)

        plate_nav_layout.addStretch()

        layout.addLayout(plate_nav_layout)

        scroll_area.setWidget(tab_widget)
        return scroll_area

    def _create_results_tab(self):
        """Crea la pestaña de resultados MIC."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Instrucciones
        results_instructions = QLabel(
            "📊 <b>PASO 4:</b> Analice los resultados MIC con interpretación clínica"
        )
        results_instructions.setWordWrap(True)
        results_instructions.setStyleSheet("""
            QLabel {
                background-color: #EAFAF1;
                color: #145A32;
                padding: 14px 16px;
                border-left: 5px solid #27AE60;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        results_instructions.setToolTip(
            "Revise los valores MIC calculados y las interpretaciones S/R\n"
            "según guidelines EUCAST/CLSI. Puede exportar los resultados."
        )
        results_instructions.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(results_instructions)

        self.results_table = ASTResultsTable()
        layout.addWidget(self.results_table, stretch=1)

        # Botones navegación
        results_nav_layout = QHBoxLayout()
        results_nav_layout.setSpacing(10)

        back_plate_btn = QPushButton("◀ Volver")
        back_plate_btn.setProperty("secondary", True)
        back_plate_btn.setToolTip(
            "Regresar a la visualización de la placa de 96 pocillos"
        )
        back_plate_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(3))
        results_nav_layout.addWidget(back_plate_btn)

        next_curves_btn = QPushButton("Siguiente: Ver Curvas ➔")
        next_curves_btn.setToolTip(
            "Ver curvas de crecimiento detalladas por antibiótico y concentración"
        )
        next_curves_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(5))
        results_nav_layout.addWidget(next_curves_btn)

        results_nav_layout.addStretch()

        layout.addLayout(results_nav_layout)

        scroll_area.setWidget(tab_widget)
        return scroll_area

    def _create_curves_tab(self):
        """Crea la pestaña de curvas de crecimiento."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Instrucciones
        curves_instructions = QLabel(
            "📈 <b>PASO 5:</b> Explore las curvas de crecimiento por antibiótico y concentración"
        )
        curves_instructions.setWordWrap(True)
        curves_instructions.setStyleSheet("""
            QLabel {
                background-color: #F4ECF7;
                color: #512E5F;
                padding: 14px 16px;
                border-left: 5px solid #9B59B6;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        curves_instructions.setToolTip(
            "Seleccione un antibiótico para visualizar las curvas de crecimiento\n"
            "a diferentes concentraciones durante las 18 horas de incubación."
        )
        curves_instructions.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(curves_instructions)

        self.growth_curve_widget = GrowthCurveWidget()
        layout.addWidget(self.growth_curve_widget, stretch=1)

        # Botones navegación
        curves_nav_layout = QHBoxLayout()
        curves_nav_layout.setSpacing(10)

        back_results_btn = QPushButton("◀ Volver")
        back_results_btn.setProperty("secondary", True)
        back_results_btn.setToolTip("Regresar a la tabla de resultados MIC")
        back_results_btn.clicked.connect(lambda: self.main_tabs.setCurrentIndex(4))
        curves_nav_layout.addWidget(back_results_btn)

        restart_btn = QPushButton("🔄 Nueva Simulación")
        restart_btn.setToolTip(
            "Reiniciar el workflow completo para crear una nueva simulación AST\n"
            "(Se perderán todos los datos actuales)"
        )
        restart_btn.clicked.connect(self._restart_workflow)
        curves_nav_layout.addWidget(restart_btn)

        curves_nav_layout.addStretch()

        layout.addLayout(curves_nav_layout)

        scroll_area.setWidget(tab_widget)
        return scroll_area

    def _setup_controllers(self):
        """
        Configura los controladores SOLID (Dependency Injection).
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
        """
        self.event_handler.handle_ast_failed(error_message)

    def _on_well_clicked(self, well_id: str, well_data: dict):
        """
        Maneja el clic en un pocillo de la placa.
        """
        antibiotico = well_data.get("antibiotico", "Control")
        concentracion = well_data.get("concentracion", 0)
        od_final = well_data.get("od_final", 0)

        status_msg = f"🔬 Pocillo {well_id}: {antibiotico} ({concentracion:.2f} µg/mL) - OD: {od_final:.3f}"

        main_window = self.window()
        if hasattr(main_window, "statusBar"):
            main_window.statusBar().showMessage(status_msg, 3000)

    def _on_antibiotic_selected(self, antibiotico: str, data: dict):
        """
        Maneja la selección de un antibiótico en la tabla de resultados.
        """
        mic = data.get("mic_value", 0)
        interpretacion = data.get("interpretacion", "N/A")

        status_msg = (
            f"💊 {antibiotico}: MIC = {mic:.2f} µg/mL, Interpretación: {interpretacion}"
        )

        main_window = self.window()
        if hasattr(main_window, "statusBar"):
            main_window.statusBar().showMessage(status_msg, 3000)

    def _restart_workflow(self):
        """
        Reinicia el flujo de trabajo completo.
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
