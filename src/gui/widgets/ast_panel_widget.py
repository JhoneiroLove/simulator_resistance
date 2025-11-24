"""
Widget AST Panel - Configuración de Panel AST

Widget para configurar parámetros de simulación AST:
- Organismo fijo: Pseudomonas aeruginosa
- Selección de panel predefinido
- Parámetros: inóculo, temperatura, duración
- Ejecución de simulación con barra de progreso

Autor: Sistema AST Simulator
Fecha: 11 de noviembre de 2025
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QProgressBar,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QCheckBox,
    QStackedWidget,
    QSizePolicy,
    QScrollArea,
    QFrame,
)
from PyQt5.QtCore import pyqtSignal, Qt, QThread
import time

from src.data.database import get_session
from src.data.models import PanelLayout
from src.core.ast_simulator import ASTSimulator
from src.gui.widgets.incubation_progress_widget import IncubationProgressWidget


class ASTWorker(QThread):
    """
    Worker thread para ejecutar simulacion AST en segundo plano.

    Evita bloquear la interfaz durante la simulacion (18h simuladas).
    Soporta modo progresivo (hora por hora) y modo rapido (completo).
    """

    progress = pyqtSignal(int)  # Progreso 0-100
    time_progress = pyqtSignal(int, dict)  # (hora, datos_parciales)
    finished = pyqtSignal(dict)  # Reporte final
    error = pyqtSignal(str)  # Mensaje de error

    # Señal para ajustar velocidad dinámicamente
    speed_changed = pyqtSignal(int)  # Multiplicador de velocidad (1, 2, 4)

    def __init__(
        self,
        bacteria_profile_id: int,
        panel_layout_id: int,
        inoculo_mcfarland: float,
        temperatura: float,
        duracion_horas: float,
        progressive_mode: bool = False,  # NUEVO: modo progresivo
    ):
        super().__init__()
        self.bacteria_profile_id = bacteria_profile_id
        self.panel_layout_id = panel_layout_id
        self.inoculo_mcfarland = inoculo_mcfarland
        self.temperatura = temperatura
        self.duracion_horas = duracion_horas
        self.progressive_mode = progressive_mode
        self.speed_multiplier = 1  # Velocidad actual (1x, 2x, 4x)

    def run(self):
        """Ejecuta la simulación AST."""
        print(
            f"[ASTWorker] Iniciando - Modo: {'PROGRESIVO' if self.progressive_mode else 'RÁPIDO'}"
        )
        try:
            # Obtener el panel_name desde el panel_layout_id
            from src.data.database import get_session
            from src.data.models import PanelLayout

            session = get_session()
            panel_layout = (
                session.query(PanelLayout)
                .filter(PanelLayout.id == self.panel_layout_id)
                .first()
            )

            if not panel_layout:
                self.error.emit(f"Panel con ID {self.panel_layout_id} no encontrado")
                return

            panel_name = panel_layout.panel_name
            session.close()

            print(
                f"[ASTWorker] Panel: {panel_name}, Bacteria: {self.bacteria_profile_id}"
            )

            # Inicializar simulador
            simulator = ASTSimulator(
                bacteria_profile_id=self.bacteria_profile_id,
                panel_name=panel_name,
                inoculo_mcfarland=self.inoculo_mcfarland,
                temperatura=self.temperatura,
                duracion_horas=int(self.duracion_horas),
            )

            if self.progressive_mode:
                # MODO PROGRESIVO: Simular hora por hora
                total_hours = int(self.duracion_horas)
                for hour in range(total_hours + 1):  # 0 a 18
                    # Simular hasta esta hora
                    simulator.simulate_incubation(max_hours=hour)

                    # Calcular MICs parciales
                    partial_mics = simulator.calculate_mics()

                    # Emitir datos parciales
                    partial_data = {
                        "hour": hour,
                        "well_data": simulator.panel_wells,  # CORREGIDO: panel_wells en lugar de well_data
                        "mics": partial_mics,
                    }
                    self.time_progress.emit(hour, partial_data)

                    # Actualizar progreso (0-100)
                    progress_pct = int((hour / total_hours) * 100)
                    self.progress.emit(progress_pct)

                    # NUEVO v5.0: Delay ajustable según velocidad (0.5s base / multiplier)
                    if hour < total_hours:
                        delay = 0.5 / self.speed_multiplier
                        time.sleep(delay)

                # Al terminar, generar reporte completo
                simulator.apply_qc_checks()
                report = simulator.get_report()
                self.progress.emit(100)
                self.finished.emit(report)

            else:
                # MODO RÁPIDO: Simulación completa instantánea
                self.progress.emit(10)
                simulator.simulate_incubation()
                self.progress.emit(40)

                simulator.calculate_mics()
                self.progress.emit(70)

                simulator.apply_qc_checks()
                self.progress.emit(90)

                report = simulator.get_report()
                self.progress.emit(100)

                self.finished.emit(report)

        except Exception as e:
            self.error.emit(f"Error en simulación: {str(e)}")

    def set_speed(self, multiplier: int):
        """
        Ajusta la velocidad de simulación dinámicamente.

        Args:
            multiplier: Multiplicador de velocidad (1, 2, 4)
        """
        self.speed_multiplier = max(1, min(4, multiplier))


class ASTPanelWidget(QWidget):
    """
    Widget para configuración y ejecución de panel AST.

    Características:
    - Organismo fijo: P. aeruginosa (no seleccionable)
    - Panel seleccionable desde BD
    - Parámetros ajustables: inóculo, temperatura
    - Duración fija: 18h (estándar AST)
    - Ejecución asíncrona con barra de progreso

    Signals:
        ast_completed: Emitido cuando simulación termina (con reporte)
        ast_failed: Emitido si simulación falla (con mensaje error)
    """

    ast_completed = pyqtSignal(dict)  # Reporte completo
    ast_failed = pyqtSignal(str)  # Mensaje de error

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.session = get_session()
        self.worker: Optional[ASTWorker] = None
        self.current_bacteria_profile_id: Optional[int] = None
        self.incubation_widget: Optional[IncubationProgressWidget] = None

        self._init_ui()
        self._load_panels()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""

        # Crear scroll area principal
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Contenedor central con ancho máximo
        central_container = QWidget()
        central_layout = QHBoxLayout(central_container)
        central_layout.setContentsMargins(0, 0, 0, 0)

        main_widget = QWidget()
        main_widget.setMaximumWidth(900)  # Limitar ancho máximo
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Centrar el contenido
        central_layout.addStretch()
        central_layout.addWidget(main_widget)
        central_layout.addStretch()

        # Grupo: Configuración AST
        config_group = QGroupBox("Configuración AST")
        config_group.setStyleSheet("""
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
                padding: 0 5px;
                color: #3498db;
            }
        """)
        config_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        config_layout = QFormLayout()
        config_layout.setLabelAlignment(Qt.AlignLeft)
        config_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Organismo (fijo, no editable)
        organism_label = QLabel("<b>Pseudomonas aeruginosa</b>")
        organism_label.setStyleSheet("color: #2c3e50;")
        organism_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        config_layout.addRow("Organismo:", organism_label)

        # Panel selector
        self.panel_combo = QComboBox()
        self.panel_combo.setToolTip("Seleccione el panel de antibióticos a simular")
        self.panel_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        self.panel_combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        config_layout.addRow("Panel:", self.panel_combo)

        # Inóculo (McFarland)
        self.inoculo_spin = QDoubleSpinBox()
        self.inoculo_spin.setRange(0.3, 0.7)
        self.inoculo_spin.setSingleStep(0.1)
        self.inoculo_spin.setValue(0.5)
        self.inoculo_spin.setDecimals(1)
        self.inoculo_spin.setSuffix(" McF")
        self.inoculo_spin.setToolTip(
            "Densidad del inóculo bacteriano (0.5 McFarland estándar)"
        )
        self.inoculo_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QDoubleSpinBox:focus {
                border-color: #3498db;
            }
        """)
        self.inoculo_spin.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        config_layout.addRow("Inóculo:", self.inoculo_spin)

        # Temperatura
        self.temperatura_spin = QDoubleSpinBox()
        self.temperatura_spin.setRange(35.0, 37.0)
        self.temperatura_spin.setSingleStep(0.5)
        self.temperatura_spin.setValue(37.0)
        self.temperatura_spin.setDecimals(1)
        self.temperatura_spin.setSuffix(" °C")
        self.temperatura_spin.setToolTip("Temperatura de incubación (37°C estándar)")
        self.temperatura_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QDoubleSpinBox:focus {
                border-color: #3498db;
            }
        """)
        self.temperatura_spin.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        config_layout.addRow("Temperatura:", self.temperatura_spin)

        # Duración (fija)
        duracion_label = QLabel("<b>18.0 h</b> (estándar)")
        duracion_label.setStyleSheet("color: #7f8c8d;")
        duracion_label.setToolTip("Duración estándar para AST según CLSI M07")
        duracion_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        config_layout.addRow("Duración:", duracion_label)

        # Modo temporal
        self.progressive_mode_check = QCheckBox("Simulación temporal (hora por hora)")
        self.progressive_mode_check.setToolTip(
            "Simula el crecimiento bacteriano hora por hora (18h reales aceleradas)\n"
            "Desactivado: simulación instantánea"
        )
        self.progressive_mode_check.setChecked(False)
        self.progressive_mode_check.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Fixed
        )
        config_layout.addRow("Modo:", self.progressive_mode_check)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # === CONTENEDOR PARA BOTÓN Y BARRA DE CARGA ===
        button_progress_container = QHBoxLayout()
        button_progress_container.setSpacing(20)

        # Botón ejecutar
        self.run_button = QPushButton("▶ Ejecutar AST")
        self.run_button.setMinimumHeight(40)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.run_button.setFixedWidth(180)
        self.run_button.clicked.connect(self._on_run_clicked)
        button_progress_container.addWidget(self.run_button)

        # Barra de progreso simple
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(40)
        self.progress_bar.setVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #27ae60;
                border-radius: 5px;
                text-align: center;
                background-color: #f8f9fa;
                font-weight: bold;
                color: #2c3e50;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0% - Listo")
        self.progress_bar.setFixedWidth(450)
        button_progress_container.addWidget(self.progress_bar)
        button_progress_container.addStretch()

        layout.addLayout(button_progress_container)

        # === MENSAJE DE ESTADO ===
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d; 
                font-style: italic;
                padding: 5px;
                background-color: #f8f9fa;
                border-radius: 3px;
            }
        """)
        self.status_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Contenedor apilado: Widget visual (solo para modo progresivo)
        self.progress_stack = QStackedWidget()
        self.progress_stack.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Página 0: Vacía (no se usa en modo rápido)
        empty_widget = QWidget()
        empty_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.progress_stack.addWidget(empty_widget)

        # Página 1: Widget de progreso visual (modo progresivo)
        self.incubation_widget = IncubationProgressWidget()
        self.incubation_widget.setVisible(False)
        self.incubation_widget.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred
        )
        self.progress_stack.addWidget(self.incubation_widget)

        self.progress_stack.setCurrentIndex(0)  # Por defecto: vacío
        layout.addWidget(self.progress_stack)

        # Configurar scroll area
        scroll_area.setWidget(central_container)

        # Layout principal del widget
        widget_layout = QVBoxLayout(self)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(scroll_area)

    def _load_panels(self):
        """Carga paneles disponibles desde la base de datos."""
        try:
            # Query para obtener nombres únicos de paneles
            panels = self.session.query(PanelLayout.panel_name).distinct().all()

            if not panels:
                self.panel_combo.addItem("Sin paneles disponibles")
                self.run_button.setEnabled(False)
                return

            # Agregar paneles al combo
            for panel in panels:
                panel_name = panel[0]
                # Formatear nombre para display
                display_name = panel_name.replace("_", " ").title()
                self.panel_combo.addItem(display_name, panel_name)

            # Seleccionar panel por defecto
            default_index = self.panel_combo.findData("Pseudomonas_Standard_Panel")
            if default_index >= 0:
                self.panel_combo.setCurrentIndex(default_index)

        except Exception as e:
            QMessageBox.warning(
                self,
                "Error al cargar paneles",
                f"No se pudieron cargar los paneles disponibles:\n{str(e)}",
            )
            self.run_button.setEnabled(False)

    def set_bacteria_profile(self, bacteria_profile_id: int):
        """
        Establece el perfil bacteriano para la simulación.

        Args:
            bacteria_profile_id: ID del perfil en tabla bacteria_profiles
        """
        self.current_bacteria_profile_id = bacteria_profile_id
        self.run_button.setEnabled(True)
        self.status_label.setText(
            f"✓ Perfil bacteriano cargado (ID: {bacteria_profile_id})"
        )

    def _on_run_clicked(self):
        """Maneja el clic en el botón ejecutar."""
        # Validar que hay un perfil bacteriano
        if self.current_bacteria_profile_id is None:
            QMessageBox.warning(
                self,
                "Perfil no seleccionado",
                "Debe generar o seleccionar un perfil bacteriano antes de ejecutar AST.",
            )
            return

        # Obtener panel seleccionado
        panel_name = self.panel_combo.currentData()
        if not panel_name:
            QMessageBox.warning(
                self, "Panel no seleccionado", "Debe seleccionar un panel AST."
            )
            return

        # Obtener panel_layout_id
        panel_layout = (
            self.session.query(PanelLayout)
            .filter(PanelLayout.panel_name == panel_name)
            .first()
        )

        if not panel_layout:
            QMessageBox.critical(
                self, "Error", f"No se encontró el panel: {panel_name}"
            )
            return

        # Confirmar ejecución
        reply = QMessageBox.question(
            self,
            "Confirmar simulación",
            f"¿Ejecutar simulación AST?\n\n"
            f"Panel: {self.panel_combo.currentText()}\n"
            f"Inóculo: {self.inoculo_spin.value()} McFarland\n"
            f"Temperatura: {self.temperatura_spin.value()}°C\n"
            f"Duración: 18.0 horas",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        # Iniciar simulación
        self._start_simulation(panel_layout.id)

    def _start_simulation(self, panel_layout_id: int):
        """Inicia la simulación en un thread separado."""
        # Deshabilitar controles
        self.run_button.setEnabled(False)
        self.panel_combo.setEnabled(False)
        self.inoculo_spin.setEnabled(False)
        self.temperatura_spin.setEnabled(False)
        self.progressive_mode_check.setEnabled(False)

        # Actualizar barra de progreso (ya está visible desde el inicio)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0% - Iniciando...")

        # Configurar según modo
        is_progressive = self.progressive_mode_check.isChecked()

        if is_progressive:
            # Modo progresivo: Mostrar widget visual completo
            self.progress_stack.setCurrentIndex(1)
            self.incubation_widget.setVisible(True)
            self.incubation_widget.reset()
            self.status_label.setText(" Ejecutando simulación progresiva...")
        else:
            # Modo rápido: Solo usar barra simple
            self.progress_stack.setCurrentIndex(0)
            self.status_label.setText(" Ejecutando simulación instantánea...")

        # Crear worker con modo progresivo
        self.worker = ASTWorker(
            bacteria_profile_id=self.current_bacteria_profile_id,
            panel_layout_id=panel_layout_id,
            inoculo_mcfarland=self.inoculo_spin.value(),
            temperatura=self.temperatura_spin.value(),
            duracion_horas=18.0,
            progressive_mode=self.progressive_mode_check.isChecked(),
        )

        # Conectar señales
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)

        # NUEVO v5.0: Conectar señal de progreso temporal
        if self.progressive_mode_check.isChecked():
            self.worker.time_progress.connect(self._on_time_progress)

            # Conectar controles de velocidad del widget con el worker
            def on_widget_speed_changed(multiplier: int):
                if self.worker and self.worker.isRunning():
                    self.worker.set_speed(multiplier)

            # Deshabilitar controles automáticos del widget (worker controla el avance)
            self.incubation_widget.timer.stop()
            # Conectar cambios de velocidad
            for button in self.incubation_widget.speed_button_group.buttons():
                button.toggled.connect(
                    lambda checked, btn=button: on_widget_speed_changed(
                        btn.property("multiplier")
                    )
                    if checked
                    else None
                )

        # Iniciar
        self.worker.start()

    def _on_progress(self, value: int):
        """Actualiza la barra de progreso."""
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{value}% - Procesando...")

        # Actualizar mensaje según progreso
        if self.progressive_mode_check.isChecked():
            # En modo temporal, mostrar hora actual
            hour = int((value / 100) * 18)
            self.status_label.setText(f" Hora {hour}/18 - Simulando crecimiento...")
        else:
            # Modo rápido: mensajes por fase
            if value <= 40:
                self.status_label.setText(" Simulando incubación (18h)...")
            elif value <= 70:
                self.status_label.setText(" Calculando MICs...")
            elif value <= 90:
                self.status_label.setText(" Validando controles QC...")
            else:
                self.status_label.setText(" Generando reporte...")

    def _on_time_progress(self, hour: int, partial_data: dict):
        """
        Maneja actualizaciones hora por hora en modo progresivo.
        Actualiza el widget visual en tiempo real.

        Args:
            hour: Hora actual (0-18)
            partial_data: Datos parciales hasta esta hora
        """
        # Actualizar widget de incubación visual
        if self.incubation_widget and self.incubation_widget.isVisible():
            # Forzar actualización del widget al tiempo actual
            while self.incubation_widget.get_current_hour() < hour:
                self.incubation_widget._advance_time()

    def _on_finished(self, report: dict):
        """Maneja la finalización exitosa de la simulación."""
        # Rehabilitar controles
        self.run_button.setEnabled(True)
        self.panel_combo.setEnabled(True)
        self.inoculo_spin.setEnabled(True)
        self.temperatura_spin.setEnabled(True)
        self.progressive_mode_check.setEnabled(True)

        # Actualizar barra de progreso (se queda en 100%)
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("100% - Completado")

        # Ocultar widget visual si está visible
        if self.incubation_widget:
            self.incubation_widget.setVisible(False)

        # Mostrar mensaje de éxito debajo
        self.status_label.setText("✓ Simulación completada exitosamente")

        # Emitir señal
        self.ast_completed.emit(report)

        # Mostrar mensaje
        QMessageBox.information(
            self,
            "Simulación completada",
            f"AST finalizado correctamente.\n\n"
            f"Antibióticos analizados: {len(report.get('mic_results', []))}\n"
            f"Estado QC: {report.get('qc', {}).get('overall_status', 'UNKNOWN')}",
        )

    def _on_error(self, error_msg: str):
        """Maneja errores en la simulación."""
        # Rehabilitar controles
        self.run_button.setEnabled(True)
        self.panel_combo.setEnabled(True)
        self.inoculo_spin.setEnabled(True)
        self.temperatura_spin.setEnabled(True)
        self.progressive_mode_check.setEnabled(True)

        # Actualizar barra de progreso (vuelve a 0%)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0% - Error")

        # Ocultar widget visual si está visible
        if self.incubation_widget:
            self.incubation_widget.setVisible(False)

        # Mostrar mensaje de error debajo
        self.status_label.setText("✗ Error en simulación")

        # Emitir señal
        self.ast_failed.emit(error_msg)

        # Mostrar error
        QMessageBox.critical(
            self,
            "Error en simulación",
            f"Ocurrió un error durante la simulación:\n\n{error_msg}",
        )