"""
Widget Incubation Progress - Simulacion Temporal en Tiempo Real

Simula el progreso de incubacion del panel AST hora por hora,
mostrando:
- Reloj digital con tiempo transcurrido
- Barra de progreso visual
- Actualizacion de la placa en tiempo real
- Controles de velocidad (1x, 2x, 4x, skip)
- Informacion de estado por fase

Autor: Sistema AST Simulator
Fecha: 17 de noviembre de 2025
Version: 1.0 - Simulacion Temporal
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QGroupBox,
    QFrame,
    QButtonGroup,
    QRadioButton,
    QScrollArea,
    QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QTime
from PyQt5.QtGui import QFont


class IncubationProgressWidget(QWidget):
    """
    Widget que simula el progreso temporal de incubacion AST.

    Muestra un reloj digital que avanza hora por hora, permitiendo
    al usuario experimentar el proceso de 18 horas de incubacion
    de forma acelerada pero realista.

    Signals:
        time_updated: Emitido cada vez que avanza una hora (int: hora actual)
        incubation_completed: Emitido cuando se completan las 18 horas
        incubation_paused: Emitido cuando el usuario pausa
        incubation_resumed: Emitido cuando el usuario reanuda
    """

    time_updated = pyqtSignal(int)  # Hora actual (0-18)
    incubation_completed = pyqtSignal()
    incubation_paused = pyqtSignal()
    incubation_resumed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.current_hour = 0
        self.target_hours = 18
        self.is_running = False
        self.is_completed = False

        # Timer para simular paso del tiempo
        # Velocidades: 1x=1000ms, 2x=500ms, 4x=250ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._advance_time)
        self.speed_multiplier = 1  # 1x por defecto

        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""

        # Crear scroll area principal
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        central_container = QWidget()
        central_layout = QHBoxLayout(central_container)
        central_layout.setContentsMargins(0, 0, 0, 0)

        main_widget = QWidget()
        main_widget.setMaximumWidth(800)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        central_layout.addStretch()
        central_layout.addWidget(main_widget)
        central_layout.addStretch()

        # Titulo
        title = QLabel("🔬 Incubación en Progreso")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(title)

        # Grupo: Reloj Digital
        clock_group = QGroupBox("Tiempo Transcurrido")
        clock_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        clock_layout = QVBoxLayout(clock_group)

        self.time_display = QLabel("00:00:00")
        time_font = QFont("Courier New")
        time_font.setPointSize(48)
        time_font.setBold(True)
        self.time_display.setFont(time_font)
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: #2ecc71;
                border: 3px solid #34495e;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        self.time_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        clock_layout.addWidget(self.time_display)

        # Indicador de fase
        self.phase_label = QLabel("Fase: Lag inicial (adaptación bacteriana)")
        self.phase_label.setAlignment(Qt.AlignCenter)
        self.phase_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #34495e;
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        self.phase_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        clock_layout.addWidget(self.phase_label)

        layout.addWidget(clock_group)

        # Barra de progreso
        progress_group = QGroupBox("Progreso de Incubación")
        progress_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.target_hours)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m horas (%p%)")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                font-size: 12px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db,
                    stop:1 #2ecc71
                );
                border-radius: 3px;
            }
        """)
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        progress_layout.addWidget(self.progress_bar)

        # Marcadores de tiempo
        markers_layout = QHBoxLayout()
        markers = ["0h", "6h", "12h", "18h"]
        for i, marker in enumerate(markers):
            label = QLabel(marker)
            label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
            if i == 0:
                label.setAlignment(Qt.AlignLeft)
            elif i == len(markers) - 1:
                label.setAlignment(Qt.AlignRight)
            else:
                label.setAlignment(Qt.AlignCenter)
            markers_layout.addWidget(label)
        progress_layout.addLayout(markers_layout)

        layout.addWidget(progress_group)

        # Controles de velocidad
        speed_group = QGroupBox("Velocidad de Simulación")
        speed_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        speed_layout = QHBoxLayout(speed_group)

        speed_label = QLabel("Velocidad:")
        speed_label.setStyleSheet("font-weight: bold;")
        speed_layout.addWidget(speed_label)

        self.speed_button_group = QButtonGroup(self)
        speeds = [
            ("1x (Real)", 1),
            ("2x (Rápido)", 2),
            ("4x (Muy rápido)", 4),
        ]

        for text, multiplier in speeds:
            radio = QRadioButton(text)
            radio.setProperty("multiplier", multiplier)
            radio.toggled.connect(
                lambda checked, m=multiplier: self._on_speed_changed(m) if checked else None
            )
            self.speed_button_group.addButton(radio)
            speed_layout.addWidget(radio)

            if multiplier == 1:
                radio.setChecked(True)

        speed_layout.addStretch()
        layout.addWidget(speed_group)

        # Controles de reproducción
        controls_layout = QHBoxLayout()

        self.start_button = QPushButton("▶ Iniciar Incubación")
        self.start_button.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
        self.start_button.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.start_button.setFixedWidth(200)
        self.start_button.clicked.connect(self._on_start_clicked)
        controls_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("⏸ Pausar")
        self.pause_button.setIcon(self.style().standardIcon(self.style().SP_MediaPause))
        self.pause_button.setEnabled(False)
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.pause_button.setFixedWidth(150)
        self.pause_button.clicked.connect(self._on_pause_clicked)
        controls_layout.addWidget(self.pause_button)

        self.skip_button = QPushButton("⏩ Saltar al Final")
        self.skip_button.setStyleSheet("""
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
        self.skip_button.setFixedWidth(200)
        self.skip_button.clicked.connect(self._on_skip_clicked)
        controls_layout.addWidget(self.skip_button)

        layout.addLayout(controls_layout)

        # Información de estado
        self.status_label = QLabel("Esperando inicio de incubación...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #e8f8f5;
                color: #16a085;
                padding: 10px;
                border-left: 4px solid #1abc9c;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Configurar scroll area
        scroll_area.setWidget(central_container)

        # Layout principal del widget
        widget_layout = QVBoxLayout(self)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(scroll_area)

    def _on_start_clicked(self):
        """Inicia o reanuda la incubacion."""
        if not self.is_running:
            self.is_running = True
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.skip_button.setEnabled(True)

            interval = int(1000 / self.speed_multiplier)
            self.timer.start(interval)

            self.status_label.setText(
                f"Incubacion en progreso (Velocidad {self.speed_multiplier}x)..."
            )
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #d5f4e6;
                    color: #27ae60;
                    padding: 10px;
                    border-left: 4px solid #27ae60;
                    border-radius: 5px;
                    font-size: 12px;
                }
            """)

            self.incubation_resumed.emit()

    def _on_pause_clicked(self):
        """Pausa la incubacion."""
        if self.is_running:
            self.is_running = False
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)

            self.status_label.setText(
                "Incubacion pausada. Click en 'Iniciar' para continuar."
            )
            self.status_label.setStyleSheet("""
                QLabel {
                    background-color: #fdebd0;
                    color: #f39c12;
                    padding: 10px;
                    border-left: 4px solid #f39c12;
                    border-radius: 5px;
                    font-size: 12px;
                }
            """)

            self.incubation_paused.emit()

    def _on_skip_clicked(self):
        """Salta directamente al final (18 horas)."""
        self.timer.stop()
        self.current_hour = self.target_hours
        self._update_display()
        self._complete_incubation()

    def _on_speed_changed(self, multiplier: int):
        """Cambia la velocidad de simulacion."""
        self.speed_multiplier = multiplier

        if self.is_running:
            # Reiniciar timer con nuevo intervalo
            interval = int(1000 / multiplier)
            self.timer.start(interval)

            self.status_label.setText(
                f"Incubacion en progreso (Velocidad {multiplier}x)..."
            )

    def _advance_time(self):
        """Avanza el tiempo en 1 hora."""
        if self.current_hour < self.target_hours:
            self.current_hour += 1
            self._update_display()
            self.time_updated.emit(self.current_hour)

            if self.current_hour >= self.target_hours:
                self._complete_incubation()

    def _update_display(self):
        """Actualiza la visualizacion del tiempo."""
        # Formatear tiempo como HH:MM:SS
        hours = self.current_hour
        time_str = f"{hours:02d}:00:00"
        self.time_display.setText(time_str)

        # Actualizar barra de progreso
        self.progress_bar.setValue(self.current_hour)

        # Actualizar fase segun hora
        phase = self._get_current_phase(self.current_hour)
        self.phase_label.setText(f"Fase: {phase}")

    def _get_current_phase(self, hour: int) -> str:
        """Determina la fase de crecimiento segun la hora."""
        if hour < 4:
            return "Lag inicial (adaptacion bacteriana)"
        elif hour < 10:
            return "Fase exponencial (crecimiento activo)"
        elif hour < 16:
            return "Fase estacionaria (equilibrio)"
        else:
            return "Fase final (lectura proxima)"

    def _complete_incubation(self):
        """Completa la incubacion."""
        self.is_running = False
        self.is_completed = True
        self.timer.stop()

        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.skip_button.setEnabled(False)

        # Cambiar estilos a completado
        self.time_display.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                border: 3px solid #229954;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        self.status_label.setText("Incubacion completada! Procesando resultados...")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #d4edda;
                color: #155724;
                padding: 10px;
                border-left: 4px solid #28a745;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
        """)

        self.incubation_completed.emit()

    def reset(self):
        """Reinicia el widget a estado inicial."""
        self.timer.stop()
        self.current_hour = 0
        self.is_running = False
        self.is_completed = False

        self._update_display()

        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.skip_button.setEnabled(True)

        self.time_display.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: #2ecc71;
                border: 3px solid #34495e;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        self.status_label.setText("Esperando inicio de incubacion...")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #e8f8f5;
                color: #16a085;
                padding: 10px;
                border-left: 4px solid #1abc9c;
                border-radius: 5px;
                font-size: 12px;
            }
        """)

    def get_current_hour(self) -> int:
        """Retorna la hora actual de incubacion."""
        return self.current_hour

    def is_incubation_complete(self) -> bool:
        """Retorna si la incubacion esta completada."""
        return self.is_completed
