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
    QComboBox,
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from types import SimpleNamespace

from src.data.database import get_session
from src.data.models import Gen

class InputForm(QWidget):
    params_submitted = pyqtSignal(
        list, str, float, float, int, dict, float, str, float, float, str, object
    )

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
        self.create_patient_params()

        # Botón Guardar parámetros
        self.save_button = QPushButton("Guardar parámetros")
        self.save_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.save_button.setFixedHeight(38)
        self.save_button.clicked.connect(self.submit)
        self.main_layout.addWidget(self.save_button, alignment=Qt.AlignHCenter)
        self.main_layout.addStretch()


    def load_data(self):
        """Carga genes y sitios de infección como estructuras planas."""
        genes_q = self.session.query(Gen.id, Gen.nombre, Gen.descripcion).all()
        self.genes = [
            SimpleNamespace(id=g[0], nombre=g[1], descripcion=g[2]) for g in genes_q
        ]
        
        # Cargar sitios de infección
        from src.data.models import InfectionSite
        sitios_q = self.session.query(
            InfectionSite.id, 
            InfectionSite.nombre, 
            InfectionSite.ph, 
            InfectionSite.capacidad_carga
        ).all()
        self.sitios_infeccion = [
            SimpleNamespace(id=s[0], nombre=s[1], ph=s[2], capacidad_carga=s[3]) 
            for s in sitios_q
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

    def create_patient_params(self):
        grp = QGroupBox("4. Parámetros del Paciente")
        form = QFormLayout(grp)
        form.setContentsMargins(10, 10, 10, 10)
        form.setHorizontalSpacing(15)
        form.setVerticalSpacing(10)

        # ComboBox de rango de edad
        self.age_range_cb = QComboBox()
        self.age_range_cb.addItems([
            "Neonato (0-28 días)",
            "Infante (1 mes - 2 años)",
            "Niño (2-12 años)",
            "Adolescente (12-18 años)",
            "Adulto (18-65 años)",
            "Anciano (>65 años)"
        ])
        self.age_range_cb.setCurrentIndex(4)  # Default: Adulto
        form.addRow("Rango de edad:", self.age_range_cb)
        tooltip_age = (
            "Seleccione el rango de edad del paciente. "
            "Esto afecta parámetros fisiológicos y farmacocinéticos en la simulación."
        )
        self.age_range_cb.setToolTip(tooltip_age)
        self.age_range_cb.setToolTipDuration(5000)

        # SpinBox de peso
        self.weight_sb = QDoubleSpinBox()
        self.weight_sb.setRange(0.5, 200.0)
        self.weight_sb.setSingleStep(0.1)
        self.weight_sb.setValue(70.0)  # Default: 70 kg
        self.weight_sb.setDecimals(1)
        self.weight_sb.setSuffix(" kg")
        form.addRow("Peso (kg):", self.weight_sb)
        tooltip_weight = (
            "Ingrese el peso del paciente en kilogramos. "
            "Se usa para calcular dosificación y ajustes farmacocinéticos."
        )
        self.weight_sb.setToolTip(tooltip_weight)
        self.weight_sb.setToolTipDuration(5000)

        # Creatinina sérica
        self.creatinina_sb = QDoubleSpinBox()
        self.creatinina_sb.setRange(0.1, 15.0)
        self.creatinina_sb.setSingleStep(0.1)
        self.creatinina_sb.setValue(1.0)  # Default: 1.0 mg/dL (normal)
        self.creatinina_sb.setDecimals(2)
        self.creatinina_sb.setSuffix(" mg/dL")
        form.addRow("Creatinina sérica:", self.creatinina_sb)
        tooltip_creatinina = (
            "Ingrese el valor de creatinina sérica en mg/dL. "
            "Se usa para calcular el clearance de creatinina y ajustar dosis por función renal. "
            "Valor normal: 0.6-1.2 mg/dL"
        )
        self.creatinina_sb.setToolTip(tooltip_creatinina)
        self.creatinina_sb.setToolTipDuration(5000)

        # ComboBox estado inmune
        self.estado_inmune_cb = QComboBox()
        self.estado_inmune_cb.addItems([
            "Normal",
            "Inmunodeprimido",
            "Inmunodeprimido severo"
        ])
        self.estado_inmune_cb.setCurrentIndex(0)  # Default: Normal
        form.addRow("Estado inmune:", self.estado_inmune_cb)
        tooltip_inmune = (
            "Seleccione el estado del sistema inmune del paciente. "
            "Esto afecta la capacidad de combatir la infección bacteriana. "
            "Pacientes inmunodeprimidos requieren tratamientos más agresivos."
        )
        self.estado_inmune_cb.setToolTip(tooltip_inmune)
        self.estado_inmune_cb.setToolTipDuration(5000)
        
        # ComboBox sitio de infección
        self.sitio_infeccion_cb = QComboBox()
        self.sitio_infeccion_cb.addItem("Ninguno (usar valores por defecto)", None)
        for sitio in self.sitios_infeccion:
            self.sitio_infeccion_cb.addItem(sitio.nombre, sitio.id)
        self.sitio_infeccion_cb.setCurrentIndex(0)  # Default: Ninguno
        form.addRow("Sitio de infección:", self.sitio_infeccion_cb)
        tooltip_sitio = (
            "Seleccione el sitio anatómico donde ocurre la infección. "
            "Cada sitio tiene características específicas (pH, capacidad de carga, perfusión) "
            "que afectan la efectividad del tratamiento."
        )
        self.sitio_infeccion_cb.setToolTip(tooltip_sitio)
        self.sitio_infeccion_cb.setToolTipDuration(5000)

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
        repro = self.repro_rate_sb.value()
        age_range = self.age_range_cb.currentText()
        weight = self.weight_sb.value()
        creatinina = self.creatinina_sb.value()
        estado_inmune = self.estado_inmune_cb.currentText()
        sitio_infeccion_id = self.sitio_infeccion_cb.currentData()
        return selected, unit, mut, death, time_horizon, environmental_factors, repro, age_range, weight, creatinina, estado_inmune, sitio_infeccion_id
    
    def submit(self):
        params = self.collect_params()
        if params:
            logging.debug(
                f"InputForm.collect_params -> genes={params[0]}, unit={params[1]}, mut_rate={params[2]}, "
                f"death_rate={params[3]}, time_horizon={params[4]}, environmental_factors={params[5]}, "
                f"reproduction_rate={params[6]}, age_range={params[7]}, weight={params[8]}, "
                f"creatinina={params[9]}, estado_inmune={params[10]}, sitio_infeccion_id={params[11]}"
            )
            self.params_submitted.emit(*params)