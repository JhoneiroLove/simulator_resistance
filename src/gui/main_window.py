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

        # ---- Pestañas ----
        self.tabs = QTabWidget()
        self.input_tab = InputForm()

        # Cargo antibióticos para ResultsView
        session = get_session()
        abs_q = session.query(
            Antibiotico.id, Antibiotico.nombre, Antibiotico.concentracion_minima
        ).all()
        session.close()
        antibiotics = [{"id": a[0], "nombre": a[1], "conc_min": a[2]} for a in abs_q]

        self.results_tab = ResultsView(antibiotics)
        self.results_tab.simulate_requested.connect(self.handle_simulation)
        # para recargar en caliente si cambias la tabla durante la simulación
        self.results_tab.schedule_table.cellChanged.connect(self._reload_schedule)

        self.csv_tab = CSVValidationWidget()
        self.detail_tab = DetailedResults()

        self.tabs.addTab(self.input_tab, "1. Selección y Parámetros")
        self.tabs.addTab(self.results_tab, "2. Secuencia y Simulación")
        self.tabs.addTab(self.csv_tab, "Validación CSV")
        self.tabs.addTab(self.detail_tab, "Resultados Detallados")

        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())

        # Timer para avanzar la simulación paso a paso
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._on_sim_step)

    def handle_simulation(self, schedule):
        """
        schedule: lista de (t, ab_id, conc) tal cual llega de ResultsView.
        """
        # 1) Validar genes seleccionados
        selected_genes = [
            gid for gid, cb in self.input_tab.checks.items() if cb.isChecked()
        ]
        if not selected_genes:
            QMessageBox.warning(self, "Error", "Seleccione al menos un gen.")
            self.tabs.setCurrentWidget(self.input_tab)
            return

        # 2) Leer parámetros mut/death/time
        mut_rate = self.input_tab.mut_rate_sb.value()
        death_rate = self.input_tab.death_rate_sb.value()
        time_horizon = self.input_tab.time_horizon_sb.value()

        # 3) Traducir schedule de IDs → objetos ORM
        session = get_session()
        sched_objs = []
        for t, ab_id, conc in schedule:
            ab = session.query(Antibiotico).get(ab_id)
            sched_objs.append((t, ab, conc))
        session.close()

        # 4) Instanciar GA **con** schedule inicial
        self.ga = GeneticAlgorithm(
            genes=session.query(Gen).all(),
            antibiotic_schedule=sched_objs,  # <-- aquí inyectamos tus dosis
            mutation_rate=mut_rate,
            generations=time_horizon,
            pop_size=200,
            death_rate=death_rate,
        )
        self.ga.initialize(selected_genes)

        # 5) Preparo la gráfica
        self.results_tab.clear_plot()

        # 6) Arranco el timer
        self.sim_timer.start(100)
        self.tabs.setCurrentWidget(self.results_tab)

    def _reload_schedule(self):
        """
        Cada vez que cambias la tabla de dosis **durante** la simulación,
        actualizamos self.ga.schedule para que el próximo step lo considere.
        """
        session = get_session()
        ui_sched = []
        for r in range(self.results_tab.schedule_table.rowCount()):
            ab_cb = self.results_tab.schedule_table.cellWidget(r, 0)
            conc_sb = self.results_tab.schedule_table.cellWidget(r, 1)
            if not ab_cb or not conc_sb:
                continue
            ab_id = ab_cb.currentData()
            ab = session.query(Antibiotico).get(ab_id)
            conc = conc_sb.value()
            ui_sched.append((r, ab, conc))
        session.close()
        self.ga.schedule = sorted(ui_sched, key=lambda e: e[0])

    def _on_sim_step(self):
        """
        Ejecuta un step de GA y actualiza la curva promedio (y diversidad).
        """
        if not self.ga.step():
            self.sim_timer.stop()
            return

        # Construyo el eje temporal
        t = np.linspace(0, self.ga.generations, len(self.ga.avg_hist))
        # Actualizo solo la curva promedio en la pestaña principal
        self.results_tab.curve_avg.setData(t, self.ga.avg_hist)
        # Y mantengo diversidad en su pestaña (si la necesitas)
        self.results_tab.curve_div_tab.setData(t, self.ga.div_hist)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())