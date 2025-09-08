from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class ExpansionWidget(QWidget):
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

        # Plot de expansión
        self.plot_expansion = pg.PlotWidget()
        self.plot_expansion.setBackground("#fff")
        self.plot_expansion.showGrid(x=True, y=True, alpha=0.3)
        self.plot_expansion.setLabel("left", "Índice de Expansión (Nₜ₊₁ / Nₜ)")
        self.plot_expansion.setLabel("bottom", "Tiempo (Generaciones)")
        self.plot_expansion.setMouseEnabled(x=False, y=False)
        plot_layout.addWidget(self.plot_expansion)

        # Curva de expansión
        self.curve_expansion = self.plot_expansion.plot(
            pen=pg.mkPen("#8E44AD", width=2)
        )

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

        # Leyenda de expansión
        lbl_exp = QLabel()
        lbl_exp.setText(
            '<span style="background-color:#8E44AD;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Índice de Expansión'
        )
        legend_layout.addWidget(lbl_exp)

        legend_layout.addStretch()

        # Añadir al layout principal
        main_layout.addWidget(plot_container, stretch=1)
        main_layout.addWidget(self.legend_widget, stretch=0)

    def update_plot(self, times, expansion_hist):
        """Actualiza el gráfico de expansión con nuevos datos."""
        if len(times) > 0 and len(expansion_hist) > 0:
            n = min(len(times), len(expansion_hist))
            self.curve_expansion.setData(times[:n], expansion_hist[:n])
            self.plot_expansion.enableAutoRange()

    def clear_plot(self):
        """Limpia el gráfico."""
        self.curve_expansion.setData([], [])
