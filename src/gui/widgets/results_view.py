from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QBrush, QColor, QPainterPath
import pyqtgraph as pg
import numpy as np

class CustomTooltip(pg.TextItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill = QBrush(QColor(255, 255, 255, 230))
        self.border = pg.mkPen(color="#888", width=1)
        self.setZValue(1000)

    def paint(self, p, *args):
        p.setBrush(self.fill)
        p.setPen(self.border)
        path = QPainterPath()
        path.addRoundedRect(self.boundingRect(), 5, 5)
        p.drawPath(path)
        p.setPen(QColor("#333"))
        super().paint(p, *args)

class ResultsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QWidget{background:#f5f5f5;} QLabel{color:#333;}")

        # Layout principal
        self.layout = QVBoxLayout(self)

        # Título
        self.title = QLabel("Análisis de Evolución de Resistencia Bacteriana")
        self.title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Leyenda
        leg = QWidget()
        hl = QHBoxLayout(leg)
        for sym, col, txt in [
            ("●", "#E74C3C", "Resistencia Máxima"),
            ("■", "#3498DB", "Resistencia Promedio"),
            ("▲", "#9B59B6", "Mortalidad"),
            ("▼", "#F1C40F", "Mutación"),
        ]:
            lbl = QLabel(f"<span style='color:{col}'>{sym}</span> {txt}")
            lbl.setFont(QFont("Segoe UI", 9))
            hl.addWidget(lbl)
        self.layout.addWidget(leg)

        # Gráfico
        self.plot = pg.PlotWidget(title="Evolución por Tiempo")
        self.plot.setBackground("#fff")
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setLabel("left", "Nivel de Resistencia")
        self.plot.setLabel("bottom", "Tiempo")
        self.layout.addWidget(self.plot)

        # Curvas
        self.max_curve = self.plot.plot(
            pen=pg.mkPen(color="#E74C3C", width=2), symbol="o"
        )
        self.avg_curve = self.plot.plot(
            pen=pg.mkPen(color="#3498DB", width=2, style=Qt.DashLine), symbol="s"
        )
        self.mort_curve = self.plot.plot(
            pen=pg.mkPen(color="#9B59B6", width=2), symbol="t"
        )
        self.mut_curve = self.plot.plot(
            pen=pg.mkPen(color="#F1C40F", width=2), symbol="d"
        )

        # Tooltip
        self.ttip = CustomTooltip(anchor=(0.5, 1.5))
        self.plot.addItem(self.ttip, ignoreBounds=True)
        self.ttip.hide()

        # Proxy para capturar movimiento de ratón
        self.proxy = pg.SignalProxy(
            self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved
        )

        # Para limpiar anotaciones de eventos
        self._event_lines = []
        self._event_labels = []

        # Datos de la simulación
        self.times = None
        self.best = []
        self.avg = []
        self.mort = []
        self.mut = []

    def update_plot(self, times, best, avg, mort=None, mut=None, schedule=None):
        """
        Actualiza las curvas y anota los eventos de antibiótico.
        :param times: lista o np.ndarray de tiempos
        :param best: lista de valores de resistencia máxima
        :param avg: lista de valores de resistencia promedio
        :param mort: lista de tasas de mortalidad
        :param mut: lista de tasas de mutación
        :param schedule: lista de tuplas (t_evento, antibiótico_obj, concentración)
        """
        # Guardar series
        self.times = np.array(times)
        self.best = best
        self.avg = avg
        self.mort = mort or [0] * len(times)
        self.mut = mut or [0] * len(times)

        # Dibujar curvas
        self.max_curve.setData(times, best)
        self.avg_curve.setData(times, avg)
        self.mort_curve.setData(times, self.mort)
        self.mut_curve.setData(times, self.mut)

        # Limpiar anotaciones anteriores
        for item in self._event_lines + self._event_labels:
            self.plot.removeItem(item)
        self._event_lines.clear()
        self._event_labels.clear()

        # Anotar cada evento de antibiótico
        if schedule:
            ymax = max(self.best) if self.best else 1.0
            for t_evt, ab, conc in schedule:
                # Línea vertical punteada
                line = pg.InfiniteLine(
                    pos=t_evt, angle=90, pen=pg.mkPen(color="#888", style=Qt.DashLine)
                )
                self.plot.addItem(line)
                self._event_lines.append(line)

                # Etiqueta arriba de la curva
                lbl = pg.TextItem(f"{ab.nombre}\n{conc}", anchor=(0, 1))
                lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
                lbl.setPos(t_evt, ymax * 1.01)
                self.plot.addItem(lbl)
                self._event_labels.append(lbl)

    def mouseMoved(self, evt):
        """
        Muestra un tooltip con valores en el punto más cercano al ratón.
        """
        pos = evt[0]  # posición en escena
        mp = self.plot.plotItem.vb.mapSceneToView(pos)
        # Validación de datos
        if self.times is None or len(self.times) == 0:
            return

        # Índice más cercano
        idx = int(np.argmin((self.times - mp.x()) ** 2))

        # Si estamos suficientemente cerca en X, mostramos tooltip
        tol = (self.times[-1] - self.times[0]) / len(self.times)
        if abs(mp.x() - self.times[idx]) < tol:
            txt = (
                f"t={self.times[idx]:.1f}\n"
                f"Res max: {self.best[idx]:.3f}\n"
                f"Res avg: {self.avg[idx]:.3f}\n"
                f"Mortalidad: {self.mort[idx]:.3f}\n"
                f"Mutación: {self.mut[idx]:.3f}"
            )
            self.ttip.setText(txt)
            self.ttip.setPos(self.times[idx], self.best[idx])
            self.ttip.show()
        else:
            self.ttip.hide()