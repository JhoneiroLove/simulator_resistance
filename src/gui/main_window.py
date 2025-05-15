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

        # --- Crear widgets ---
        self.input_tab = InputForm()
        self.results_tab = ResultsView(self._load_antibiotics())
        self.csv_tab = CSVValidationWidget()
        self.detail_tab = DetailedResults()

        # --- Conectar señales ---
        # 1) Cuando guardas parámetros, muestro mensaje y voy a ResultsView
        self.input_tab.params_submitted.connect(self.on_params_saved)
        # 2) Cuando haces click en "Iniciar Simulación" en ResultsView
        self.results_tab.simulate_requested.connect(self.handle_simulation)
        # 3) Para poder recargar schedule en caliente durante ejecución
        self.results_tab.schedule_table.cellChanged.connect(self._reload_schedule)

        # --- Organizar en pestañas ---
        self.tabs = QTabWidget()
        self.tabs.addTab(self.input_tab, "1. Selección y Parámetros")
        self.tabs.addTab(self.results_tab, "2. Secuencia y Simulación")
        self.tabs.addTab(self.csv_tab, "3. Validación CSV")
        self.tabs.addTab(self.detail_tab, "4. Resultados Detallados")
        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())

        # Timer para avanzar la simulación paso a paso
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._on_sim_step)

        # Variables para almacenar parámetros guardados
        self.saved_genes = []
        self.saved_unit = None
        self.saved_mut_rate = None
        self.saved_death_rate = None
        self.saved_time_horizon = None

    def _load_antibiotics(self):
        """Lee Antibiotico.id, nombre y concentración mínima desde la BD."""
        session = get_session()
        abs_q = session.query(
            Antibiotico.id, Antibiotico.nombre, Antibiotico.concentracion_minima
        ).all()
        session.close()
        return [
            {"id": a[0], "nombre": a[1], "conc_min": a[2] or 0}
            for a in abs_q
        ]

    def on_params_saved(self, genes, unit, mut_rate, death_rate):
        """Slot que atiende input_tab.params_submitted."""
        # 1) Guardar localmente
        self.saved_genes = genes
        self.saved_unit = unit
        self.saved_mut_rate = mut_rate
        self.saved_death_rate = death_rate
        self.saved_time_horizon = self.input_tab.time_horizon_sb.value()

        # 2) Mostrar notificación de éxito
        QMessageBox.information(
            self,
            "Éxito",
            "Parámetros guardados satisfactoriamente",
            QMessageBox.Ok
        )

        # 3) Redirigir a la pestaña de resultados
        self.tabs.setCurrentWidget(self.results_tab)

    def handle_simulation(self, schedule):
        """
        schedule: lista de (t, ab_id, conc) tal cual llega de ResultsView.
        Este slot se dispara al pulsar "Iniciar Simulación".
        """
        # Asegurarnos de que haya genes guardados
        if not self.saved_genes:
            QMessageBox.warning(self, "Error", "Primero guarda los parámetros.")
            self.tabs.setCurrentWidget(self.input_tab)
            return

        # 1) Preparar schedule con objetos ORM
        session = get_session()
        sched_objs = []
        for t, ab_id, conc in schedule:
            ab = session.query(Antibiotico).get(ab_id)
            sched_objs.append((t, ab, conc))
        session.close()

        # 2) Instanciar y configurar el Algoritmo Genético
        self.ga = GeneticAlgorithm(
            genes=session.query(Gen).all(),
            antibiotic_schedule=sched_objs,
            mutation_rate=self.saved_mut_rate,
            generations=self.saved_time_horizon,
            pop_size=200,
            death_rate=self.saved_death_rate,
        )
        self.ga.initialize(self.saved_genes)

        # 3) Limpiar gráfica y arrancar timer
        self.results_tab.clear_plot()
        self.sim_timer.start(100)

    def _reload_schedule(self):
        """
        Cada vez que cambias la tabla de dosis durante la simulación,
        actualizamos self.ga.schedule para que el próximo step lo considere.
        """
        session = get_session()
        ui_sched = []
        for r in range(self.results_tab.schedule_table.rowCount()):
            ab_cb = self.results_tab.schedule_table.cellWidget(r, 0)
            conc_sb = self.results_tab.schedule_table.cellWidget(r, 1)
            if ab_cb and conc_sb:
                ab = session.query(Antibiotico).get(ab_cb.currentData())
                ui_sched.append((r, ab, conc_sb.value()))
        session.close()
        self.ga.schedule = sorted(ui_sched, key=lambda e: e[0])

    def _on_sim_step(self):
        """
        Ejecuta un step de GA y actualiza las curvas en ResultsView.
        """
        if not self.ga.step():
            self.sim_timer.stop()
            return

        # Eje temporal
        t = np.linspace(0, self.ga.generations, len(self.ga.avg_hist))
        # Actualizar gráfica promedio y diversidad
        self.results_tab.curve_avg.setData(t, self.ga.avg_hist)
        self.results_tab.curve_div_tab.setData(t, self.ga.div_hist)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
