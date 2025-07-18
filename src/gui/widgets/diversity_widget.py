from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class DiversityWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Container del plot
        plot_container = QWidget()
        plot_layout = QVBoxLayout(plot_container)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(0)

        # Plot de diversidad
        self.plot_div = pg.PlotWidget()
        self.plot_div.setBackground("#fff")
        self.plot_div.showGrid(x=True, y=True, alpha=0.3)
        self.plot_div.setLabel("left", "Diversidad")
        self.plot_div.setLabel("bottom", "Tiempo (Generaciones)")
        self.plot_div.setMouseEnabled(x=False, y=False)
        plot_layout.addWidget(self.plot_div)

        # Curva de diversidad
        self.curve_div = self.plot_div.plot(pen=pg.mkPen("#CC2EBF", width=2))

        # Widget de leyenda
        self.legend_widget = QWidget()
        self.legend_widget.setFixedWidth(150)
        legend_layout = QVBoxLayout(self.legend_widget)
        legend_layout.setContentsMargins(5, 5, 5, 5)
        legend_layout.setSpacing(8)

        # Título de leyenda
        lbl_subtitulo = QLabel("Linea de Curva")
        lbl_subtitulo.setAlignment(Qt.AlignCenter)
        lbl_subtitulo.setStyleSheet("font-weight: bold;")
        legend_layout.addWidget(lbl_subtitulo)

        # Leyenda de diversidad
        lbl_div = QLabel()
        lbl_div.setText(
            '<span style="background-color:#CC2EBF;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Diversidad'
        )
        legend_layout.addWidget(lbl_div)

        legend_layout.addStretch()

        # Añadir al layout principal
        main_layout.addWidget(plot_container, stretch=1)
        main_layout.addWidget(self.legend_widget, stretch=0)

    def update_plot(self, times, div_hist):
        """Actualiza el gráfico de diversidad con nuevos datos."""
        if len(times) > 0 and len(div_hist) > 0:
            n = min(len(times), len(div_hist))
            self.curve_div.setData(times[:n], div_hist[:n])

    def clear_plot(self):
        """Limpia el gráfico."""
        self.curve_div.setData([], [])