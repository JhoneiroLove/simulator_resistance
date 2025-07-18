import logging
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QMessageBox,
    QGroupBox,
    QScrollArea,
    QFrame,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QToolTip,
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from types import SimpleNamespace

from src.data.database import get_session
from src.data.models import Gen

class InputForm(QWidget):
    params_submitted = pyqtSignal(list, str, float, float, int, dict, float)  

    def __init__(self):
        super().__init__()
        self.session = get_session()

        # Layout principal con márgenes y espaciado
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(32, 32, 32, 32)
        self.main_layout.setSpacing(28)
        QToolTip.setFont(QFont("Segoe UI", 10))

        # Construcción de la UI
        self.load_data()
        self.create_gene_selection()
        self.create_simulation_params()
        self.create_environmental_params()

        # Botón Guardar parámetros
        self.save_button = QPushButton("Guardar parámetros")
        self.save_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.save_button.setFixedHeight(38)
        self.save_button.clicked.connect(self.submit)
        self.main_layout.addWidget(self.save_button, alignment=Qt.AlignHCenter)
        self.main_layout.addStretch()


    def load_data(self):
        """Carga genes como estructuras planas."""
        genes_q = self.session.query(Gen.id, Gen.nombre, Gen.descripcion).all()
        self.genes = [
            SimpleNamespace(id=g[0], nombre=g[1], descripcion=g[2]) for g in genes_q
        ]

    def create_gene_selection(self):
        grp = QGroupBox("1. Selección de Genes")
        layout = QVBoxLayout(grp)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        cont = QWidget()
        cont_l = QVBoxLayout(cont)
        cont_l.setContentsMargins(5, 5, 5, 5)
        cont_l.setSpacing(5)
        self.checks = {}
        for g in self.genes:
            cb = QCheckBox(f"{g.nombre} ({g.descripcion})")
            self.checks[g.id] = cb
            cont_l.addWidget(cb)
        cont_l.addStretch()
        scroll.setWidget(cont)
        layout.addWidget(scroll)
        grp.setLayout(layout)
        self.main_layout.addWidget(grp)

    def create_simulation_params(self):
        grp = QGroupBox("2. Parámetros de Simulación")
        form = QFormLayout(grp)
        form.setContentsMargins(10, 10, 10, 10)
        form.setHorizontalSpacing(15)
        form.setVerticalSpacing(10)

        # Unidad de tiempo (fija)
        label_unit = QLabel("Generaciones")
        label_unit.setEnabled(False)
        form.addRow("Unidad de tiempo:", label_unit)

        # Duración total
        self.time_horizon_sb = QSpinBox()
        self.time_horizon_sb.setRange(10, 10000)
        self.time_horizon_sb.setValue(100)
        form.addRow("Duración total (max 10000 / min 10):", self.time_horizon_sb)

        # Tasa de mutación
        self.mut_rate_sb = QDoubleSpinBox()
        self.mut_rate_sb.setRange(0.05, 1.0)
        self.mut_rate_sb.setSingleStep(0.01)
        self.mut_rate_sb.setValue(0.05)
        form.addRow("Tasa mutación (max 1.00 / min 0.05):", self.mut_rate_sb)
        tooltip_mut = (
            "Probabilidad de que ocurra una mutación genética en cada generación, "
            "impulsando la variabilidad genética."
        )
        self.mut_rate_sb.setToolTip(tooltip_mut)
        self.mut_rate_sb.setToolTipDuration(5000)
        self.mut_rate_sb.setMouseTracking(True)
        label_mut = form.labelForField(self.mut_rate_sb)
        if label_mut:
            label_mut.setToolTip(tooltip_mut)

        # Tasa de mortalidad
        self.death_rate_sb = QDoubleSpinBox()
        self.death_rate_sb.setRange(0.03, 1.0)
        self.death_rate_sb.setSingleStep(0.01)
        self.death_rate_sb.setValue(0.05)
        form.addRow("Tasa mortalidad (max 1.00 / min 0.03):", self.death_rate_sb)
        tooltip_death = (
            "Probabilidad de que un individuo muera en cada generación, "
            "reflejando la eficacia del tratamiento o condiciones adversas."
        )
        self.death_rate_sb.setToolTip(tooltip_death)
        self.death_rate_sb.setToolTipDuration(5000)
        self.death_rate_sb.setMouseTracking(True)
        label_death = form.labelForField(self.death_rate_sb)
        if label_death:
            label_death.setToolTip(tooltip_death)

        # Tasa de reproducción 
        self.repro_rate_sb = QDoubleSpinBox()
        self.repro_rate_sb.setRange(0.01, 5.0)
        self.repro_rate_sb.setSingleStep(0.01)
        self.repro_rate_sb.setValue(1.0)
        form.addRow("Tasa reproducción (max 5.0 / min 0.01):", self.repro_rate_sb)
        tooltip_repro = (
            "Multiplicador sobre el crecimiento bacteriano en cada generación. "
            "Valores >1: aceleran el crecimiento, <1: lo ralentizan."
        )
        self.repro_rate_sb.setToolTip(tooltip_repro)
        self.repro_rate_sb.setToolTipDuration(5000)
        self.repro_rate_sb.setMouseTracking(True)
        label_repro = form.labelForField(self.repro_rate_sb)
        if label_repro:
            label_repro.setToolTip(tooltip_repro)

        grp.setLayout(form)
        self.main_layout.addWidget(grp)

    def create_environmental_params(self):
        grp = QGroupBox("3. Factores Ambientales")
        form = QFormLayout(grp)
        form.setContentsMargins(10, 10, 10, 10)
        form.setHorizontalSpacing(15)
        form.setVerticalSpacing(10)

        self.temperature_sb = QDoubleSpinBox()
        self.temperature_sb.setRange(25.0, 45.0)
        self.temperature_sb.setSingleStep(0.1)
        self.temperature_sb.setValue(37.0)
        self.temperature_sb.setSuffix(" °C")
        form.addRow("Temperatura (°C):", self.temperature_sb)

        self.ph_sb = QDoubleSpinBox()
        self.ph_sb.setRange(5.0, 9.0)
        self.ph_sb.setSingleStep(0.1)
        self.ph_sb.setValue(7.4)
        form.addRow("pH:", self.ph_sb)

        grp.setLayout(form)
        self.main_layout.addWidget(grp)

    def collect_params(self):
        selected = [gid for gid, cb in self.checks.items() if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione al menos un gen.")
            return None
        unit = "Generaciones"
        mut = self.mut_rate_sb.value()
        death = self.death_rate_sb.value()
        time_horizon = self.time_horizon_sb.value()
        environmental_factors = {
            "temperature": self.temperature_sb.value(),
            "pH": self.ph_sb.value(),
        }
        repro = self.repro_rate_sb.value()  # <-- NUEVO
        return selected, unit, mut, death, time_horizon, environmental_factors, repro

    def submit(self):
        params = self.collect_params()
        if params:
            logging.debug(
            f"InputForm.collect_params -> genes={params[0]}, unit={params[1]}, mut_rate={params[2]}, death_rate={params[3]}, time_horizon={params[4]}, environmental_factors={params[5]}, reproduction_rate={params[6]}"
        )
            self.params_submitted.emit(*params)