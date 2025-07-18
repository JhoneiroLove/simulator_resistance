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
    QMessageBox,
    QLabel,
    QFrame,
    QSizePolicy,
    QDialog,
    QSpinBox,
    QTableWidgetItem,
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QLocale
from .resistance_widget import ResistanceWidget
from .diversity_widget import DiversityWidget
from .population_widget import PopulationWidget
from .expansion_widget import ExpansionWidget
from .degradation_widget import DegradationWidget
import pyqtgraph as pg
import numpy as np
import logging

ANTIBIOTICS_LIST = [
    {"id": 1, "nombre": "Meropenem", "conc_min": 0.03, "conc_max": 64.0},
    {"id": 2, "nombre": "Ciprofloxacino", "conc_min": 0.25, "conc_max": 256.0},
    {"id": 3, "nombre": "Colistina", "conc_min": 0.06, "conc_max": 512.0},
    {"id": 4, "nombre": "Amikacina", "conc_min": 0.5, "conc_max": 512.0},
    {"id": 5, "nombre": "Piperacilina/Tazobactam", "conc_min": 0.5, "conc_max": 1024.0},
    {"id": 6, "nombre": "Ceftazidima", "conc_min": 0.25, "conc_max": 1024.0},
    {"id": 7, "nombre": "Gentamicina", "conc_min": 0.5, "conc_max": 512.0},
    {"id": 8, "nombre": "Tobramicina", "conc_min": 0.25, "conc_max": 1024.0},
    {"id": 9, "nombre": "Imipenem", "conc_min": 0.12, "conc_max": 128.0},
    {"id": 10, "nombre": "Cefepime", "conc_min": 1.0, "conc_max": 32.0},
]

