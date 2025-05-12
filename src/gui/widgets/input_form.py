from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QComboBox,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QScrollArea,
    QFrame,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from types import SimpleNamespace

from src.data.database import get_session
from src.data.models import Gen, Antibiotico


class InputForm(QWidget):
    # Ahora emitimos: selected_genes_ids, schedule (tuplas de id), unidad, mut_rate, death_rate
    simulation_triggered = pyqtSignal(list, list, str, float, float)

    def __init__(self):
        super().__init__()
        self.session = get_session()
        self.main_layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QWidget { font-family: 'Segoe UI'; font-size:12px; }
            QGroupBox { border:1px solid #ccc; border-radius:5px; margin-top:10px; }
            QPushButton { background-color:#4CAF50; color:white; padding:8px 16px; }
            QPushButton:hover { background-color:#45a049; }
        """)

        self.load_data()
        self.create_gene_selection()
        self.create_simulation_params()
        self.create_antibiotic_schedule()
        self.create_simulation_button()
        self.main_layout.addStretch()

    def load_data(self):
        """Carga genes y antibióticos como estructuras planas (no ORM)."""
        # Genes
        genes_q = self.session.query(Gen.id, Gen.nombre, Gen.descripcion).all()
        # Usamos SimpleNamespace solo para acceder con .id, .nombre, .descripcion
        self.genes = [
            SimpleNamespace(id=g[0], nombre=g[1], descripcion=g[2]) for g in genes_q
        ]

        # Antibióticos: necesitamos id, nombre y conc_min para el UI
        abs_q = self.session.query(
            Antibiotico.id, Antibiotico.nombre, Antibiotico.concentracion_minima
        ).all()
        self.antibioticos = [
            {"id": a[0], "nombre": a[1], "conc_min": a[2]} for a in abs_q
        ]

    def create_gene_selection(self):
        grp = QGroupBox("1. Selección de Genes")
        lay = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        cont = QWidget()
        cont_l = QVBoxLayout(cont)
        self.checks = {}
        for g in self.genes:
            cb = QCheckBox(f"{g.nombre} ({g.descripcion})")
            self.checks[g.id] = cb
            cont_l.addWidget(cb)
        cont_l.addStretch()
        scroll.setWidget(cont)
        lay.addWidget(scroll)
        grp.setLayout(lay)
        self.main_layout.addWidget(grp)

    def create_simulation_params(self):
        grp = QGroupBox("2. Parámetros de Simulación")
        form = QFormLayout(grp)
        # Unidad de tiempo
        self.time_unit_cb = QComboBox()
        self.time_unit_cb.addItems(["Generaciones", "Horas", "Días"])
        form.addRow("Unidad de tiempo:", self.time_unit_cb)
        # Duración
        self.time_horizon_sb = QSpinBox()
        self.time_horizon_sb.setRange(1, 10000)
        self.time_horizon_sb.setValue(100)
        form.addRow("Duración total:", self.time_horizon_sb)
        # Tasa mutación
        self.mut_rate_sb = QDoubleSpinBox()
        self.mut_rate_sb.setRange(0.0, 1.0)
        self.mut_rate_sb.setSingleStep(0.01)
        self.mut_rate_sb.setValue(0.05)
        form.addRow("Tasa mutación:", self.mut_rate_sb)
        # Tasa mortalidad
        self.death_rate_sb = QDoubleSpinBox()
        self.death_rate_sb.setRange(0.0, 1.0)
        self.death_rate_sb.setSingleStep(0.01)
        self.death_rate_sb.setValue(0.05)
        form.addRow("Tasa mortalidad:", self.death_rate_sb)
        self.main_layout.addWidget(grp)

    def create_antibiotic_schedule(self):
        grp = QGroupBox("3. Secuencia de Tratamientos")
        lay = QVBoxLayout()
        # Tabla con 3 columnas: Tiempo, Antibiótico, Concentración
        self.schedule_table = QTableWidget(0, 3)
        self.schedule_table.setHorizontalHeaderLabels(
            ["Tiempo", "Antibiótico", "Concentración"]
        )
        self.schedule_table.horizontalHeader().setStretchLastSection(True)
        lay.addWidget(self.schedule_table)
        # Botones Agregar/Eliminar
        hl = QHBoxLayout()
        btn_add = QPushButton("Agregar tratamiento")
        btn_add.clicked.connect(self._add_schedule_row)
        btn_del = QPushButton("Eliminar fila")
        btn_del.clicked.connect(self._del_schedule_row)
        hl.addWidget(btn_add)
        hl.addWidget(btn_del)
        hl.addStretch()
        lay.addLayout(hl)
        grp.setLayout(lay)
        self.main_layout.addWidget(grp)

    def _add_schedule_row(self):
        """Inserta una nueva fila con spinboxes y combobox."""
        row = self.schedule_table.rowCount()
        self.schedule_table.insertRow(row)
        # Tiempo (float)
        time_sb = QDoubleSpinBox()
        time_sb.setRange(0, 1e6)
        time_sb.setValue(0.0)
        # Antibiótico (combo con nombres + datos planos)
        ab_cb = QComboBox()
        for a in self.antibioticos:
            ab_cb.addItem(a["nombre"], a["id"])
        # Concentración (default = conc_min del primero)
        conc_sb = QDoubleSpinBox()
        conc_sb.setRange(0.0, 1e6)
        conc_sb.setValue(self.antibioticos[0]["conc_min"] if self.antibioticos else 0.0)

        self.schedule_table.setCellWidget(row, 0, time_sb)
        self.schedule_table.setCellWidget(row, 1, ab_cb)
        self.schedule_table.setCellWidget(row, 2, conc_sb)

    def _del_schedule_row(self):
        """Elimina la fila actualmente seleccionada."""
        row = self.schedule_table.currentRow()
        if row >= 0:
            self.schedule_table.removeRow(row)

    def on_simulate(self):
        """Valida entradas y emite la señal con los datos planos."""
        # Genes seleccionados
        selected = [gid for gid, cb in self.checks.items() if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione al menos un gen.")
            return
        # Debe haber al menos un tratamiento
        if self.schedule_table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "Agregue al menos un tratamiento.")
            return

        # Leemos la tabla de schedule
        schedule = []
        for r in range(self.schedule_table.rowCount()):
            t = self.schedule_table.cellWidget(r, 0).value()
            ab_id = self.schedule_table.cellWidget(r, 1).currentData()
            conc = self.schedule_table.cellWidget(r, 2).value()
            schedule.append((t, ab_id, conc))
        schedule.sort(key=lambda x: x[0])

        # Parámetros
        unit = self.time_unit_cb.currentText()
        mut_r = self.mut_rate_sb.value()
        death_r = self.death_rate_sb.value()

        # Emitimos lista de IDs y lista de tuplas (tiempo,id,conc)
        self.simulation_triggered.emit(selected, schedule, unit, mut_r, death_r)

    def create_simulation_button(self):
        grp = QGroupBox("4. Ejecutar Simulación")
        lay = QVBoxLayout()
        btn = QPushButton("Iniciar Simulación")
        btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn.clicked.connect(self.on_simulate)
        lay.addWidget(btn, alignment=Qt.AlignCenter)
        grp.setLayout(lay)
        self.main_layout.addWidget(grp)
