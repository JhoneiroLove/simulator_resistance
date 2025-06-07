from PyQt5.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
import pyqtgraph as pg
import numpy as np

from ..main_window import get_app_icon

class PopulationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(get_app_icon())
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        plot_container = QWidget()
        plot_layout = QVBoxLayout(plot_container)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(0)
        self.plot = pg.PlotWidget()
        self.plot.setBackground("#fff")
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setLabel("left", "Población Bacteriana")
        self.plot.setLabel("bottom", "Tiempo (Generaciones)")
        plot_layout.addWidget(self.plot)
        self.curve_population = self.plot.plot(pen=pg.mkPen("#16A085", width=2))
        self.legend_pop_widget = QWidget()
        self.legend_pop_widget.setFixedWidth(150) 
        legend_layout = QVBoxLayout(self.legend_pop_widget)
        legend_layout.setContentsMargins(5, 5, 5, 5)
        legend_layout.setSpacing(8)
        lbl_pop = QLabel()
        lbl_pop.setText(
            '<span style="background-color:#16A085;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Tamaño de Población'
        )
        legend_layout.addWidget(lbl_pop)
        legend_layout.addStretch()
        main_layout.addWidget(plot_container, stretch=1)
        main_layout.addWidget(self.legend_pop_widget, stretch=0)

    def update_population(self, times, population_hist):
        n = min(len(times), len(population_hist))
        self.curve_population.setData(times[:n], population_hist[:n])
        self.plot.enableAutoRange()

