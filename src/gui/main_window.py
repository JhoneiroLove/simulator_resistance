# src/gui/main_window.py

import sys
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar,
    QMessageBox, QApplication,
)
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

        # Pestañas
        self.tabs = QTabWidget()
        self.input_tab = InputForm()

        # Carga de antibióticos para la pestaña de resultados
        session = get_session()
        abs_q = session.query(
            Antibiotico.id, Antibiotico.nombre, Antibiotico.concentracion_minima
        ).all()
        session.close()
        antibiotics = [
            {"id": a[0], "nombre": a[1], "conc_min": a[2]}
            for a in abs_q
        ]

        self.results_tab = ResultsView(antibiotics)
        self.results_tab.simulate_requested.connect(self.handle_simulation)

        self.csv_tab = CSVValidationWidget()
        self.detail_tab = DetailedResults()

        self.tabs.addTab(self.input_tab,   "1. Selección y Parámetros")
        self.tabs.addTab(self.results_tab, "2. Secuencia y Simulación")
        self.tabs.addTab(self.csv_tab,     "Validación CSV")
        self.tabs.addTab(self.detail_tab,  "Resultados Detallados")

        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())

    def handle_simulation(self, schedule):
        # Leer genes
        selected_genes = [
            gid for gid, cb in self.input_tab.checks.items() if cb.isChecked()
        ]
        if not selected_genes:
            QMessageBox.warning(self, "Error", "Seleccione al menos un gen.")
            self.tabs.setCurrentWidget(self.input_tab)
            return

        # Parámetros
        mut_rate     = self.input_tab.mut_rate_sb.value()
        death_rate   = self.input_tab.death_rate_sb.value()
        time_horizon = self.input_tab.time_horizon_sb.value()

        session = get_session()
        try:
            genes = session.query(Gen).all()
            sched_objs = []
            for t, ab_id, conc in schedule:
                ab = session.query(Antibiotico).get(ab_id)
                if not ab:
                    raise ValueError(f"Antibiótico con id={ab_id} no existe")
                sched_objs.append((t, ab, conc))

            # 2) Instancio el GA con los nombres de parámetros correctos
            #    y usando el time_horizon que el usuario puso en el SpinBox
            time_horizon = self.input_tab.time_horizon_sb.value()
            
            ga = GeneticAlgorithm(
                genes=genes,
                antibiotic_schedule=sched_objs,
                mutation_rate=mut_rate,
                generations=time_horizon,
                pop_size=200,
                death_rate=death_rate,
            )

            # 3) Ejecuto la simulación (ya no paso concentration ni time_unit)
            best_hist, avg_hist, kill_hist, mut_hist, diversity_hist = ga.run(
                selected_gene_ids=selected_genes,
                time_horizon=time_horizon,
            )

            # Plot dinámico
            times = np.linspace(0, time_horizon, len(best_hist))
            self.tabs.setCurrentWidget(self.results_tab)
            self.results_tab.update_plot(
                times,
                best_hist,
                avg_hist,
                mort_vals=kill_hist,
                mut_vals=mut_hist,
                div_vals=diversity_hist,
                schedule=sched_objs,
                interval_ms=100,
            )

            # Guardar resultado
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

            self.statusBar().showMessage(
                f"Simulación completada — Resistencia final: {best_hist[-1]*100:.1f}%", 5000
            )

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", str(e))
        finally:
            session.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
