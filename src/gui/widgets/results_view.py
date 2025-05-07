from PyQt5.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg

class ResultsView(QWidget):
    def __init__(self):
        super().__init__()

        # Configuración del layout
        self.layout = QVBoxLayout(self)

        # Crear widget de gráfico
        self.plot_widget = pg.PlotWidget(
            title="Evolución de la Resistencia por Generación"
        )
        self.plot_widget.setLabel("left", "Resistencia (%)")
        self.plot_widget.setLabel("bottom", "Generación")
        self.plot_widget.setBackground("w")
        self.plot = self.plot_widget.plot(pen=pg.mkPen(color="#FF5733", width=2))

        # Añadir al layout
        self.layout.addWidget(self.plot_widget)

    def update_plot(self, x_data, y_data):
        """Actualiza el gráfico con nuevos datos."""
        self.plot.setData(x_data, y_data)