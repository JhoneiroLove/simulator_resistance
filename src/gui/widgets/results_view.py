from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class ResultsView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.plot_widget = pg.PlotWidget(
            title="Evolución de la Resistencia por Generación"
        )
        self.plot_widget.setLabel("left", "Resistencia")
        self.plot_widget.setLabel("bottom", "Generación")
        self.plot_widget.setBackground("w")

        # Curvas: máximo y promedio
        self.max_curve = self.plot_widget.plot(
            pen=pg.mkPen(width=2, color="#FF5733"), name="Máximo"
        )
        self.avg_curve = self.plot_widget.plot(
            pen=pg.mkPen(width=2, color="#337BFF", style=Qt.DashLine), name="Promedio"
        )

        self.layout.addWidget(self.plot_widget)

    def update_plot(self, generations, best_history, avg_history):
        """
        generations: lista de índices de generación
        best_history: valores de fitness máximo por generación
        avg_history: valores de fitness promedio por generación
        """
        # Si quieres en %, multiplica por 100 aquí:
        # best = [v * 100 for v in best_history]
        # avg  = [v * 100 for v in avg_history]
        self.max_curve.setData(generations, best_history)
        self.avg_curve.setData(generations, avg_history)