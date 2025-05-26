from PyQt5.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np

class PopulationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget()
        self.plot.setBackground("#fff")
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setLabel("left", "Población Bacteriana")
        self.plot.setLabel("bottom", "Tiempo (Generaciones)")
        layout.addWidget(self.plot)

        # Curva de población
        self.curve_population = self.plot.plot(pen=pg.mkPen("#16A085", width=2))

    def update_population(self, times, population_hist):
        # Forzar que ambos tengan el mismo tamaño (toma el mínimo)
        n = min(len(times), len(population_hist))
        self.curve_population.setData(times[:n], population_hist[:n])
        self.plot.enableAutoRange()
