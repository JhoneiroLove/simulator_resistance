from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class PopulationWidget(QWidget):
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

        # Plot de población
        self.plot_population = pg.PlotWidget()
        self.plot_population.setBackground("#fff")
        self.plot_population.showGrid(x=True, y=True, alpha=0.3)
        self.plot_population.setLabel("left", "Población Bacteriana (Nₜ)")
        self.plot_population.setLabel("bottom", "Tiempo (Generaciones)")
        self.plot_population.setMouseEnabled(x=False, y=False)
        plot_layout.addWidget(self.plot_population)

        # Curva de población
        self.curve_population = self.plot_population.plot(
            pen=pg.mkPen("#46BD0F", width=2)
        )

        # Widget de leyenda
        self.legend_widget = QWidget()
        self.legend_widget.setFixedWidth(200)
        legend_layout = QVBoxLayout(self.legend_widget)
        legend_layout.setContentsMargins(5, 5, 5, 5)
        legend_layout.setSpacing(6)

        # Título de umbrales
        lbl_umbral_title = QLabel("Línea de Umbral")
        lbl_umbral_title.setAlignment(Qt.AlignCenter)
        lbl_umbral_title.setStyleSheet("font-weight: bold;")
        legend_layout.addWidget(lbl_umbral_title)

        # Leyendas de umbrales
        lbl_umbral_rojo = QLabel()
        lbl_umbral_rojo.setText(
            '<span style="background-color:#FF0000;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Población ≤ 100 (Crítico)'
        )
        legend_layout.addWidget(lbl_umbral_rojo)

        lbl_umbral_amarillo = QLabel()
        lbl_umbral_amarillo.setText(
            '<span style="background-color:#FFFF00;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Población 101 – 200 (Alerta)'
        )
        legend_layout.addWidget(lbl_umbral_amarillo)

        lbl_umbral_verde = QLabel()
        lbl_umbral_verde.setText(
            '<span style="background-color:#00FF00;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Población > 200 (Normal)'
        )
        legend_layout.addWidget(lbl_umbral_verde)

        legend_layout.addSpacing(10)

        # Línea de umbral en leyenda
        umbral_hbox = QWidget()
        umbral_hbox_layout = QHBoxLayout(umbral_hbox)
        umbral_hbox_layout.setContentsMargins(0, 0, 0, 0)
        umbral_hbox_layout.setSpacing(4)

        dash_widget2 = QFrame()
        dash_widget2.setFixedSize(20, 5)
        dash_widget2.setFrameShape(QFrame.HLine)
        dash_widget2.setFrameShadow(QFrame.Plain)
        dash_widget2.setStyleSheet("border-top: 1px dashed red;")
        umbral_hbox_layout.addWidget(dash_widget2)

        lbl_umbral_text = QLabel("Umbral Máximo (100)")
        umbral_hbox_layout.addWidget(lbl_umbral_text)
        umbral_hbox_layout.addStretch()

        legend_layout.addWidget(umbral_hbox)

        legend_layout.addSpacing(10)

        # Título de curva
        lbl_subtitulo_curva = QLabel("Linea de Curva")
        lbl_subtitulo_curva.setAlignment(Qt.AlignCenter)
        lbl_subtitulo_curva.setStyleSheet("font-weight: bold;")
        legend_layout.addWidget(lbl_subtitulo_curva)

        # Leyenda de población
        lbl_pop = QLabel()
        lbl_pop.setText(
            '<span style="background-color:#46BD0F;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Tamaño de Población'
        )
        legend_layout.addWidget(lbl_pop)

        legend_layout.addSpacing(10)

        # Interpretación dinámica
        self.lbl_interpretacion_header = QLabel("Interpretación")
        self.lbl_interpretacion_header.setAlignment(Qt.AlignCenter)
        self.lbl_interpretacion_header.setStyleSheet("font-weight: bold;")
        self.lbl_interpretacion_header.setVisible(False)
        legend_layout.addWidget(self.lbl_interpretacion_header)

        self.lbl_caso_baja = QLabel("Población en zona crítica; riesgo de extinción.")
        self.lbl_caso_baja.setWordWrap(True)
        self.lbl_caso_baja.setVisible(False)
        legend_layout.addWidget(self.lbl_caso_baja)

        self.lbl_caso_media = QLabel(
            "Población en rango de advertencia; monitorear evolución."
        )
        self.lbl_caso_media.setWordWrap(True)
        self.lbl_caso_media.setVisible(False)
        legend_layout.addWidget(self.lbl_caso_media)

        self.lbl_caso_alta = QLabel(
            "Población suficientemente alta; condiciones favorables."
        )
        self.lbl_caso_alta.setWordWrap(True)
        self.lbl_caso_alta.setVisible(False)
        legend_layout.addWidget(self.lbl_caso_alta)

        legend_layout.addStretch()

        # Añadir al layout principal
        main_layout.addWidget(plot_container, stretch=1)
        main_layout.addWidget(self.legend_widget, stretch=0)

        # Configuración de umbrales
        self.extinction_threshold = 100

    def update_plot(self, times, population_hist):
        """Actualiza el gráfico de población con nuevos datos."""
        if len(times) > 0 and len(population_hist) > 0:
            n = min(len(times), len(population_hist))
            self.curve_population.setData(times[:n], population_hist[:n])
            self.plot_population.enableAutoRange()

            # Actualizar línea de umbral con color dinámico
            if hasattr(self, "extinction_line"):
                try:
                    self.plot_population.removeItem(self.extinction_line)
                except Exception:
                    pass

            current_pop = population_hist[-1] if population_hist else 0
            if current_pop > self.extinction_threshold * 2:
                umbral_color = "green"
            elif current_pop > self.extinction_threshold:
                umbral_color = "yellow"
            else:
                umbral_color = "red"

            self.extinction_line = pg.InfiniteLine(
                pos=self.extinction_threshold,
                angle=0,
                pen=pg.mkPen(umbral_color, width=1, style=Qt.DashLine),
                movable=False,
            )
            self.plot_population.addItem(self.extinction_line)

    def clear_plot(self):
        """Limpia el gráfico."""
        self.curve_population.setData([], [])
        if hasattr(self, "extinction_line"):
            try:
                self.plot_population.removeItem(self.extinction_line)
            except Exception:
                pass

    def show_interpretation(self, final_value: float):
        """Muestra la interpretación según el valor final de población."""
        self.lbl_interpretacion_header.setVisible(True)

        if final_value <= self.extinction_threshold:  # ≤ 100
            self.lbl_caso_baja.setVisible(True)
            self.lbl_caso_media.setVisible(False)
            self.lbl_caso_alta.setVisible(False)
        elif final_value <= self.extinction_threshold * 2:  # 101-200
            self.lbl_caso_baja.setVisible(False)
            self.lbl_caso_media.setVisible(True)
            self.lbl_caso_alta.setVisible(False)
        else:  # > 200
            self.lbl_caso_baja.setVisible(False)
            self.lbl_caso_media.setVisible(False)
            self.lbl_caso_alta.setVisible(True)