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
    QSizePolicy,
    QProgressBar,
)
from PyQt5.QtCore import pyqtSignal, QThread, QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from src.data.database import get_session
from src.data.models import BacteriaProfile as BacteriaProfileModel
from src.core.bacteria_profile_generator import (
    generate_wild_type,
    generate_from_history,
    BacteriaProfile,
)
from src.core.genotype_phenotype_calculator import GenotypePhenotypeCalculator


class ProfileGenerationThread(QThread):
    """Hilo para generación de perfiles bacterianos en segundo plano."""
    profile_generated = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)  # Nueva señal para progreso
    
    def __init__(self, profile_type, antibiotics=None):
        super().__init__()
        self.profile_type = profile_type
        self.antibiotics = antibiotics
    
    def run(self):
        try:
            # Simular progreso inicial
            self.progress_updated.emit(10)
            
            if self.profile_type == "wild-type":
                # Simular progreso durante generación wild-type
                self.progress_updated.emit(30)
                profile = generate_wild_type()
                self.progress_updated.emit(70)
            else:
                # Simular progreso durante generación con resistencia
                self.progress_updated.emit(20)
                profile = generate_from_history(self.antibiotics)
                self.progress_updated.emit(60)
            
            # Simular cálculo final de MICs
            self.progress_updated.emit(90)
            
            # Pequeña pausa para simular procesamiento final
            self.msleep(200)
            self.progress_updated.emit(100)
            
            self.profile_generated.emit(profile)
        except Exception as e:
            self.error_occurred.emit(str(e))


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
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # Alinear todo a la izquierda

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
        title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(title_label)

        # === Contenedor principal con columnas ===
        columns_container = QHBoxLayout()
        columns_container.setSpacing(20)
        columns_container.setAlignment(Qt.AlignLeft)  # Alinear columnas a la izquierda

        # === COLUMNA 1: Tipo de perfil ===
        profile_column = QVBoxLayout()
        profile_column.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        profile_type_group = QGroupBox("Tipo de Perfil")
        profile_type_group.setFixedHeight(200)  # ALTURA AUMENTADA
        profile_type_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        profile_type_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                min-width: 300px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #3498db;
            }
        """)
        profile_type_layout = QVBoxLayout()
        profile_type_layout.setAlignment(Qt.AlignLeft)

        self.profile_type_group = QButtonGroup()

        self.wildtype_radio = QRadioButton("🟢 Wild-type (Bacteria sensible)")
        self.wildtype_radio.setChecked(True)
        self.wildtype_radio.setToolTip(
            "Bacteria comunitaria sin exposición previa a antibióticos\n"
            "Todas las MICs en rango sensible"
        )
        self.wildtype_radio.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.profile_type_group.addButton(self.wildtype_radio, 1)
        profile_type_layout.addWidget(self.wildtype_radio)

        self.resistant_radio = QRadioButton("🔴 Con resistencia adquirida")
        self.resistant_radio.setToolTip(
            "Bacteria hospitalaria con exposición a antibióticos\n"
            "Genera mutaciones según historial de tratamientos"
        )
        self.resistant_radio.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.profile_type_group.addButton(self.resistant_radio, 2)
        profile_type_layout.addWidget(self.resistant_radio)

        # Agregar más espacio entre los radio buttons
        profile_type_layout.addSpacing(10)

        # Agregar espacio flexible para empujar el contenido hacia arriba
        profile_type_layout.addStretch()

        profile_type_group.setLayout(profile_type_layout)
        profile_column.addWidget(profile_type_group)

        # === COLUMNA 2: Antibióticos previos ===
        antibiotics_column = QVBoxLayout()
        antibiotics_column.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.antibiotics_group = QGroupBox("Antibióticos Previos (Exposición)")
        self.antibiotics_group.setFixedHeight(200)  # ALTURA AUMENTADA
        self.antibiotics_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.antibiotics_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                min-width: 300px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #27ae60;
            }
        """)
        antibiotics_layout = QVBoxLayout()
        antibiotics_layout.setAlignment(Qt.AlignLeft)

        # Mensaje informativo para Wild-type
        self.info_label = QLabel(
            "🟢 <b>Perfil Wild-type seleccionado</b><br>"
            "<span style='color: #7f8c8d; font-size: 10px;'>"
            "No se requieren antibióticos previos para bacteria sensible"
            "</span>"
        )
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: #d5f4e6;
                color: #27ae60;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #27ae60;
                font-size: 11px;
                min-width: 270px;
                max-height: 80px; 
            }
        """)
        self.info_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        antibiotics_layout.addWidget(self.info_label)

        # Lista de antibióticos (inicialmente oculta)
        self.antibiotics_list = QListWidget()
        self.antibiotics_list.setSelectionMode(QListWidget.MultiSelection)
        self.antibiotics_list.addItems(self.available_antibiotics)
        self.antibiotics_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.antibiotics_list.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.antibiotics_list.setVisible(False)
        self.antibiotics_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                min-width: 270px;
                max-height: 140px;  
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
                font-size: 11px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        antibiotics_layout.addWidget(self.antibiotics_list)

        self.antibiotics_group.setLayout(antibiotics_layout)
        antibiotics_column.addWidget(self.antibiotics_group)

        # Agregar ambas columnas al contenedor principal
        columns_container.addLayout(profile_column)
        columns_container.addLayout(antibiotics_column)
        columns_container.addStretch()

        # Agregar el contenedor de columnas al layout principal
        layout.addLayout(columns_container)

        # === FILA DE BOTÓN Y BARRA DE CARGA ===
        button_progress_container = QHBoxLayout()
        button_progress_container.setSpacing(20)
        button_progress_container.setAlignment(Qt.AlignLeft)

        # === BOTÓN GENERAR (mismo ancho que Tipo de Perfil) ===
        self.generate_button = QPushButton("⚡ Generar Perfil")
        self.generate_button.setFixedWidth(300)  # Mismo ancho que el groupbox de Tipo de Perfil
        self.generate_button.setFixedHeight(40)  # Altura consistente
        self.generate_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.generate_button.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #1e8449;  
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.generate_button.clicked.connect(self._on_generate_clicked)
        button_progress_container.addWidget(self.generate_button)

        # === BARRA DE CARGA (mismo tamaño que Antibióticos Previos) - SIEMPRE VISIBLE ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(520)  # Mismo ancho que el groupbox de Antibióticos Previos
        self.progress_bar.setFixedHeight(40)  # Misma altura que el botón
        self.progress_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.progress_bar.setVisible(True)  # SIEMPRE VISIBLE
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
        self.progress_bar.setValue(0)  # Inicia en 0%
        self.progress_bar.setFormat("0% - Listo")
        button_progress_container.addWidget(self.progress_bar)

        # Agregar stretch para alinear a la izquierda
        button_progress_container.addStretch()

        # Agregar el contenedor de botón y barra al layout principal
        layout.addLayout(button_progress_container)

        # === Resumen del perfil generado ===
        summary_group = QGroupBox("📋 Perfil Actual")
        summary_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        summary_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                min-width: 620px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #9b59b6;
            }
        """)
        summary_layout = QVBoxLayout()
        summary_layout.setAlignment(Qt.AlignLeft)

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
                font-size: 12px;
                min-width: 630px;
            }
        """)
        self.summary_text.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        summary_layout.addWidget(self.summary_text)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        layout.addStretch()

        # Conectar señal para habilitar/deshabilitar selector de antibióticos
        self.wildtype_radio.toggled.connect(self._on_profile_type_changed)

    def _on_profile_type_changed(self, checked: bool):
        """Habilita/deshabilita selector de antibióticos según tipo de perfil."""
        if checked:  # Wild-type seleccionado
            # Mostrar mensaje informativo
            self.info_label.setText(
                "🟢 <b>Perfil Wild-type seleccionado</b><br>"
                "<span style='color: #7f8c8d; font-size: 10px;'>"
                "No se requieren antibióticos previos para bacteria sensible"
                "</span>"
            )
            self.info_label.setStyleSheet("""
                QLabel {
                    background-color: #d5f4e6;
                    color: #27ae60;
                    padding: 15px;
                    border-radius: 5px;
                    border: 1px solid #27ae60;
                    font-size: 11px;
                    min-width: 270px;
                    max-height: 80px;
                }
            """)
            self.info_label.setVisible(True)
            
            # Ocultar lista de antibióticos
            self.antibiotics_list.setVisible(False)
            self.antibiotics_list.clearSelection()
            
        else:  # Con resistencia adquirida seleccionado
            # Mostrar mensaje diferente
            self.info_label.setText(
                "🔴 <b>Perfil con Resistencia Adquirida</b><br>"
                "<span style='color: #7f8c8d; font-size: 10px;'>"
                "Seleccione los antibióticos a los que fue expuesta la bacteria"
                "</span>"
            )
            self.info_label.setStyleSheet("""
                QLabel {
                    background-color: #fdeaea;
                    color: #e74c3c;
                    padding: 15px;
                    border-radius: 5px;
                    border: 1px solid #e74c3c;
                    font-size: 11px;
                    min-width: 270px;
                    max-height: 80px;
                }
            """)
            self.info_label.setVisible(True)
            
            # Mostrar lista de antibióticos
            self.antibiotics_list.setVisible(True)

    def _on_generate_clicked(self):
        """Genera el perfil bacteriano según la configuración seleccionada."""
        try:
            # Validar selección para perfil resistente
            if self.resistant_radio.isChecked():
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
            else:
                antibioticos_previos = None

            # Resetear barra de progreso a 0% para nueva generación
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("0% - Iniciando...")
            self.generate_button.setEnabled(False)
            
            # Forzar actualización de la UI
            QApplication.processEvents()

            # Determinar tipo de perfil y configurar hilo
            if self.wildtype_radio.isChecked():
                self.thread = ProfileGenerationThread("wild-type")
            else:
                self.thread = ProfileGenerationThread("resistant", antibioticos_previos)

            # Conectar señales del hilo
            self.thread.profile_generated.connect(self._on_profile_generated)
            self.thread.error_occurred.connect(self._on_generation_error)
            self.thread.progress_updated.connect(self._on_progress_updated)

            # Iniciar generación en segundo plano
            self.thread.start()

        except Exception as e:
            self._reset_ui_after_error()
            QMessageBox.critical(
                self,
                "Error al generar perfil",
                f"Ocurrió un error al generar el perfil bacteriano:\n\n{str(e)}",
            )

    def _on_progress_updated(self, progress_value: int):
        """Actualiza la barra de progreso con el valor recibido."""
        self.progress_bar.setValue(progress_value)
        self.progress_bar.setFormat(f"{progress_value}% - Procesando...")
        QApplication.processEvents()

    def _on_profile_generated(self, profile: BacteriaProfile):
        """Maneja la finalización exitosa de la generación del perfil."""
        try:
            # Asegurar que la barra muestre 100%
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("100%")
            
            # Habilitar el botón para nueva generación
            self.generate_button.setEnabled(True)

            # Determinar tipo de perfil para el resumen
            profile_type = "wild-type" if self.wildtype_radio.isChecked() else "resistente"

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
            self._reset_ui_after_error()
            QMessageBox.critical(
                self,
                "Error al guardar perfil",
                f"Ocurrió un error al guardar el perfil bacteriano:\n\n{str(e)}",
            )

    def _on_generation_error(self, error_msg: str):
        """Maneja errores durante la generación del perfil."""
        self._reset_ui_after_error()
        QMessageBox.critical(
            self,
            "Error al generar perfil",
            f"Ocurrió un error al generar el perfil bacteriano:\n\n{error_msg}",
        )

    def _reset_ui_after_error(self):
        """Resetea la UI después de un error."""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0% - Listo")
        self.generate_button.setEnabled(True)
        QApplication.processEvents()

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