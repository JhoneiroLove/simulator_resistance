import sys
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QMessageBox, QApplication
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

        # Configuración inicial
        self.setWindowTitle("Simulador de Resistencia Bacteriana")
        self.setGeometry(100, 100, 1280, 720)

        # Inicializar componentes
        self.tabs = QTabWidget()
        self.input_tab = InputForm()
        self.results_tab = ResultsView()
        self.csv_tab = CSVValidationWidget()
        self.detail_tab = DetailedResults()
        self.status_bar = QStatusBar()
        self.fitness_data = {"x": [], "y": []}

        # Configurar interfaz
        self.tabs.addTab(self.input_tab, "Nueva Simulación")
        self.tabs.addTab(self.results_tab, "Evolución en Tiempo Real")
        self.tabs.addTab(self.csv_tab, "Validación CSV")
        self.tabs.addTab(self.detail_tab, "Resultados Detallados")
        self.setCentralWidget(self.tabs)
        self.setStatusBar(self.status_bar)

        # Conectar señales
        self.input_tab.simulation_triggered.connect(self.handle_simulation)

    def handle_simulation(self, antibiotico_id, selected_genes):
        session = get_session()
        try:
            # Obtener datos necesarios
            genes = session.query(Gen).all()
            antibiotico = session.query(Antibiotico).get(antibiotico_id)

            if not genes or not antibiotico:
                raise ValueError("Datos de entrada inválidos")

            # Reiniciar datos del gráfico
            self.fitness_data = {"x": [], "y": []}

            # Ejecutar algoritmo genético
            ga = GeneticAlgorithm(genes)
            resistencia = ga.run(
                selected_genes, lambda gen, fit: self.update_real_time_graph(gen, fit)
            )

            # Guardar resultados en BD
            nueva_simulacion = Simulacion(
                antibiotico_id=antibiotico.id, resistencia_predicha=resistencia
            )
            session.add(nueva_simulacion)
            session.commit()

            # Registrar relación genes-simulación
            for gen_id in selected_genes:
                session.add(
                    SimulacionGen(simulacion_id=nueva_simulacion.id, gen_id=gen_id)
                )
            session.commit()

            # Actualizar UI
            self.status_bar.showMessage(
                f"Simulación completada. Resistencia: {resistencia:.2%}", 5000
            )
            self.detail_tab.update_results(resistencia, antibiotico.nombre)

        except Exception as e:
            session.rollback()
            QMessageBox.critical(
                self, "Error", f"Error durante la simulación:\n{str(e)}"
            )
        finally:
            session.close()

    def update_real_time_graph(self, generation, fitness):
        self.fitness_data["x"].append(generation)
        self.fitness_data["y"].append(fitness)
        QTimer.singleShot(0, self._update_plot_ui)

    def _update_plot_ui(self):
        self.results_tab.update_plot(self.fitness_data["x"], self.fitness_data["y"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())