class ResultsView(QWidget):
    simulate_requested = pyqtSignal(list)

    def __init__(self, antibiotics=None, parent=None):
        super().__init__(parent)
        self.antibiotics = antibiotics if antibiotics is not None else ANTIBIOTICS_LIST
        self._schedule_events = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        # ——— Sección de secuencia de tratamientos ———
        self._create_schedule_section(main_layout)

        # ——— Sección de acciones ———
        self._create_actions_section(main_layout)

        # ——— Pestañas de gráficos (usando widgets separados) ———
        self._create_plot_tabs(main_layout)

        # Datos internos
        self.times = np.array([])
        self.avg_vals = np.array([])
        self.div_vals = np.array([])

        # Timer para animación
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)

        # Thresholds para visualización
        self.extinction_threshold = 100
        self.resistance_threshold = 0.8

    def _create_schedule_section(self, main_layout):
        """Crea la sección de secuencia de tratamientos."""
        grp_schedule = QGroupBox("Secuencia de Tratamientos")
        schedule_layout = QVBoxLayout(grp_schedule)

        self.schedule_table = QTableWidget(0, 3)
        self.schedule_table.setHorizontalHeaderLabels(
            ["Antibiótico", "Concentración (mg/l)", "Tiempo (Generacion)"]
        )
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.setFixedHeight(120)
        self.schedule_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.schedule_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.schedule_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

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

    def _create_actions_section(self, main_layout):
        """Crea la sección de botones de acción."""
        actions_hbox = QHBoxLayout()
        actions_hbox.addStretch()

        self.run_button = QPushButton("Iniciar Simulación")
        self.run_button.clicked.connect(self._emit_simulation)
        actions_hbox.addWidget(self.run_button)

        self.dose_intervals_button = QPushButton("Ver intervalos de dosis")
        self.dose_intervals_button.clicked.connect(self.show_dose_intervals_modal)
        actions_hbox.addWidget(self.dose_intervals_button)

        # Conexiones para habilitar/deshabilitar el botón de simulación
        self.schedule_table.model().rowsInserted.connect(self._update_run_button_state)
        self.schedule_table.model().rowsRemoved.connect(self._update_run_button_state)
        self._update_run_button_state()

        main_layout.addLayout(actions_hbox)

    def _create_plot_tabs(self, main_layout):
        """Crea las pestañas con los widgets de gráficos separados."""
        self.plot_tabs = QTabWidget()

        # Tab 1: Resistencia
        self.resistance_widget = ResistanceWidget()
        self.plot_tabs.addTab(self.resistance_widget, "Resistencia")

        # Tab 2: Diversidad
        self.diversity_widget = DiversityWidget()
        self.plot_tabs.addTab(self.diversity_widget, "Diversidad")

        # Tab 3: Población
        self.population_widget = PopulationWidget()
        self.plot_tabs.addTab(self.population_widget, "Población")

        # Tab 4: Expansión
        self.expansion_widget = ExpansionWidget()
        self.plot_tabs.addTab(self.expansion_widget, "Expansión")

        # Tab 5: Degradación
        self.degradation_widget = DegradationWidget()
        self.plot_tabs.addTab(self.degradation_widget, "Degradación")

        main_layout.addWidget(self.plot_tabs)

    def show_dose_intervals_modal(self):
        """Muestra el modal con intervalos de dosis por medicamento."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Intervalos de dosis por medicamento")
        layout = QVBoxLayout(dialog)
        label = QLabel("Intervalos de dosis aplicables por medicamento:")
        layout.addWidget(label)
        table = QTableWidget(dialog)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(
            ["Medicamento", "Dosis mínima (mg/l)", "Dosis máxima (mg/l)"]
        )
        table.setRowCount(len(self.antibiotics))
        for i, ab in enumerate(self.antibiotics):
            item_nombre = QTableWidgetItem(str(ab.get("nombre", "")))
            min_val = ab.get("conc_min")
            max_val = ab.get("conc_max")
            item_min = QTableWidgetItem(str(min_val if min_val is not None else "-"))
            item_max = QTableWidgetItem(str(max_val if max_val is not None else "-"))
            flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
            item_nombre.setFlags(flags)
            item_min.setFlags(flags)
            item_max.setFlags(flags)
            table.setItem(i, 0, item_nombre)
            table.setItem(i, 1, item_min)
            table.setItem(i, 2, item_max)
        table.resizeColumnsToContents()
        layout.addWidget(table)
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(dialog.accept)
        layout.addWidget(btn_close)
        dialog.setLayout(layout)
        dialog.resize(500, 350)
        dialog.exec_()

    def _update_run_button_state(self):
        """Habilita el botón de simulación solo si hay al menos una fila en la tabla."""
        self.run_button.setEnabled(self.schedule_table.rowCount() > 0)

    def _add_schedule_row(self):
        """Añade una nueva fila a la tabla de secuencia."""
        row = self.schedule_table.rowCount()
        self.schedule_table.insertRow(row)

        # Selector de antibiótico
        ab_cb = QComboBox()
        for a in self.antibiotics:
            ab_cb.addItem(a["nombre"], a["id"])

        # SpinBox de concentración
        selected_ab = self.antibiotics[0]
        conc_sb = QDoubleSpinBox()
        conc_sb.setDecimals(2)
        conc_sb.setSingleStep(0.01)
        conc_sb.setLocale(QLocale(QLocale.C))
        conc_sb.setRange(selected_ab["conc_min"], selected_ab["conc_max"])
        conc_sb.setValue(selected_ab["conc_min"])

        def on_antibiotic_changed(index):
            ab_data = self.antibiotics[index]
            min_c = ab_data["conc_min"]
            max_c = ab_data["conc_max"]
            conc_sb.setRange(min_c, max_c)
            if not (min_c <= conc_sb.value() <= max_c):
                conc_sb.setValue(min_c)

        ab_cb.currentIndexChanged.connect(on_antibiotic_changed)

        # SpinBox de tiempo
        time_sb = QSpinBox()
        time_sb.setRange(0, 10000)
        time_sb.setValue(0)

        # Colocar en columnas
        self.schedule_table.setCellWidget(row, 0, ab_cb)
        self.schedule_table.setCellWidget(row, 1, conc_sb)
        self.schedule_table.setCellWidget(row, 2, time_sb)

    def _del_schedule_row(self):
        """Elimina la fila seleccionada de la tabla."""
        row = self.schedule_table.currentRow()
        if row == -1:
            row = self.schedule_table.rowCount() - 1
        if row >= 0:
            self.schedule_table.removeRow(row)

    def _emit_simulation(self):
        """Emite la señal de simulación con los parámetros de la tabla."""
        sched = []
        for r in range(self.schedule_table.rowCount()):
            ab_cb = self.schedule_table.cellWidget(r, 0)
            conc_sb = self.schedule_table.cellWidget(r, 1)
            ab_index = ab_cb.currentIndex()
            ab_data = self.antibiotics[ab_index]
            conc = conc_sb.value()

            # Validación por rango
            if not (ab_data["conc_min"] <= conc <= ab_data["conc_max"]):
                ab_name = ab_data["nombre"]
                self.show_alert(
                    "Concentración fuera de rango",
                    f"La concentración para {ab_name} debe estar entre {ab_data['conc_min']} y {ab_data['conc_max']} mg/l.",
                )
                return

            t = self.schedule_table.cellWidget(r, 2).value()
            ab_id = ab_cb.currentData()
            sched.append((t, ab_id, conc))

        # Registrar eventos para dibujo
        self._schedule_events = []
        for t_evt, ab_id, conc in sched:
            name = next(
                (a["nombre"] for a in self.antibiotics if a["id"] == ab_id), str(ab_id)
            )
            self._schedule_events.append((t_evt, name, conc))

        logging.debug(f"ResultsView._emit_simulation -> schedule={sched}")
        self.simulate_requested.emit(sched)

    def clear_plot(self):
        """Limpia todos los gráficos."""
        self.resistance_widget.clear_plot()
        self.diversity_widget.clear_plot()
        self.population_widget.clear_plot()
        self.expansion_widget.clear_plot()
        self.degradation_widget.clear_plot()

    def _update_frame(self):
        """Actualiza los frames de animación (método legacy)."""
        # La actualización se hace desde main_window
        pass

    # ——— Métodos de actualización para cada widget ———

    def update_resistance_plot(self, times, avg_hist):
        """Actualiza el gráfico de resistencia."""
        self.resistance_widget.update_plot(times, avg_hist)

    def update_diversity_plot(self, times, div_hist):
        """Actualiza el gráfico de diversidad."""
        self.diversity_widget.update_plot(times, div_hist)

    def update_population_plot(self, times, population_hist):
        """Actualiza el gráfico de población."""
        self.population_widget.update_plot(times, population_hist)

    def update_expansion_plot(self, times, expansion_hist):
        """Actualiza el gráfico de expansión."""
        self.expansion_widget.update_plot(times, expansion_hist)

    def update_degradation_plot(self, times, degradation_hist):
        """Actualiza el gráfico de degradación."""
        self.degradation_widget.update_plot(times, degradation_hist)

    def add_antibiotic_markers(self, schedule):
        """Añade marcadores de antibióticos al gráfico de resistencia."""
        self.resistance_widget.add_antibiotic_markers(schedule)

    # ——— Métodos de interpretación ———

    def show_interpretation(self, final_value: float):
        """Muestra la interpretación de resistencia."""
        self.resistance_widget.show_interpretation(final_value)

    def show_population_interpretation(self, final_value: float):
        """Muestra la interpretación de población."""
        self.population_widget.show_interpretation(final_value)

    def show_degradation_interpretation(self, peak_value: float):
        """Muestra la interpretación de degradación."""
        self.degradation_widget.show_interpretation(peak_value)

    def show_alert(self, title, message):
        """Muestra una alerta al usuario."""
        QMessageBox.warning(self, title, message, QMessageBox.Ok)

    # ——— Propiedades de compatibilidad ———

    @property
    def curve_avg(self):
        """Acceso a la curva de resistencia para compatibilidad."""
        return self.resistance_widget.curve_avg

    @property
    def curve_div_tab(self):
        """Acceso a la curva de diversidad para compatibilidad."""
        return self.diversity_widget.curve_div

    @property
    def plot_main(self):
        """Acceso al plot principal para compatibilidad."""
        return self.resistance_widget.plot_main

    @property
    def resistance_thresholds(self):
        """Acceso a los umbrales de resistencia para compatibilidad."""
        return self.resistance_widget.resistance_thresholds