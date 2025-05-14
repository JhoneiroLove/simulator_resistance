import sys
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QStatusBar,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import QTimer
from src.gui.widgets.input_form import InputForm
from src.gui.widgets.results_view import ResultsView
from src.gui.widgets.csv_validation import CSVValidationWidget
from src.gui.widgets.detailed_results import DetailedResults
from src.core.genetic_algorithm import GeneticAlgorithm
from src.data.database import get_session
from src.data.models import Gen, Antibiotico, Simulacion, SimulacionGen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador Evolutivo por Tratamientos")
        self.setGeometry(100, 100, 1280, 720)

        # ---- pestañas ----
        self.tabs = QTabWidget()
        self.input_tab = InputForm()

        # datos de antibióticos para ResultsView
        session = get_session()
        abs_q = session.query(
            Antibiotico.id, Antibiotico.nombre, Antibiotico.concentracion_minima
        ).all()
        session.close()
        antibiotics = [{"id": a[0], "nombre": a[1], "conc_min": a[2]} for a in abs_q]

        self.results_tab = ResultsView(antibiotics)
        # Conectar inicio de simulación
        self.results_tab.simulate_requested.connect(self.handle_simulation)
        # Conectar detección de cambios en la tabla de schedule
        self.results_tab.schedule_table.cellChanged.connect(
            lambda *args: self._reload_schedule()
        )

        self.csv_tab = CSVValidationWidget()
        self.detail_tab = DetailedResults()

        self.tabs.addTab(self.input_tab, "1. Selección y Parámetros")
        self.tabs.addTab(self.results_tab, "2. Secuencia y Simulación")
        self.tabs.addTab(self.csv_tab, "Validación CSV")
        self.tabs.addTab(self.detail_tab, "Resultados Detallados")

        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())

        # temporizador para pasos de Simulación
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._on_sim_step)

    def handle_simulation(self, schedule):
        """
        schedule: lista de (t, ab_id, conc). Lanzada al pulsar 'Iniciar Simulación'.
        """
        # genes seleccionados
        selected_genes = [
            gid for gid, cb in self.input_tab.checks.items() if cb.isChecked()
        ]
        if not selected_genes:
            QMessageBox.warning(self, "Error", "Seleccione al menos un gen.")
            self.tabs.setCurrentWidget(self.input_tab)
            return

        # parámetros
        mut_rate = self.input_tab.mut_rate_sb.value()
        death_rate = self.input_tab.death_rate_sb.value()
        time_horizon = self.input_tab.time_horizon_sb.value()

        # cargar genes ORM
        session = get_session()
        genes = session.query(Gen).all()
        session.close()

        # instanciar GA (schedule vacío: lo inyectaremos dinámicamente)
        self.ga = GeneticAlgorithm(
            genes=genes,
            antibiotic_schedule=[],
            mutation_rate=mut_rate,
            generations=time_horizon,
            pop_size=200,
            death_rate=death_rate,
        )
        self.ga.initialize(selected_genes)

        # limpiar gráfica anterior
        self.results_tab.clear_plot()

        # arrancar el timer (100ms entre generaciones)
        self.sim_timer.start(100)

        # cambiar a la pestaña de simulación
        self.tabs.setCurrentWidget(self.results_tab)

    def _reload_schedule(self):
        """
        Cada vez que cambie ANY celda de la tabla de schedule,
        volvemos a leerla y actualizamos self.ga.schedule.
        """
        session = get_session()
        ui_sched = []
        for r in range(self.results_tab.schedule_table.rowCount()):
            # tiempo → si tu tabla tiene columna explícita de tiempo la lees aquí;
            # en este ejemplo usamos el índice de fila:
            t = r
            ab_cb = self.results_tab.schedule_table.cellWidget(r, 0)
            conc_sb = self.results_tab.schedule_table.cellWidget(r, 1)
            if not ab_cb or not conc_sb:
                continue
            ab_id = ab_cb.currentData()
            ab = session.query(Antibiotico).get(ab_id)
            conc = conc_sb.value()
            ui_sched.append((t, ab, conc))
        session.close()
        self.ga.schedule = sorted(ui_sched, key=lambda e: e[0])

    def _on_sim_step(self):
        """
        Disparado por el QTimer: cada tick ejecuta un step de la GA,
        actualiza la gráfica y, si terminó, detiene el timer.
        """
        # si la simulación ha terminado
        if not self.ga.step():
            self.sim_timer.stop()
            # aquí podrías guardar en BD el último valor, etc.
            return

        # actualizar curvas en ResultsView
        t = self.ga.times[: self.ga.current_step]
        self.results_tab.curve_max.setData(t, self.ga.best_hist)
        self.results_tab.curve_avg.setData(t, self.ga.avg_hist)
        self.results_tab.curve_mort.setData(t, self.ga.kill_hist)
        self.results_tab.curve_mut.setData(t, self.ga.mut_hist)
        self.results_tab.curve_div.setData(t, self.ga.div_hist)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())