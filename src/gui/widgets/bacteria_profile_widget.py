"""
Widget Bacteria Profile - Generación de perfiles bacterianos

Widget para crear perfiles in-silico de Pseudomonas aeruginosa:
- Perfil wild-type (bacteria sensible, sin exposición previa)
- Perfil con resistencia adquirida (historial de antibióticos)

Autor: Sistema AST Simulator
Fecha: 14 de noviembre de 2025
"""

from typing import Optional, List
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QListWidget,
    QPushButton,
    QGroupBox,
    QButtonGroup,
    QMessageBox,
    QTextEdit,
)
from PyQt5.QtCore import pyqtSignal

from src.data.database import get_session
from src.data.models import BacteriaProfile as BacteriaProfileModel
from src.core.bacteria_profile_generator import (
    generate_wild_type,
    generate_from_history,
    BacteriaProfile,
)
from src.core.genotype_phenotype_calculator import GenotypePhenotypeCalculator


class BacteriaProfileWidget(QWidget):
    """
    Widget para generar perfiles bacterianos in-silico.

    Dos modos:
    1. Wild-type: Bacteria comunitaria sensible (sin mutaciones)
    2. Con resistencia: Bacteria expuesta a antibióticos (con mutaciones)

    Signals:
        profile_generated: Emitido cuando se genera un perfil exitosamente
            - bacteria_profile_id (int): ID en la base de datos
            - genotype (dict): Diccionario gen → estado
    """

    profile_generated = pyqtSignal(int, dict)  # ID, genotipo

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.session = get_session()
        self.available_antibiotics = [
            "Meropenem",
            "Imipenem",
            "Doripenem",
            "Ciprofloxacino",
            "Levofloxacino",
            "Ceftazidima",
            "Cefepime",
            "Piperacilina/Tazobactam",
            "Amikacina",
            "Tobramicina",
            "Colistina",
            "Aztreonam",
            "Ceftazidima/Avibactam",
            "Ceftolozano/Tazobactam",
        ]

        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)

        # === Título ===
        title_label = QLabel("🦠 Generar Perfil Bacteriano")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 3px;
            }
        """)
        layout.addWidget(title_label)

        # === Selección de tipo de perfil ===
        profile_type_group = QGroupBox("Tipo de Perfil")
        profile_type_layout = QVBoxLayout()

        self.profile_type_group = QButtonGroup()

        self.wildtype_radio = QRadioButton("🟢 Wild-type (Bacteria sensible)")
        self.wildtype_radio.setChecked(True)
        self.wildtype_radio.setToolTip(
            "Bacteria comunitaria sin exposición previa a antibióticos\n"
            "Todas las MICs en rango sensible"
        )
        self.profile_type_group.addButton(self.wildtype_radio, 1)
        profile_type_layout.addWidget(self.wildtype_radio)

        self.resistant_radio = QRadioButton("🔴 Con resistencia adquirida")
        self.resistant_radio.setToolTip(
            "Bacteria hospitalaria con exposición a antibióticos\n"
            "Genera mutaciones según historial de tratamientos"
        )
        self.profile_type_group.addButton(self.resistant_radio, 2)
        profile_type_layout.addWidget(self.resistant_radio)

        profile_type_group.setLayout(profile_type_layout)
        layout.addWidget(profile_type_group)

        # Conectar señal para habilitar/deshabilitar selector de antibióticos
        self.wildtype_radio.toggled.connect(self._on_profile_type_changed)

        # === Selector de antibióticos previos ===
        self.antibiotics_group = QGroupBox("Antibióticos Previos (Exposición)")
        antibiotics_layout = QVBoxLayout()

        help_label = QLabel(
            "Seleccione los antibióticos a los que fue expuesta la bacteria:"
        )
        help_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        antibiotics_layout.addWidget(help_label)

        self.antibiotics_list = QListWidget()
        self.antibiotics_list.setSelectionMode(QListWidget.MultiSelection)
        self.antibiotics_list.addItems(self.available_antibiotics)
        self.antibiotics_list.setMaximumHeight(120)
        antibiotics_layout.addWidget(self.antibiotics_list)

        self.antibiotics_group.setLayout(antibiotics_layout)
        self.antibiotics_group.setEnabled(False)  # Deshabilitado por defecto
        layout.addWidget(self.antibiotics_group)

        # === Botón generar ===
        button_layout = QHBoxLayout()

        self.generate_button = QPushButton("⚡ Generar Perfil")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.generate_button.clicked.connect(self._on_generate_clicked)
        button_layout.addWidget(self.generate_button)

        layout.addLayout(button_layout)

        # === Resumen del perfil generado ===
        summary_group = QGroupBox("📋 Perfil Actual")
        summary_layout = QVBoxLayout()

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setPlaceholderText("Ningún perfil generado aún...")
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        summary_layout.addWidget(self.summary_text)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        layout.addStretch()

    def _on_profile_type_changed(self, checked: bool):
        """Habilita/deshabilita selector de antibióticos según tipo de perfil."""
        # Si se selecciona wild-type, deshabilitar antibióticos
        self.antibiotics_group.setEnabled(not checked)

        # Limpiar selección si se cambia a wild-type
        if checked:
            self.antibiotics_list.clearSelection()

    def _on_generate_clicked(self):
        """Genera el perfil bacteriano según la configuración seleccionada."""
        try:
            # Determinar tipo de perfil
            if self.wildtype_radio.isChecked():
                # Generar wild-type
                profile = generate_wild_type()
                profile_type = "wild-type"
                antibioticos_previos = None

            else:
                # Generar con resistencia
                selected_items = self.antibiotics_list.selectedItems()

                if not selected_items:
                    QMessageBox.warning(
                        self,
                        "Sin antibióticos seleccionados",
                        "Debe seleccionar al menos un antibiótico para generar "
                        "un perfil con resistencia adquirida.",
                    )
                    return

                antibioticos_previos = [item.text() for item in selected_items]
                profile = generate_from_history(
                    antibioticos_previos=antibioticos_previos,
                    probabilidad_mutacion=0.7,
                )
                profile_type = "resistente"

            # Guardar perfil en base de datos
            bacteria_profile_id = self._save_profile_to_db(profile)

            # Mostrar resumen
            self._display_profile_summary(profile, profile_type, bacteria_profile_id)

            # Emitir señal
            self.profile_generated.emit(bacteria_profile_id, profile.genotipo)

            # Mensaje de éxito
            QMessageBox.information(
                self,
                "Perfil generado",
                f"Perfil bacteriano {profile_type} generado exitosamente.\n\n"
                f"ID en base de datos: {bacteria_profile_id}\n"
                f"Mutaciones: {len([g for g in profile.genotipo.values() if g not in ['wild-type', 'functional', 'basal', 'absent']])}\n\n"
                f"Ahora puede ejecutar la simulación AST.",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al generar perfil",
                f"Ocurrió un error al generar el perfil bacteriano:\n\n{str(e)}",
            )

    def _save_profile_to_db(self, profile: BacteriaProfile) -> int:
        """
        Guarda el perfil en la base de datos.

        Args:
            profile: Objeto BacteriaProfile a guardar

        Returns:
            ID del perfil en la base de datos
        """
        import json

        # Crear registro
        db_profile = BacteriaProfileModel(
            organismo=profile.organismo,
            genotipo=json.dumps(profile.genotipo),
            mics_calculated=json.dumps(profile.mics_calculated),
            escenario=profile.escenario,
            origen_muestra=profile.origen_muestra,
            antibioticos_previos=(
                json.dumps(profile.antibioticos_previos)
                if profile.antibioticos_previos
                else None
            ),
            mutaciones_aplicadas=(
                json.dumps(profile.mutaciones_aplicadas)
                if profile.mutaciones_aplicadas
                else None
            ),
        )

        # Guardar
        self.session.add(db_profile)
        self.session.commit()

        bacteria_profile_id = db_profile.id

        # Refrescar sesión
        self.session.refresh(db_profile)

        return bacteria_profile_id

    def _display_profile_summary(
        self, profile: BacteriaProfile, profile_type: str, profile_id: int
    ):
        """Muestra un resumen del perfil generado."""
        # Contar mutaciones
        mutations = [
            (gene, state)
            for gene, state in profile.genotipo.items()
            if state not in ["wild-type", "functional", "basal", "absent"]
        ]

        # Generar texto de resumen
        summary_lines = [
            f"═══════════════════════════════════════════",
            f"PERFIL BACTERIANO ID: {profile_id}",
            f"═══════════════════════════════════════════",
            f"Tipo: {profile_type.upper()}",
            f"Organismo: {profile.organismo}",
            f"Escenario: {profile.escenario}",
            f"",
            f"GENOTIPO:",
        ]

        if mutations:
            summary_lines.append(f"  Mutaciones detectadas: {len(mutations)}")
            for gene, state in mutations:
                summary_lines.append(f"    • {gene}: {state}")
        else:
            summary_lines.append("  Sin mutaciones (wild-type)")

        summary_lines.append("")
        summary_lines.append(f"MICs CALCULADOS (primeros 5):")

        for i, (abx, mic) in enumerate(list(profile.mics_calculated.items())[:5]):
            summary_lines.append(f"  {abx}: {mic:.3f} µg/mL")
            if i >= 4:
                break

        if len(profile.mics_calculated) > 5:
            summary_lines.append(f"  ... ({len(profile.mics_calculated) - 5} más)")

        summary_lines.append(f"═══════════════════════════════════════════")

        # Mostrar en el widget
        self.summary_text.setText("\n".join(summary_lines))
