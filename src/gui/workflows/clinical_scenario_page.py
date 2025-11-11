"""
Pagina de wizard para configuracion de escenario clinico.

Define el contexto del paciente y genera el perfil bacteriano inicial
antes de ejecutar el antibiograma simulado.

Autor: Sistema SRB
Fecha: 11 de noviembre de 2025
"""

from PyQt5.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QRadioButton,
    QCheckBox,
    QPushButton,
    QTextEdit,
    QGroupBox,
    QButtonGroup,
    QScrollArea,
    QWidget,
    QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from typing import Optional

from src.core.bacteria_profile_generator import (
    generate_wild_type,
    generate_from_history,
    format_profile_summary,
    BacteriaProfile,
)


class ClinicalScenarioPage(QWizardPage):
    """
    Primera pagina del wizard AST: configuracion de escenario clinico.

    Permite al usuario:
    - Seleccionar origen de muestra
    - Elegir contexto del paciente (comunitario/hospitalizado)
    - Especificar antibioticos previos (si aplica)
    - Generar perfil bacteriano in-silico
    """

    profile_generated = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Paso 1: Escenario Clinico")
        self.setSubTitle(
            "Configure el contexto del paciente para generar el perfil bacteriano inicial"
        )

        self.bacteria_profile: Optional[BacteriaProfile] = None
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Construye la interfaz grafica."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Seccion 1: Origen de muestra
        self.create_sample_origin_section(layout)

        # Seccion 2: Contexto del paciente
        self.create_patient_context_section(layout)

        # Seccion 3: Antibioticos previos (condicional)
        self.create_antibiotic_history_section(layout)

        # Boton de generacion
        self.create_generate_button(layout)

        # Seccion 4: Resultado (genotipo generado)
        self.create_result_section(layout)

        layout.addStretch()

    def create_sample_origin_section(self, parent_layout):
        """Crea seccion de seleccion de origen de muestra."""
        group = QGroupBox("Origen de muestra")
        layout = QVBoxLayout(group)

        label = QLabel("Tipo de muestra clinica:")
        label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(label)

        self.sample_origin_combo = QComboBox()
        self.sample_origin_combo.addItems(
            ["Hemocultivo", "Esputo", "Orina", "Herida", "Cateter"]
        )
        self.sample_origin_combo.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.sample_origin_combo)

        info_label = QLabel(
            "Nota: El origen de muestra es informativo. "
            "La bacteria ya fue identificada como Pseudomonas aeruginosa."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #555; font-size: 9pt;")
        layout.addWidget(info_label)

        parent_layout.addWidget(group)

    def create_patient_context_section(self, parent_layout):
        """Crea seccion de contexto del paciente (comunitario/hospitalizado)."""
        group = QGroupBox("Contexto del paciente")
        layout = QVBoxLayout(group)

        self.context_button_group = QButtonGroup(self)

        self.community_radio = QRadioButton("Comunitario (bacteria sensible estandar)")
        self.community_radio.setFont(QFont("Segoe UI", 10))
        self.community_radio.setChecked(True)
        self.context_button_group.addButton(self.community_radio, 0)
        layout.addWidget(self.community_radio)

        desc_community = QLabel(
            "   Paciente ambulatorio sin tratamientos antibioticos previos. "
            "Bacteria con genotipo wild-type."
        )
        desc_community.setWordWrap(True)
        desc_community.setStyleSheet("color: #666; font-size: 9pt; margin-left: 20px;")
        layout.addWidget(desc_community)

        layout.addSpacing(10)

        self.hospital_radio = QRadioButton("Hospitalizado (tratado previamente)")
        self.hospital_radio.setFont(QFont("Segoe UI", 10))
        self.context_button_group.addButton(self.hospital_radio, 1)
        layout.addWidget(self.hospital_radio)

        desc_hospital = QLabel(
            "   Paciente con exposicion previa a antibioticos. "
            "Bacteria puede tener resistencias adquiridas."
        )
        desc_hospital.setWordWrap(True)
        desc_hospital.setStyleSheet("color: #666; font-size: 9pt; margin-left: 20px;")
        layout.addWidget(desc_hospital)

        parent_layout.addWidget(group)

    def create_antibiotic_history_section(self, parent_layout):
        """Crea seccion de historial de antibioticos (solo para hospitalizados)."""
        self.antibiotic_history_group = QGroupBox("Antibioticos previos")
        self.antibiotic_history_group.setEnabled(False)

        layout = QVBoxLayout(self.antibiotic_history_group)

        info = QLabel("Seleccione los antibioticos usados en tratamientos anteriores:")
        info.setFont(QFont("Segoe UI", 9))
        layout.addWidget(info)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(150)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(5, 5, 5, 5)

        # Lista de antibioticos comunes en P. aeruginosa
        antibiotics = [
            "Ciprofloxacino",
            "Levofloxacino",
            "Meropenem",
            "Imipenem",
            "Ceftazidima",
            "Cefepime",
            "Piperacilina/Tazobactam",
            "Amikacina",
            "Tobramicina",
            "Colistina",
        ]

        self.antibiotic_checkboxes = {}
        for antibiotic in antibiotics:
            cb = QCheckBox(antibiotic)
            cb.setFont(QFont("Segoe UI", 9))
            self.antibiotic_checkboxes[antibiotic] = cb
            scroll_layout.addWidget(cb)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        parent_layout.addWidget(self.antibiotic_history_group)

    def create_generate_button(self, parent_layout):
        """Crea boton para generar perfil bacteriano."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.generate_button = QPushButton("Generar Bacteria")
        self.generate_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.generate_button.setFixedHeight(40)
        self.generate_button.setFixedWidth(200)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """)
        self.generate_button.clicked.connect(self.on_generate_clicked)

        button_layout.addWidget(self.generate_button)
        button_layout.addStretch()

        parent_layout.addLayout(button_layout)

    def create_result_section(self, parent_layout):
        """Crea seccion para mostrar el perfil bacteriano generado."""
        group = QGroupBox("Perfil bacteriano generado")
        layout = QVBoxLayout(group)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 9))
        self.result_text.setMaximumHeight(180)
        self.result_text.setPlaceholderText(
            "El perfil bacteriano aparecera aqui una vez generado..."
        )
        layout.addWidget(self.result_text)

        parent_layout.addWidget(group)

    def connect_signals(self):
        """Conecta senales de la interfaz."""
        self.hospital_radio.toggled.connect(self.on_context_changed)

    def on_context_changed(self, checked: bool):
        """Habilita/deshabilita seccion de antibioticos previos."""
        self.antibiotic_history_group.setEnabled(checked)

        if not checked:
            for cb in self.antibiotic_checkboxes.values():
                cb.setChecked(False)

    def on_generate_clicked(self):
        """Genera el perfil bacteriano segun la configuracion del usuario."""
        try:
            if self.community_radio.isChecked():
                self.bacteria_profile = generate_wild_type()
            else:
                selected_antibiotics = [
                    name
                    for name, cb in self.antibiotic_checkboxes.items()
                    if cb.isChecked()
                ]

                if not selected_antibiotics:
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        "Debe seleccionar al menos un antibiotico previo "
                        "para generar bacteria hospitalaria.",
                    )
                    return

                self.bacteria_profile = generate_from_history(selected_antibiotics)

            summary = format_profile_summary(self.bacteria_profile)
            self.result_text.setPlainText(summary)

            self.profile_generated.emit(self.bacteria_profile)

            self.completeChanged.emit()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error al generar perfil bacteriano:\n{str(e)}"
            )

    def isComplete(self):
        """Verifica si la pagina esta completa para avanzar al siguiente paso."""
        return self.bacteria_profile is not None

    def get_sample_origin(self) -> str:
        """Retorna el origen de muestra seleccionado."""
        return self.sample_origin_combo.currentText()

    def get_bacteria_profile(self) -> Optional[BacteriaProfile]:
        """Retorna el perfil bacteriano generado."""
        return self.bacteria_profile
