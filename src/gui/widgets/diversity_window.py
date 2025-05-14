from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtGui import QFont
import pyqtgraph as pg

class DiversityWindow(QDialog):
    def __init__(self, times, diversity_hist, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Diversidad Genética")
        self.resize(600, 400)
        layout = QVBoxLayout(self)

        # Título opcional
        title = pg.TextItem("Entropía de Shannon / Diversidad", color="#2ECC71")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))

        # PlotWidget
        self.plot = pg.PlotWidget()
        self.plot.setBackground("#fff")
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setLabel("left", "Diversidad (H)")
        self.plot.setLabel("bottom", "Tiempo")
        layout.addWidget(self.plot)

        # Pintar la serie
        self.curve = self.plot.plot(
            times,
            diversity_hist,
            pen=pg.mkPen("#2ECC71", width=2),
        )

        # Ajustar rangos
        self.plot.setXRange(times.min(), times.max())
        ymin, ymax = diversity_hist.min(), diversity_hist.max()
        self.plot.setYRange(ymin, ymax)