"""
Widget Bacteria Identification - Simulación de identificación bacteriana

Simula el proceso de identificación de Pseudomonas aeruginosa siguiendo
el flujo clínico real de microbiología:

1. Origen de la muestra
2. Cultivo en agar MacConkey
3. Pruebas bioquímicas (Oxidasa, Lactosa)
4. Características fenotípicas (Pigmento, Olor, Motilidad)
5. Pruebas adicionales (Crecimiento 42°C)

Este paso es PREVIO al AST y simula la decisión diagnóstica real.

Autor: Sistema AST Simulator
Fecha: 17 de noviembre de 2025
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QGroupBox,
    QCheckBox,
    QTextEdit,
    QProgressBar,
)
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QFont


class BacteriaIdentificationWidget(QWidget):
    """
    Widget para simular identificación bacteriana de Pseudomonas aeruginosa.

    Simula el proceso diagnóstico que precede al AST:
    - Selección de origen de muestra
    - Cultivo en medios selectivos
    - Pruebas bioquímicas
    - Identificación fenotípica

    Signals:
        identification_completed: Emitido cuando se confirma P. aeruginosa
            - organism (str): "Pseudomonas aeruginosa"
            - sample_origin (str): Origen de la muestra
            - confidence (float): Confianza en identificación (0.0-1.0)
    """

    identification_completed = pyqtSignal(
        str, str, float
    )  # organism, origin, confidence

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.current_sample_origin = None
        self.test_results = {}

        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # === TÍTULO ===
        title_label = QLabel("🔬 Identificación Bacteriana")
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

        # === INFORMACIÓN CLÍNICA ===
        info_label = QLabel(
            "⚕️ <b>Flujo clínico:</b> Antes de realizar AST, debe identificarse el organismo mediante "
            "cultivo en medios selectivos y pruebas bioquímicas."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            QLabel {
                background-color: #e8f4f8;
                color: #2c3e50;
                padding: 10px;
                border-left: 4px solid #3498db;
                border-radius: 3px;
                font-size: 11px;
            }
        """)
        layout.addWidget(info_label)

        # === PASO 1: ORIGEN DE MUESTRA ===
        sample_group = QGroupBox("📋 Paso 1: Origen de la Muestra")
        sample_group.setStyleSheet("""
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
        sample_layout = QVBoxLayout()

        sample_desc = QLabel("Seleccione el tipo de muestra clínica:")
        sample_desc.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        sample_layout.addWidget(sample_desc)

        self.sample_combo = QComboBox()
        self.sample_combo.addItems(
            [
                "-- Seleccione origen --",
                "🩸 Hemocultivo (sangre)",
                "🫁 Esputo (tracto respiratorio)",
                "💧 Orina (urocultivo)",
                "🦴 Líquido sinovial (articulación)",
                "🧪 Punta de catéter",
                "🩹 Exudado de herida",
                "🧠 Líquido cefalorraquídeo (LCR)",
            ]
        )
        self.sample_combo.setStyleSheet("""
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
        self.sample_combo.currentTextChanged.connect(self._on_sample_changed)
        sample_layout.addWidget(self.sample_combo)

        sample_group.setLayout(sample_layout)
        layout.addWidget(sample_group)

        # === PASO 2: CULTIVO Y PRUEBAS ===
        self.tests_group = QGroupBox(
            "🧫 Paso 2: Cultivo en MacConkey y Pruebas Bioquímicas"
        )
        self.tests_group.setEnabled(False)
        self.tests_group.setStyleSheet("""
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
                padding: 0 5px;
                color: #27ae60;
            }
        """)
        tests_layout = QVBoxLayout()

        # Botón ejecutar pruebas
        self.run_tests_btn = QPushButton(
            "▶ Ejecutar Cultivo y Pruebas de Identificación"
        )
        self.run_tests_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 13px;
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
        self.run_tests_btn.clicked.connect(self._run_identification_tests)
        tests_layout.addWidget(self.run_tests_btn)

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
                background-color: #27ae60;
            }
        """)
        tests_layout.addWidget(self.progress_bar)

        # Área de resultados
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(250)
        self.results_text.setPlaceholderText(
            "Los resultados de las pruebas aparecerán aquí..."
        )
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        tests_layout.addWidget(self.results_text)

        self.tests_group.setLayout(tests_layout)
        layout.addWidget(self.tests_group)

        # === PASO 3: CONFIRMACIÓN ===
        self.confirm_group = QGroupBox("✅ Paso 3: Confirmación de Identificación")
        self.confirm_group.setEnabled(False)
        self.confirm_group.setStyleSheet("""
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
                padding: 0 5px;
                color: #9b59b6;
            }
        """)
        confirm_layout = QVBoxLayout()

        self.identification_label = QLabel("")
        self.identification_label.setStyleSheet("""
            QLabel {
                background-color: #d5f4e6;
                color: #27ae60;
                padding: 12px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        self.identification_label.setVisible(False)
        confirm_layout.addWidget(self.identification_label)

        self.confirm_btn = QPushButton(
            "✓ Confirmar Identificación y Continuar a Perfil Bacteriano"
        )
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.confirm_btn.clicked.connect(self._confirm_identification)
        confirm_layout.addWidget(self.confirm_btn)

        self.confirm_group.setLayout(confirm_layout)
        layout.addWidget(self.confirm_group)

        layout.addStretch()

    def _on_sample_changed(self, sample_text: str):
        """Maneja cambio en selección de muestra."""
        if sample_text.startswith("--"):
            self.tests_group.setEnabled(False)
            self.current_sample_origin = None
        else:
            self.tests_group.setEnabled(True)
            # Extraer nombre limpio (quitar emoji)
            self.current_sample_origin = (
                sample_text.split(" ", 1)[1] if " " in sample_text else sample_text
            )

            # Limpiar resultados previos
            self.results_text.clear()
            self.confirm_group.setEnabled(False)
            self.identification_label.setVisible(False)

    def _run_identification_tests(self):
        """Ejecuta la simulación de pruebas de identificación."""
        self.run_tests_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_text.clear()

        # Simular proceso secuencial con timer
        self.test_step = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._simulate_test_step)
        self.timer.start(800)  # 800ms por paso

    def _simulate_test_step(self):
        """Simula cada paso del proceso de identificación."""
        steps = [
            (10, "🧫 Inoculación en agar MacConkey...", self._test_macconkey),
            (25, "⏱️ Incubación 24h a 37°C...", self._test_incubation),
            (40, "🔍 Observación de colonias...", self._test_colony_morphology),
            (55, "🧪 Prueba de Oxidasa...", self._test_oxidase),
            (70, "🍬 Prueba de Lactosa...", self._test_lactose),
            (85, "🎨 Observación de pigmento...", self._test_pigment),
            (92, "👃 Prueba de olor...", self._test_odor),
            (96, "🌡️ Crecimiento a 42°C...", self._test_42c),
            (100, "✅ Análisis de resultados...", self._analyze_results),
        ]

        if self.test_step < len(steps):
            progress, message, test_func = steps[self.test_step]
            self.progress_bar.setValue(progress)
            self.results_text.append(f"\n{message}")

            # Ejecutar prueba
            result = test_func()
            if result:
                self.results_text.append(f"   → {result}")

            self.test_step += 1
        else:
            # Finalizar
            self.timer.stop()
            self.run_tests_btn.setEnabled(True)
            self.progress_bar.setVisible(False)

    def _test_macconkey(self) -> str:
        """Simula cultivo en MacConkey."""
        self.test_results["macconkey"] = True
        return "✓ Crecimiento en MacConkey: POSITIVO"

    def _test_incubation(self) -> str:
        """Simula incubación."""
        return "✓ Colonias visibles tras incubación"

    def _test_colony_morphology(self) -> str:
        """Simula observación de colonias."""
        self.test_results["morphology"] = "incoloras"
        return "✓ Morfología: Colonias INCOLORAS (lactosa negativa)"

    def _test_oxidase(self) -> str:
        """Simula prueba de oxidasa."""
        self.test_results["oxidase"] = "positiva"
        return "✓ Oxidasa: POSITIVA (coloración púrpura)"

    def _test_lactose(self) -> str:
        """Simula prueba de lactosa."""
        self.test_results["lactose"] = "negativa"
        return "✓ Lactosa: NEGATIVA (no fermenta)"

    def _test_pigment(self) -> str:
        """Simula observación de pigmento."""
        self.test_results["pigment"] = "pioverdina"
        return "✓ Pigmento: PIOVERDINA (fluorescencia verde-amarilla)"

    def _test_odor(self) -> str:
        """Simula prueba de olor."""
        self.test_results["odor"] = "uva"
        return "✓ Olor característico: UVA/dulce (2-aminoacetofenona)"

    def _test_42c(self) -> str:
        """Simula crecimiento a 42°C."""
        self.test_results["growth_42c"] = True
        return "✓ Crecimiento a 42°C: POSITIVO"

    def _analyze_results(self) -> str:
        """Analiza resultados y determina identificación."""
        # Calcular confianza basada en pruebas positivas
        criteria_met = 0
        total_criteria = 6

        if self.test_results.get("macconkey"):
            criteria_met += 1
        if self.test_results.get("oxidase") == "positiva":
            criteria_met += 1
        if self.test_results.get("lactose") == "negativa":
            criteria_met += 1
        if self.test_results.get("pigment") == "pioverdina":
            criteria_met += 1
        if self.test_results.get("odor") == "uva":
            criteria_met += 1
        if self.test_results.get("growth_42c"):
            criteria_met += 1

        confidence = (criteria_met / total_criteria) * 100

        # Mostrar conclusión
        self.results_text.append("\n" + "=" * 60)
        self.results_text.append("📊 CONCLUSIÓN:")
        self.results_text.append(
            f"   Criterios cumplidos: {criteria_met}/{total_criteria}"
        )
        self.results_text.append(f"   Confianza: {confidence:.1f}%")

        if confidence >= 80:
            self.results_text.append(
                "\n✅ IDENTIFICACIÓN CONFIRMADA: Pseudomonas aeruginosa"
            )
            self.results_text.append("   (Bacilo Gram-negativo, no fermentador)")

            # Habilitar confirmación
            self.confirm_group.setEnabled(True)
            self.identification_label.setText(
                f"🦠 Organismo identificado: Pseudomonas aeruginosa (Confianza: {confidence:.1f}%)"
            )
            self.identification_label.setVisible(True)

            return f"✓ Identificación exitosa ({confidence:.1f}% confianza)"
        else:
            self.results_text.append("\n⚠️ IDENTIFICACIÓN INCOMPLETA")
            self.results_text.append("   Se requieren pruebas adicionales")
            return "⚠️ Confianza insuficiente - pruebas adicionales requeridas"

    def _confirm_identification(self):
        """Confirma la identificación y emite señal."""
        confidence = len([v for v in self.test_results.values() if v]) / 6.0

        self.identification_completed.emit(
            "Pseudomonas aeruginosa", self.current_sample_origin, confidence
        )

        # Mostrar mensaje de éxito
        from PyQt5.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Identificación Confirmada",
            f"✅ Organismo: Pseudomonas aeruginosa\n"
            f"📋 Muestra: {self.current_sample_origin}\n"
            f"📊 Confianza: {confidence * 100:.1f}%\n\n"
            f"Puede proceder a generar el perfil bacteriano.",
        )

    def reset(self):
        """Reinicia el widget a estado inicial."""
        self.sample_combo.setCurrentIndex(0)
        self.results_text.clear()
        self.test_results = {}
        self.tests_group.setEnabled(False)
        self.confirm_group.setEnabled(False)
        self.identification_label.setVisible(False)
        self.current_sample_origin = None
