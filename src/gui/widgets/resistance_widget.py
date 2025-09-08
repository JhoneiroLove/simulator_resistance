from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import numpy as np

def value_to_color_hex(value, thresholds, colors):
    """Convierte un valor numérico a color HEX basado en thresholds y colores."""
    for i, thresh in enumerate(thresholds):
        if value < thresh:
            r, g, b = colors[i]
            return f"#{r:02x}{g:02x}{b:02x}"
    r, g, b = colors[-1]
    return f"#{r:02x}{g:02x}{b:02x}"

class ResistanceWidget(QWidget):
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

        # Plot principal
        self.plot_main = pg.PlotWidget()
        self.plot_main.setBackground("#fff")
        self.plot_main.showGrid(x=True, y=True, alpha=0.3)
        self.plot_main.setLabel("left", "Nivel de Resistencia")
        self.plot_main.setLabel("bottom", "Tiempo (Generaciones)")
        self.plot_main.setMouseEnabled(x=False, y=False)
        plot_layout.addWidget(self.plot_main)

        # Curva principal
        self.curve_avg = self.plot_main.plot(pen=pg.mkPen("#3498DB", width=2))

        # Línea de umbral de resistencia
        self.resistance_threshold = 0.8
        self.resistance_line = pg.InfiniteLine(
            pos=self.resistance_threshold,
            angle=0,
            pen=pg.mkPen("r", width=1, style=Qt.DashLine),
            movable=False,
        )
        self.plot_main.addItem(self.resistance_line)

        # Contenedor de leyenda
        self.legend_widget = QWidget()
        self.legend_widget.setFixedWidth(220)
        legend_layout = QVBoxLayout(self.legend_widget)
        legend_layout.setContentsMargins(12, 12, 12, 12)
        legend_layout.setSpacing(12)

        # Título de leyenda
        lbl_subtitulo = QLabel("Niveles de la curva")
        lbl_subtitulo.setAlignment(Qt.AlignCenter)
        lbl_subtitulo.setStyleSheet("font-weight: bold; font-size: 13px;")
        legend_layout.addWidget(lbl_subtitulo)

        # Leyendas de colores
        lbl_res_azul = QLabel()
        lbl_res_azul.setText(
            '<span style="background-color:#0000FF;">&nbsp;&nbsp;&nbsp;&nbsp;</span> '
            "Resistencia &lt; 0.4 (Baja)"
        )
        legend_layout.addWidget(lbl_res_azul)

        lbl_res_naranja = QLabel()
        lbl_res_naranja.setText(
            '<span style="background-color:#FFA500;">&nbsp;&nbsp;&nbsp;&nbsp;</span> '
            "Resistencia 0.4 - 0.8 (Media)"
        )
        legend_layout.addWidget(lbl_res_naranja)

        lbl_res_rojo = QLabel()
        lbl_res_rojo.setText(
            '<span style="background-color:#FF0000;">&nbsp;&nbsp;&nbsp;&nbsp;</span> '
            "Resistencia ≥ 0.8 (Alta)"
        )
        legend_layout.addWidget(lbl_res_rojo)

        # Línea de umbral en leyenda
        dash_widget = QFrame()
        dash_widget.setFixedSize(20, 5)
        dash_widget.setFrameShape(QFrame.HLine)
        dash_widget.setFrameShadow(QFrame.Plain)
        dash_widget.setStyleSheet("border-top: 1px dashed red;")

        legend_layout.addSpacing(10)

        container = QWidget()
        hbox = QHBoxLayout(container)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(4)
        hbox.addWidget(dash_widget)
        hbox.addWidget(QLabel("Umbral máximo (0.8)"))
        legend_layout.addWidget(container)

        legend_layout.addSpacing(10)

        # Interpretación dinámica
        self.lbl_interpretacion_header = QLabel("Interpretación")
        self.lbl_interpretacion_header.setAlignment(Qt.AlignCenter)
        self.lbl_interpretacion_header.setStyleSheet("font-weight: bold;")
        self.lbl_interpretacion_header.setVisible(False)
        legend_layout.addWidget(self.lbl_interpretacion_header)

        self.lbl_caso_baja = QLabel(
            "Resistencia menor que 0.4, muy buena respuesta; la curva de resistencia finalizó en nivel bajo."
        )
        self.lbl_caso_baja.setWordWrap(True)
        self.lbl_caso_baja.setVisible(False)
        legend_layout.addWidget(self.lbl_caso_baja)

        self.lbl_caso_media = QLabel(
            "Resistencia entre 0.4 y 0.8, respuesta intermedia; la curva de resistencia finalizó en nivel moderado."
        )
        self.lbl_caso_media.setWordWrap(True)
        self.lbl_caso_media.setVisible(False)
        legend_layout.addWidget(self.lbl_caso_media)

        self.lbl_caso_alta = QLabel(
            "Resistencia mayor o igual a 0.8, respuesta débil; la curva de resistencia finalizó en nivel alto."
        )
        self.lbl_caso_alta.setWordWrap(True)
        self.lbl_caso_alta.setVisible(False)
        legend_layout.addWidget(self.lbl_caso_alta)

        legend_layout.addStretch()

        # Añadir al layout principal
        main_layout.addWidget(plot_container, stretch=1)
        main_layout.addWidget(self.legend_widget, stretch=0)

        # Thresholds para visualización
        self.resistance_thresholds = [0.4, 0.8]
        self._event_items = []

    def update_plot(self, times, avg_hist):
        """Actualiza el gráfico de resistencia con nuevos datos."""
        if len(times) > 0 and len(avg_hist) > 0:
            n = min(len(times), len(avg_hist))
            self.curve_avg.setData(times[:n], avg_hist[:n])

            # Cambiar color según último valor
            ultimo_valor = avg_hist[-1] if len(avg_hist) > 0 else 0
            if ultimo_valor < self.resistance_thresholds[0]:
                curvas_color = "#0000FF"  # Azul
            elif ultimo_valor < self.resistance_thresholds[1]:
                curvas_color = "#FFA500"  # Naranja
            else:
                curvas_color = "#FF0000"  # Rojo

            self.curve_avg.setPen(pg.mkPen(curvas_color, width=2))

    def clear_plot(self):
        """Limpia el gráfico."""
        self.curve_avg.setData([], [])
        # Limpiar items de eventos
        for item in self._event_items:
            self.plot_main.removeItem(item)
        self._event_items.clear()

    def add_antibiotic_markers(self, schedule):
        """Añade marcadores de antibióticos al gráfico."""
        # Mapa de colores por tipo de antibiótico
        ANTIBIOTIC_COLORS = {
            "Carbapenémico": "#2980B9",
            "Fluoroquinolona": "#F39C12",
            "Polimixina": "#E74C3C",
            "Aminoglucósido": "#27AE60",
            "Penicilina": "#8E44AD",
            "Glicilciclina": "#16A085",
        }
        DEFAULT_COLOR = "#7F8C8D"

        for t, ab, conc in schedule:
            color_line = ANTIBIOTIC_COLORS.get(ab.get("tipo", ""), DEFAULT_COLOR)
            line = pg.InfiniteLine(
                pos=t, angle=90, pen=pg.mkPen(color_line, width=2, style=Qt.DashLine)
            )
            texto = f"{ab.get('nombre', 'Antibiótico')}\n{conc:.2f}"
            label = pg.TextItem(texto, color=color_line, anchor=(0, 1))

            # Posicionar label
            y_min, y_max = self.plot_main.viewRange()[1]
            rango_y = y_max - y_min
            porcentaje = 0.08
            y_pos = y_min + rango_y * porcentaje
            label.setPos(t, y_pos)

            self.plot_main.addItem(line)
            self.plot_main.addItem(label, ignoreBounds=True)
            self._event_items.extend([line, label])

    def show_interpretation(self, final_value: float):
        """Muestra la interpretación según el valor final de resistencia."""
        self.lbl_interpretacion_header.setVisible(True)

        if final_value < self.resistance_thresholds[0]:
            self.lbl_caso_baja.setVisible(True)
            self.lbl_caso_media.setVisible(False)
            self.lbl_caso_alta.setVisible(False)
        elif final_value < self.resistance_thresholds[1]:
            self.lbl_caso_baja.setVisible(False)
            self.lbl_caso_media.setVisible(True)
            self.lbl_caso_alta.setVisible(False)
        else:
            self.lbl_caso_baja.setVisible(False)
            self.lbl_caso_media.setVisible(False)
            self.lbl_caso_alta.setVisible(True)