import sys
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QStatusBar,
    QMessageBox,
    QApplication,
)
from src.gui.widgets.input_form import InputForm
from src.gui.widgets.results_view import ResultsView
from src.gui.widgets.csv_validation import CSVValidationWidget
from src.gui.widgets.detailed_results import DetailedResults

from src.core.genetic_algorithm import GeneticAlgorithm
from src.core.metrics import exponential_growth
from src.data.database import get_session
from src.data.models import Gen, Antibiotico, Simulacion, SimulacionGen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador Evolutivo por Tratamientos")
        self.setGeometry(100, 100, 1280, 720)

        # Pestañas
        self.tabs = QTabWidget()
        self.input_tab = InputForm()
        self.results_tab = ResultsView()
        self.csv_tab = CSVValidationWidget()
        self.detail_tab = DetailedResults()

        self.tabs.addTab(self.input_tab, "Nueva Simulación")
        self.tabs.addTab(self.results_tab, "Evolución en Tiempo Real")
        self.tabs.addTab(self.csv_tab, "Validación CSV")
        self.tabs.addTab(self.detail_tab, "Resultados Detallados")

        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())

        # Conectar señal
        self.input_tab.simulation_triggered.connect(self.handle_simulation)

    def handle_simulation(
        self,
        selected_genes: list,
        schedule: list,
        time_unit: str,
        mut_rate: float,
        death_rate: float,
    ):
        """
        schedule: lista de (t, ab_id, conc)
        """
        session = get_session()
        try:
            # 1) Cargo genes y construyo el schedule con objetos Antibiotico
            genes = session.query(Gen).all()
            sched_objs = []
            for t, ab_id, conc in schedule:
                ab = session.query(Antibiotico).get(ab_id)
                if not ab:
                    raise ValueError(f"Antibiótico con id={ab_id} no existe")
                sched_objs.append((t, ab, conc))

            # 2) Instancio el GA pasándole la secuencia completa
            ga = GeneticAlgorithm(
                genes=genes,
                antibiotic_schedule=sched_objs,
                mutation_rate=mut_rate,
                generations=self.input_tab.time_horizon_sb.value(),
                pop_size=200,
                reproduction_func=exponential_growth,
                death_rate=death_rate,
            )

            # 3) Ejecuto la simulación (ya no paso concentration ni time_unit)
            best_hist, avg_hist, kill_hist, mut_hist = ga.run(
                selected_gene_ids=selected_genes,
                time_horizon=self.input_tab.time_horizon_sb.value(),
            )

            # 4) Pinto las 4 curvas en “Evolución en Tiempo Real”
            times = np.linspace(
                0, self.input_tab.time_horizon_sb.value(), len(best_hist)
            )
            self.results_tab.update_plot(
                times, best_hist, avg_hist, kill_hist, mut_hist, schedule=sched_objs
            )

            # 5) Guardo en BD la simulación final (último antibiótico)
            last_t, last_ab_id, last_conc = schedule[-1]
            sim = Simulacion(
                antibiotico_id=last_ab_id,
                concentracion=last_conc,
                resistencia_predicha=best_hist[-1],
            )
            session.add(sim)
            session.commit()
            for gid in selected_genes:
                session.add(SimulacionGen(simulacion_id=sim.id, gen_id=gid))
            session.commit()

            # 6) Solo mostramos mensaje de éxito
            self.statusBar().showMessage(
                f"Simulación completada — Resistencia final: {best_hist[-1] * 100:.1f}%",
                5000,
            )

            # Opcional: podrías actualizar aquí la pestaña de detalles
            # según el nuevo diseño que quieras para “Resultados Detallados”.

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error durante simulación", str(e))
        finally:
            session.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())