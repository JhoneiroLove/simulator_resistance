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

    def __init__(self, antibiotics, parent=None):
        super().__init__(parent)
        self.antibiotics = antibiotics
        self._event_items = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # ——— Calendario de Tratamientos ———
        grp_schedule = QGroupBox("Secuencia de Tratamientos")
        schedule_layout = QVBoxLayout(grp_schedule)
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

        # ——— Botones de acción ———
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

        # ——— Pestañas de gráfica ———
        self.plot_tabs = QTabWidget()

        # • Tab Principal (solo Avg)
        self.tab_main = QWidget()
        lay_main = QVBoxLayout(self.tab_main)
        self.plot_main = pg.PlotWidget()
        self.plot_main.setBackground("#fff")
        self.plot_main.showGrid(x=True, y=True, alpha=0.3)
        self.plot_main.setLabel("left", "Nivel de Resistencia")
        self.plot_main.setLabel("bottom", "Tiempo")
        lay_main.addWidget(self.plot_main)

        # Curva promedio únicamente
        self.curve_avg = self.plot_main.plot(
            pen=pg.mkPen("#3498DB", width=2), name="Resistencia Promedio"
        )

        self.plot_tabs.addTab(self.tab_main, "Principal")

        # • Tab Diversidad (opcional)
        self.tab_div = QWidget()
        lay_div = QVBoxLayout(self.tab_div)
        self.plot_div = pg.PlotWidget()
        self.plot_div.setBackground("#fff")
        self.plot_div.showGrid(x=True, y=True, alpha=0.3)
        self.plot_div.setLabel("left", "Diversidad")
        self.plot_div.setLabel("bottom", "Tiempo")
        lay_div.addWidget(self.plot_div)
        # Curva de diversidad
        self.curve_div_tab = self.plot_div.plot(
            pen=pg.mkPen("#2ECC71", width=2), name="Diversidad"
        )

        self.plot_tabs.addTab(self.tab_div, "Diversidad")
        main_layout.addWidget(self.plot_tabs)

        # ——— Datos internos ———
        self.schedule = []
        self.times = np.array([])
        self.avg_vals = np.array([])
        self.div_vals = np.array([])

        # Temporizador para la animación
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)

    def _add_schedule_row(self):
        row = self.schedule_table.rowCount()
        self.schedule_table.insertRow(row)
        ab_cb = QComboBox()
        for a in self.antibiotics:
            ab_cb.addItem(a["nombre"], a["id"])
        conc_sb = QDoubleSpinBox()
        conc_sb.setRange(0, 1e6)
        conc_sb.setValue(self.antibiotics[0].get("conc_min", 0))
        action_btn = QPushButton("Añadir")
        wrapper = QWidget()
        lay = QHBoxLayout(wrapper)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addStretch()
        lay.addWidget(action_btn)
        lay.addStretch()

        self.schedule_table.setCellWidget(row, 0, ab_cb)
        self.schedule_table.setCellWidget(row, 1, conc_sb)
        self.schedule_table.setCellWidget(row, 2, wrapper)

    def _del_schedule_row(self):
        row = self.schedule_table.currentRow()
        if row != -1:
            self.schedule_table.removeRow(row)

    def _emit_simulation(self):
        sched = []
        for r in range(self.schedule_table.rowCount()):
            ab_id = self.schedule_table.cellWidget(r, 0).currentData()
            conc = self.schedule_table.cellWidget(r, 1).value()
            sched.append((r, ab_id, conc))
        self.simulate_requested.emit(sched)

    def clear_plot(self):
        # Limpiar curva promedio
        self.curve_avg.setData([], [])
        # Limpiar curva diversidad
        self.curve_div_tab.setData([], [])
        # Limpiar anotaciones
        for it in self._event_items:
            self.plot_main.removeItem(it)
        self._event_items.clear()

    def update_plot(
        self, times, avg_vals, div_vals=None, schedule=None, interval_ms=100
    ):
        self.times = np.array(times)
        self.avg_vals = np.array(avg_vals)
        self.div_vals = (
            np.array(div_vals) if div_vals is not None else np.zeros_like(self.times)
        )

        # Borrar anotaciones previas
        for it in self._event_items:
            self.plot_main.removeItem(it)
        self._event_items.clear()

        # Guardar schedule para cuando termine
        self.schedule = [
            (t, f"{ab.nombre}\n{conc}") for t, ab, conc in (schedule or [])
        ]

        # Iniciar animación
        self._idx = 0
        self.timer.start(interval_ms)

    def skip_animation(self):
        self.timer.stop()
        self._idx = len(self.times) - 1 if len(self.times) > 0 else 0
        self._update_frame()

    def _update_frame(self):
        end = self._idx >= len(self.times)
        idx = len(self.times) - 1 if end else self._idx
        x = self.times[: idx + 1]

        # Actualizo curva promedio
        self.curve_avg.setData(x, self.avg_vals[: idx + 1])
        # Actualizo diversidad en su pestaña
        self.curve_div_tab.setData(x, self.div_vals[: idx + 1])

        if end:
            # Pinto líneas de evento arriba del principal
            for t_evt, label in self.schedule:
                line = pg.InfiniteLine(
                    pos=t_evt, angle=90, pen=pg.mkPen("#888", style=Qt.DashLine)
                )
                text = pg.TextItem(label, anchor=(0, 1))
                text.setPos(t_evt, self.plot_main.viewRange()[1][1])
                self.plot_main.addItem(line)
                self.plot_main.addItem(text)
                self._event_items.extend([line, text])
            return

        self._idx += 1