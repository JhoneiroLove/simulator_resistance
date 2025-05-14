from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QTableWidget, QPushButton, QComboBox, QDoubleSpinBox, QHeaderView
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
import pyqtgraph as pg
import numpy as np

class ResultsView(QWidget):
    simulate_requested = pyqtSignal(list)

    def __init__(self, antibiotics, parent=None):
        super().__init__(parent)
        self.antibiotics = antibiotics

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # Grupo: Secuencia de Tratamientos
        grp_schedule = QGroupBox("Secuencia de Tratamientos")
        schedule_layout = QVBoxLayout(grp_schedule)
        # Ahora 3 columnas: Antibiótico, Concentración, Acciones
        self.schedule_table = QTableWidget(0, 3)
        self.schedule_table.setHorizontalHeaderLabels(
            ["Antibiótico", "Concentración", "Acciones"]
        )
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        schedule_layout.addWidget(self.schedule_table)

        btn_hbox = QHBoxLayout()
        btn_add = QPushButton("Agregar")
        btn_del = QPushButton("Eliminar")
        btn_add.setFixedWidth(100)
        btn_del.setFixedWidth(100)
        btn_add.clicked.connect(self._add_schedule_row)
        btn_del.clicked.connect(self._del_schedule_row)
        btn_hbox.addWidget(btn_add)
        btn_hbox.addWidget(btn_del)
        btn_hbox.addStretch()
        schedule_layout.addLayout(btn_hbox)
        main_layout.addWidget(grp_schedule)

        # Botones de acción
        actions_hbox = QHBoxLayout()
        self.run_button = QPushButton("Iniciar Simulación")
        self.skip_button = QPushButton("Saltar Animación")
        self.skip_button.setToolTip("Muestra todos los datos sin animación")
        self.run_button.clicked.connect(self._emit_simulation)
        self.skip_button.clicked.connect(self.skip_animation)
        actions_hbox.addStretch()
        actions_hbox.addWidget(self.run_button)
        actions_hbox.addWidget(self.skip_button)
        main_layout.addLayout(actions_hbox)

        # Gráfico
        grp_plot = QGroupBox("Evolución Dinámica de Resistencia")
        plot_layout = QVBoxLayout(grp_plot)
        self.plot = pg.PlotWidget()
        self.plot.setBackground('#fff')
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setLabel('left', 'Nivel de Resistencia')
        self.plot.setLabel('bottom', 'Tiempo')
        plot_layout.addWidget(self.plot)
        main_layout.addWidget(grp_plot)

        # Curvas
        self.curve_max = self.plot.plot(pen=pg.mkPen('#E74C3C', width=2), name="Máx")
        self.curve_avg = self.plot.plot(pen=pg.mkPen('#3498DB', width=2), name="Avg")
        self.curve_mort = self.plot.plot(pen=pg.mkPen('#9B59B6', width=2), name="Mort")
        self.curve_mut = self.plot.plot(pen=pg.mkPen('#F1C40F', width=2), name="Mut")
        self.curve_div = self.plot.plot(pen=pg.mkPen("#2ECC71", width=2), name="Div")

        # Datos
        self.times = np.array([])
        self.max_vals = np.array([])
        self.avg_vals = np.array([])
        self.mort_vals = np.array([])
        self.mut_vals = np.array([])
        self.schedule = []
        self._idx = 0
        self._event_items = []

        # Temporizador animación
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)

    def _add_schedule_row(self):
        row = self.schedule_table.rowCount()
        self.schedule_table.insertRow(row)

        # Combo antibiótico
        ab_cb = QComboBox()
        for a in self.antibiotics:
            ab_cb.addItem(a['nombre'], a['id'])
        self.schedule_table.setCellWidget(row, 0, ab_cb)

        # Spin concentración
        conc_sb = QDoubleSpinBox()
        conc_sb.setRange(0, 1e6)
        conc_sb.setValue(self.antibiotics[0].get('conc_min', 0))
        self.schedule_table.setCellWidget(row, 1, conc_sb)

        # Botón de acción en la nueva columna
        action_btn = QPushButton("Añadir")
        action_btn.setFixedWidth(80)
        # wrapper para centrar
        wrapper = QWidget()
        lay = QHBoxLayout(wrapper)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addStretch()
        lay.addWidget(action_btn)
        lay.addStretch()
        # Aquí puedes conectar action_btn.clicked a la función que desees
        # action_btn.clicked.connect(lambda _, r=row: self._your_custom_handler(r))
        self.schedule_table.setCellWidget(row, 2, wrapper)

    def _del_schedule_row(self):
        row = self.schedule_table.currentRow()
        if row != -1:
            self.schedule_table.removeRow(row)

    def _emit_simulation(self):
        sched = []
        for r in range(self.schedule_table.rowCount()):
            t = r
            ab_id = self.schedule_table.cellWidget(r, 0).currentData()
            conc = self.schedule_table.cellWidget(r, 1).value()
            sched.append((t, ab_id, conc))
        self.simulate_requested.emit(sched)

    def update_plot(self, times, max_vals, avg_vals,
                    mort_vals=None, mut_vals=None, div_vals=None,
                    schedule=None, interval_ms=100):
        self.times = np.array(times)
        self.max_vals = np.array(max_vals)
        self.avg_vals = np.array(avg_vals)
        self.mort_vals = np.array(mort_vals) if mort_vals is not None else np.zeros_like(self.times)
        self.mut_vals = np.array(mut_vals) if mut_vals is not None else np.zeros_like(self.times)
        self.div_vals = (np.array(div_vals) if div_vals is not None else np.zeros_like(self.times))
        self.schedule = [(t, f"{ab.nombre}\n{conc}") for t, ab, conc in (schedule or [])]
        self._idx = 0
        self.plot.setXRange(self.times[0], self.times[-1])
        y_min = min(self.mort_vals.min(), self.mut_vals.min(),
                    self.avg_vals.min(), self.max_vals.min())
        y_max = max(self.mort_vals.max(), self.mut_vals.max(),
                    self.avg_vals.max(), self.max_vals.max())
        self.plot.setYRange(y_min, y_max)
        for it in self._event_items:
            self.plot.removeItem(it)
        self._event_items = []
        self.timer.start(interval_ms)

    def skip_animation(self):
        self.timer.stop()
        self._idx = len(self.times) - 1 if len(self.times) > 0 else 0
        self._update_frame()

    def _update_frame(self):
        if self._idx >= len(self.times):
            x = self.times
            self.curve_max.setData(x, self.max_vals)
            self.curve_avg.setData(x, self.avg_vals)
            self.curve_mort.setData(x, self.mort_vals)
            self.curve_mut.setData(x, self.mut_vals)
            self.curve_div.setData(x, self.div_vals)
            for t_evt, label in self.schedule:
                line = pg.InfiniteLine(pos=t_evt, angle=90,
                pen=pg.mkPen('#888', style=Qt.DashLine))
                text = pg.TextItem(label, anchor=(0, 1))
                text.setPos(t_evt, self.plot.viewRange()[1][1])
                self.plot.addItem(line)
                self.plot.addItem(text)
                self._event_items.extend([line, text])
            return

        x = self.times[:self._idx + 1]
        self.curve_max.setData(x, self.max_vals[:self._idx + 1])
        self.curve_avg.setData(x, self.avg_vals[:self._idx + 1])
        self.curve_mort.setData(x, self.mort_vals[:self._idx + 1])
        self.curve_mut.setData(x, self.mut_vals[:self._idx + 1])
        self.curve_div.setData(x, self.div_vals[: self._idx + 1])
        self._idx += 1
