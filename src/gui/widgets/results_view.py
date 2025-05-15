from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGroupBox,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QTableWidget,
    QHeaderView,
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
import pyqtgraph as pg
import numpy as np

class ResultsView(QWidget):
    simulate_requested = pyqtSignal(list)
    optimize_requested = pyqtSignal()

    def __init__(self, antibiotics, parent=None):
        super().__init__(parent)
        self.antibiotics = antibiotics  # list of dicts: {id, nombre, conc_min}
        self._event_items = []
        self._schedule_events = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # ——— Calendario de Tratamientos ———
        grp_schedule = QGroupBox("Secuencia de Tratamientos")
        schedule_layout = QVBoxLayout(grp_schedule)

        # Columnas: Antibiótico, Concentración, Tiempo
        self.schedule_table = QTableWidget(0, 3)
        self.schedule_table.setHorizontalHeaderLabels([
            "Antibiótico", "Concentración", "Tiempo"
        ])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        schedule_layout.addWidget(self.schedule_table)

        # Botones Agregar/Eliminar filas
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

        # ——— Botones de acción ———
        actions_hbox = QHBoxLayout()
        actions_hbox.addStretch()

        # Botón simular
        self.run_button = QPushButton("Iniciar Simulación")
        self.run_button.clicked.connect(self._emit_simulation)
        actions_hbox.addWidget(self.run_button)

        # Botón optimizar
        self.optimize_button = QPushButton("Optimizar Tratamiento")
        self.optimize_button.setToolTip("Encuentra el plan óptimo")
        self.optimize_button.clicked.connect(lambda: self.optimize_requested.emit())
        actions_hbox.addWidget(self.optimize_button)

        main_layout.addLayout(actions_hbox)

        # ——— Pestañas de gráfica ———
        self.plot_tabs = QTabWidget()

        # • Tab Principal
        self.tab_main = QWidget()
        lay_main = QVBoxLayout(self.tab_main)
        self.plot_main = pg.PlotWidget()
        self.plot_main.setBackground("#fff")
        self.plot_main.showGrid(x=True, y=True, alpha=0.3)
        self.plot_main.setLabel("left", "Nivel de Resistencia")
        self.plot_main.setLabel("bottom", "Tiempo")
        lay_main.addWidget(self.plot_main)
        self.curve_avg = self.plot_main.plot(pen=pg.mkPen("#3498DB", width=2))
        self.plot_tabs.addTab(self.tab_main, "Principal")

        # • Tab Diversidad
        self.tab_div = QWidget()
        lay_div = QVBoxLayout(self.tab_div)
        self.plot_div = pg.PlotWidget()
        self.plot_div.setBackground("#fff")
        self.plot_div.showGrid(x=True, y=True, alpha=0.3)
        self.plot_div.setLabel("left", "Diversidad")
        self.plot_div.setLabel("bottom", "Tiempo")
        lay_div.addWidget(self.plot_div)
        self.curve_div_tab = self.plot_div.plot(pen=pg.mkPen("#2ECC71", width=2))
        self.plot_tabs.addTab(self.tab_div, "Diversidad")

        main_layout.addWidget(self.plot_tabs)

        # Datos internos
        self.times = np.array([])
        self.avg_vals = np.array([])
        self.div_vals = np.array([])

        # Timer para animación
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)

    def _add_schedule_row(self):
        row = self.schedule_table.rowCount()
        self.schedule_table.insertRow(row)

        # Selector de antibiótico
        ab_cb = QComboBox()
        for a in self.antibiotics:
            ab_cb.addItem(a["nombre"], a["id"])

        # SpinBox de concentración
        conc_sb = QDoubleSpinBox()
        conc_sb.setRange(0, 1e6)
        conc_sb.setValue(self.antibiotics[0].get("conc_min", 0))

        # SpinBox de tiempo (generación)
        time_sb = QDoubleSpinBox()
        time_sb.setRange(0, 1e6)
        time_sb.setValue(0)

        # Colocar en columnas
        self.schedule_table.setCellWidget(row, 0, ab_cb)
        self.schedule_table.setCellWidget(row, 1, conc_sb)
        self.schedule_table.setCellWidget(row, 2, time_sb)

    def _del_schedule_row(self):
        row = self.schedule_table.currentRow()
        if row != -1:
            self.schedule_table.removeRow(row)

    def _emit_simulation(self):
        sched = []
        for r in range(self.schedule_table.rowCount()):
            ab_id = self.schedule_table.cellWidget(r, 0).currentData()
            conc = self.schedule_table.cellWidget(r, 1).value()
            t = self.schedule_table.cellWidget(r, 2).value()
            sched.append((t, ab_id, conc))

        # Registrar eventos para dibujo
        self._schedule_events = []
        for t_evt, ab_id, conc in sched:
            name = next((a['nombre'] for a in self.antibiotics if a['id']==ab_id), str(ab_id))
            self._schedule_events.append((t_evt, name, conc))

        print(f"DEBUG ResultsView._emit_simulation -> schedule={sched}")
        self.simulate_requested.emit(sched)

    def clear_plot(self):
        self.curve_avg.setData([], [])
        self.curve_div_tab.setData([], [])
        for it in self._event_items:
            self.plot_main.removeItem(it)
        self._event_items.clear()

    def update_plot(self, times, avg_vals, div_vals=None, schedule=None, interval_ms=100):
        self.times = np.array(times)
        self.avg_vals = np.array(avg_vals)
        self.div_vals = np.array(div_vals) if div_vals is not None else np.zeros_like(self.times)

        for it in self._event_items:
            self.plot_main.removeItem(it)
        self._event_items.clear()

        if schedule:
            self._schedule_events = []
            for t_evt, ab, conc in schedule:
                name = ab.nombre if hasattr(ab, 'nombre') else str(ab)
                self._schedule_events.append((t_evt, name, conc))

        self._idx = 0
        self.timer.start(interval_ms)

    def _update_frame(self):
        end = hasattr(self, '_idx') and self._idx >= len(self.times)
        idx = len(self.times) - 1 if end else self._idx
        x = self.times[:idx+1]

        self.curve_avg.setData(x, self.avg_vals[:idx+1])
        self.curve_div_tab.setData(x, self.div_vals[:idx+1])

        if end:
            for t_evt, name, conc in self._schedule_events:
                line = pg.InfiniteLine(pos=t_evt, angle=90, pen=pg.mkPen('#888', style=Qt.DashLine))
                text = pg.TextItem(f"{name}\n{conc:.2f}", anchor=(0, 1))
                text.setPos(t_evt, self.plot_main.viewRange()[1][1])
                self.plot_main.addItem(line)
                self.plot_main.addItem(text)
                self._event_items.extend([line, text])
            return

        self._idx += 1
