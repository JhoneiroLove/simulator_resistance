from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
import pyqtgraph as pg

def value_to_color_hex(value, thresholds, colors):
    """Convierte un valor numérico a color HEX basado en thresholds y colores."""
    for i, thresh in enumerate(thresholds):
        if value < thresh:
            r, g, b = colors[i]
            return f"#{r:02x}{g:02x}{b:02x}"
    r, g, b = colors[-1]
    return f"#{r:02x}{g:02x}{b:02x}"

class DegradationWidget(QWidget):
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

        # Plot de degradación
        self.plot_degradation = pg.PlotWidget()
        self.plot_degradation.setBackground("#fff")
        self.plot_degradation.showGrid(x=True, y=True, alpha=0.3)
        self.plot_degradation.setLabel("left", "Índice de Degradación")
        self.plot_degradation.setLabel("bottom", "Tiempo (Generaciones)")
        self.plot_degradation.setMouseEnabled(x=False, y=False)
        plot_layout.addWidget(self.plot_degradation)

        # Curva de degradación
        self.curve_degradation = self.plot_degradation.plot(
            pen=pg.mkPen("#FFB764", width=2)
        )

        # Widget de leyenda
        self.legend_widget = QWidget()
        self.legend_widget.setFixedWidth(200)
        legend_layout = QVBoxLayout(self.legend_widget)
        legend_layout.setContentsMargins(5, 5, 5, 5)
        legend_layout.setSpacing(8)

        # Título de leyenda
        lbl_subtitulo = QLabel("Linea de Curva")
        lbl_subtitulo.setAlignment(Qt.AlignCenter)
        lbl_subtitulo.setStyleSheet("font-weight: bold;")
        legend_layout.addWidget(lbl_subtitulo)

        # Leyendas de umbrales
        lbl_umbral_1 = QLabel()
        lbl_umbral_1.setText(
            '<span style="background-color:#008000;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Degradación &lt; 0.2 (Baja)'
        )
        legend_layout.addWidget(lbl_umbral_1)

        lbl_umbral_2 = QLabel()
        lbl_umbral_2.setText(
            '<span style="background-color:#FFA500;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Degradación 0.2 – 0.5 (Media)'
        )
        legend_layout.addWidget(lbl_umbral_2)

        lbl_umbral_3 = QLabel()
        lbl_umbral_3.setText(
            '<span style="background-color:#FF0000;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Degradación ≥ 0.5 (Alta)'
        )
        legend_layout.addWidget(lbl_umbral_3)

        legend_layout.addSpacing(10)

        # Interpretación dinámica
        self.lbl_interpretacion_header = QLabel("Interpretación")
        self.lbl_interpretacion_header.setAlignment(Qt.AlignCenter)
        self.lbl_interpretacion_header.setStyleSheet("font-weight: bold;")
        self.lbl_interpretacion_header.setVisible(False)
        legend_layout.addWidget(self.lbl_interpretacion_header)

        self.lbl_caso_baja = QLabel(
            "El pico máximo de degradación alcanzado se mantuvo por debajo de 0.2, \n"
            "lo cual indica que la actividad bacteriana se ha mantenido estable."
        )
        self.lbl_caso_baja.setWordWrap(True)
        self.lbl_caso_baja.setVisible(False)
        legend_layout.addWidget(self.lbl_caso_baja)

        self.lbl_caso_media = QLabel(
            "El valor más alto de degradación estuvo entre 0.2 y 0.5, \n"
            "lo que sugiere un inicio de deterioro en la población bacteriana."
        )
        self.lbl_caso_media.setWordWrap(True)
        self.lbl_caso_media.setVisible(False)
        legend_layout.addWidget(self.lbl_caso_media)

        self.lbl_caso_alta = QLabel(
            "El pico máximo de degradación superó 0.5, \n"
            "indicando que la bacteria se encuentra en rápida declinación."
        )
        self.lbl_caso_alta.setWordWrap(True)
        self.lbl_caso_alta.setVisible(False)
        legend_layout.addWidget(self.lbl_caso_alta)

        legend_layout.addStretch()

        # Añadir al layout principal
        main_layout.addWidget(plot_container, stretch=1)
        main_layout.addWidget(self.legend_widget, stretch=0)

        # Thresholds para visualización
        self.degradation_thresholds = [0.2, 0.5]
        self.degradation_colors = [
            (0, 128, 0),  # verde
            (255, 165, 0),  # naranja
            (255, 0, 0),  # rojo
        ]

    def update_plot(self, times, degradation_hist):
        """Actualiza el gráfico de degradación con nuevos datos."""
        if len(times) > 0 and len(degradation_hist) > 0:
            n = min(len(times), len(degradation_hist))
            self.curve_degradation.setData(times[:n], degradation_hist[:n])
            self.plot_degradation.enableAutoRange()

            # Cambiar color según último valor
            if n > 0:
                last_val = degradation_hist[n - 1]
                color_hex = value_to_color_hex(
                    last_val, self.degradation_thresholds, self.degradation_colors
                )
                self.curve_degradation.setPen(pg.mkPen(color_hex, width=2))

    def clear_plot(self):
        """Limpia el gráfico."""
        self.curve_degradation.setData([], [])

    def show_interpretation(self, peak_value: float):
        """Muestra la interpretación según el valor pico de degradación."""
        self.lbl_interpretacion_header.setVisible(True)

        if peak_value < self.degradation_thresholds[0]:
            self.lbl_caso_baja.setVisible(True)
            self.lbl_caso_media.setVisible(False)
            self.lbl_caso_alta.setVisible(False)
        elif peak_value < self.degradation_thresholds[1]:
            self.lbl_caso_baja.setVisible(False)
            self.lbl_caso_media.setVisible(True)
            self.lbl_caso_alta.setVisible(False)
        else:
            self.lbl_caso_baja.setVisible(False)
            self.lbl_caso_media.setVisible(False)
            self.lbl_caso_alta.setVisible(True)
