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
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QProgressBar,
    QGroupBox,
    QFormLayout,
    QMessageBox,
)
from PyQt5.QtCore import pyqtSignal, QThread

from src.data.database import get_session
from src.data.models import PanelLayout
from src.core.ast_simulator import ASTSimulator


class ASTWorker(QThread):
    """
    Worker thread para ejecutar simulación AST en segundo plano.

    Evita bloquear la interfaz durante la simulación (18h simuladas).
    """

    progress = pyqtSignal(int)  # Progreso 0-100
    finished = pyqtSignal(dict)  # Reporte final
    error = pyqtSignal(str)  # Mensaje de error

    def __init__(
        self,
        bacteria_profile_id: int,
        panel_layout_id: int,
        inoculo_mcfarland: float,
        temperatura: float,
        duracion_horas: float,
    ):
        super().__init__()
        self.bacteria_profile_id = bacteria_profile_id
        self.panel_layout_id = panel_layout_id
        self.inoculo_mcfarland = inoculo_mcfarland
        self.temperatura = temperatura
        self.duracion_horas = duracion_horas

    def run(self):
        """Ejecuta la simulación AST."""
        try:
            # Inicializar simulador
            simulator = ASTSimulator(
                bacteria_profile_id=self.bacteria_profile_id,
                panel_layout_id=self.panel_layout_id,
            )

            # Paso 1: Simulación de incubación (40% del progreso)
            self.progress.emit(10)
            well_data_list = simulator.simulate_incubation(
                duracion_horas=self.duracion_horas,
                temperatura=self.temperatura,
                inoculo_mcfarland=self.inoculo_mcfarland,
            )
            self.progress.emit(40)

            # Paso 2: Cálculo de MICs (30% del progreso)
            mic_results = simulator.calculate_mics(well_data_list)
            self.progress.emit(70)

            # Paso 3: Validación QC (20% del progreso)
            qc_report = simulator.apply_qc_checks(well_data_list)
            self.progress.emit(90)

            # Paso 4: Generar reporte final (10% del progreso)
            report = simulator.get_report(
                well_data_list=well_data_list,
                mic_results=mic_results,
                qc_report=qc_report,
            )
            self.progress.emit(100)

            # Emitir resultado
            self.finished.emit(report)

        except Exception as e:
            self.error.emit(f"Error en simulación: {str(e)}")


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

        self._init_ui()
        self._load_panels()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)

        # Grupo: Configuración AST
        config_group = QGroupBox("Configuración AST")
        config_layout = QFormLayout()

        # Organismo (fijo, no editable)
        organism_label = QLabel("<b>Pseudomonas aeruginosa</b>")
        organism_label.setStyleSheet("color: #2c3e50;")
        config_layout.addRow("Organismo:", organism_label)

        # Panel selector
        self.panel_combo = QComboBox()
        self.panel_combo.setToolTip("Seleccione el panel de antibióticos a simular")
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
        config_layout.addRow("Inóculo:", self.inoculo_spin)

        # Temperatura
        self.temperatura_spin = QDoubleSpinBox()
        self.temperatura_spin.setRange(35.0, 37.0)
        self.temperatura_spin.setSingleStep(0.5)
        self.temperatura_spin.setValue(37.0)
        self.temperatura_spin.setDecimals(1)
        self.temperatura_spin.setSuffix(" °C")
        self.temperatura_spin.setToolTip("Temperatura de incubación (37°C estándar)")
        config_layout.addRow("Temperatura:", self.temperatura_spin)

        # Duración (fija)
        duracion_label = QLabel("<b>18.0 h</b> (estándar)")
        duracion_label.setStyleSheet("color: #7f8c8d;")
        duracion_label.setToolTip("Duración estándar para AST según CLSI M07")
        config_layout.addRow("Duración:", duracion_label)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # Botón ejecutar
        self.run_button = QPushButton("▶ Ejecutar AST")
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.run_button.clicked.connect(self._on_run_clicked)
        layout.addWidget(self.run_button)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Label de estado
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.status_label)

        layout.addStretch()

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

        # Mostrar barra de progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(" Ejecutando simulación...")

        # Crear worker
        self.worker = ASTWorker(
            bacteria_profile_id=self.current_bacteria_profile_id,
            panel_layout_id=panel_layout_id,
            inoculo_mcfarland=self.inoculo_spin.value(),
            temperatura=self.temperatura_spin.value(),
            duracion_horas=18.0,
        )

        # Conectar señales
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)

        # Iniciar
        self.worker.start()

    def _on_progress(self, value: int):
        """Actualiza la barra de progreso."""
        self.progress_bar.setValue(value)

        # Actualizar mensaje según progreso
        if value <= 40:
            self.status_label.setText(" Simulando incubación (18h)...")
        elif value <= 70:
            self.status_label.setText(" Calculando MICs...")
        elif value <= 90:
            self.status_label.setText(" Validando controles QC...")
        else:
            self.status_label.setText(" Generando reporte...")

    def _on_finished(self, report: dict):
        """Maneja la finalización exitosa de la simulación."""
        # Rehabilitar controles
        self.run_button.setEnabled(True)
        self.panel_combo.setEnabled(True)
        self.inoculo_spin.setEnabled(True)
        self.temperatura_spin.setEnabled(True)

        # Ocultar barra de progreso
        self.progress_bar.setVisible(False)

        # Actualizar estado
        self.status_label.setText(" Simulación completada exitosamente")

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

        # Ocultar barra de progreso
        self.progress_bar.setVisible(False)

        # Actualizar estado
        self.status_label.setText(" Error en simulación")

        # Emitir señal
        self.ast_failed.emit(error_msg)

        # Mostrar error
        QMessageBox.critical(
            self,
            "Error en simulación",
            f"Ocurrió un error durante la simulación:\n\n{error_msg}",
        )
