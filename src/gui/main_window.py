import sys
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
from src.data.database import get_session
from src.data.models import Gen, Antibiotico, Simulacion, SimulacionGen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Resistencia Bacteriana")
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

        # Señal desde el formulario
        self.input_tab.simulation_triggered.connect(self.handle_simulation)

    def handle_simulation(self, antibiotico_id, selected_genes):
        session = get_session()
        try:
            # Cargar genes y antibiótico
            genes = session.query(Gen).all()
            antibiotico = session.query(Antibiotico).get(antibiotico_id)
            if not genes or not antibiotico:
                raise ValueError("Antibiótico o lista de genes vacía")

            # Ejecutar GA
            ga = GeneticAlgorithm(
                genes, mutation_rate=0.1, generations=100, pop_size=100
            )
            result = ga.run(selected_genes)

            # Desempaquetar según numero de salidas
            if len(result) == 6:
                (
                    best_hist,
                    avg_hist,
                    min_hist,
                    cnt_max_hist,
                    cnt_avg_hist,
                    cnt_min_hist,
                ) = result
            else:
                best_hist, avg_hist = result
                min_hist = cnt_max_hist = cnt_avg_hist = cnt_min_hist = None

            # Altura del eje X
            gens = list(range(len(best_hist)))

            # Actualizar gráfica
            if min_hist is not None:
                self.results_tab.update_plot(
                    gens,
                    best_hist,
                    avg_hist,
                    min_hist,
                    cnt_max_hist,
                    cnt_avg_hist,
                    cnt_min_hist,
                )
            else:
                self.results_tab.update_plot(gens, best_hist, avg_hist)

            # Mostrar pestaña de resultados
            self.tabs.setCurrentWidget(self.results_tab)

            # Métricas finales
            best_final = best_hist[-1]
            avg_final = avg_hist[-1]

            # Guardar simulación en BD
            sim = Simulacion(
                antibiotico_id=antibiotico.id, resistencia_predicha=best_final
            )
            session.add(sim)
            session.commit()
            for gid in selected_genes:
                session.add(SimulacionGen(simulacion_id=sim.id, gen_id=gid))
            session.commit()

            # Construir antibiograma
            antibiogram = []
            for ab in session.query(Antibiotico).all():
                ultima = (
                    session.query(Simulacion)
                    .filter_by(antibiotico_id=ab.id)
                    .order_by(Simulacion.fecha.desc())
                    .first()
                )
                if ultima:
                    val = ultima.resistencia_predicha
                    interp = "R" if val >= 0.5 else "S"
                else:
                    val, interp = 0.0, "N/A"
                antibiogram.append((ab.nombre, val, interp))

            # Actualizar resultados detallados
            self.detail_tab.update_results(
                avg_final, best_final, antibiotico.nombre, antibiogram
            )

            # Mostrar mensaje en la barra de estado
            self.statusBar().showMessage(
                f"Simulación completada: Promedio {avg_final:.1%} | Máxima {best_final:.1%}",
                5000,
            )

        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Error durante la simulación:\n{e}")
        finally:
            session.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())