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
            # Traer genes y antibiótico
            genes = session.query(Gen).all()
            antibiotico = session.query(Antibiotico).get(antibiotico_id)
            if not genes or not antibiotico:
                raise ValueError("Antibiótico o lista de genes vacía")

            # Ejecutar GA: ahora devuelve dos historias
            ga = GeneticAlgorithm(
                genes, mutation_rate=0.1, generations=100, pop_size=100
            )
            best_hist, avg_hist = ga.run(selected_genes)

            # Gráficar al terminar
            gens = list(range(len(best_hist)))
            self.results_tab.update_plot(gens, best_hist, avg_hist)

            # Tomar la última resistencia (mejor) como valor final
            resistencia_predicha = best_hist[-1]

            # Guardar en BD
            sim = Simulacion(
                antibiotico_id=antibiotico.id, resistencia_predicha=resistencia_predicha
            )
            session.add(sim)
            session.commit()
            for gid in selected_genes:
                session.add(SimulacionGen(simulacion_id=sim.id, gen_id=gid))
            session.commit()

            # Actualizar UI
            self.statusBar().showMessage(
                f"Simulación completada: resistencia = {resistencia_predicha:.2%}", 5000
            )
            self.detail_tab.update_results(resistencia_predicha, antibiotico.nombre)

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