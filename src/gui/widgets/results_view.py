from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush, QPainterPath
import pyqtgraph as pg
import numpy as np

class CustomTooltip(pg.TextItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill = QBrush(QColor(255, 255, 255, 230))
        self.border = pg.mkPen(color="#888", width=1)
        self.setZValue(1000)
        self.setFlag(self.ItemStacksBehindParent, False)

    def paint(self, p, *args):
        p.setBrush(self.fill)
        p.setPen(self.border)
        rect = self.boundingRect()
        path = QPainterPath()
        path.addRoundedRect(rect, 5, 5)
        p.drawPath(path)
        p.setPen(QColor("#333"))
        super().paint(p, *args)

class ResultsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget { background-color: #f5f5f5; font-family: 'Segoe UI'; }
            QLabel { color: #333; }
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Título
        self.title_label = QLabel("Análisis de Evolución de Resistencia Bacteriana")
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Leyenda externa
        self._init_legend_widget()

        # Configuración del plot
        self.plot_widget = pg.PlotWidget(
            title="Evolución de la Resistencia por Generación",
            titleStyle={"color": "#333", "size": "11pt"},
        )
        self.plot_widget.setMouseEnabled(x=True, y=True)
        self.plot_widget.hideButtons()
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.setBackground("#ffffff")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel(
            "left", "Nivel de Resistencia", color="#333", size="10pt"
        )
        self.plot_widget.setLabel("bottom", "Generación", color="#333", size="10pt")
        self.plot_widget.getAxis("left").setPen(pg.mkPen(color="#666", width=1))
        self.plot_widget.getAxis("bottom").setPen(pg.mkPen(color="#666", width=1))

        # Tooltip personalizable
        self.value_label = CustomTooltip(anchor=(0.5, 1.5))
        self.value_label.setColor("#333")
        self.value_label.setFont(QFont("Segoe UI", 9))
        self.plot_widget.addItem(self.value_label, ignoreBounds=True)
        self.value_label.hide()

        # Curvas y scatter plots
        self.max_curve = self.plot_widget.plot(
            pen=pg.mkPen("#E74C3C", width=1.5),
            symbol="o",
            symbolSize=6,
            symbolBrush=("#E74C3C"),
            name="Resistencia Máxima",
        )
        self.avg_curve = self.plot_widget.plot(
            pen=pg.mkPen("#3498DB", width=1.5, style=Qt.DashLine),
            symbol="s",
            symbolSize=6,
            symbolBrush=("#3498DB"),
            name="Resistencia Promedio",
        )
        self.min_curve = self.plot_widget.plot(
            pen=pg.mkPen("#95A5A6", width=1.5, style=Qt.DotLine),
            symbol="t",
            symbolSize=6,
            symbolBrush=("#95A5A6"),
            name="Resistencia Mínima",
        )
        self.range_curve = pg.FillBetweenItem(
            self.max_curve, self.avg_curve, brush=(53, 152, 219, 50)
        )
        self.plot_widget.addItem(self.range_curve)

        self.optimal_line = pg.InfiniteLine(
            pos=1.0,
            angle=0,
            pen=pg.mkPen("#2ECC71", width=1, style=Qt.DashLine),
            label="Óptimo Teórico",
            labelOpts={"position": 0.1, "color": "#2ECC71", "fill": "#FFFFFF"},
        )
        self.plot_widget.addItem(self.optimal_line)

        self.scatter_max = pg.ScatterPlotItem(size=6, brush=QBrush(QColor("#E74C3C")))
        self.scatter_avg = pg.ScatterPlotItem(size=8, brush=QBrush(QColor("#3498DB")))
        self.scatter_min = pg.ScatterPlotItem(size=6, brush=QBrush(QColor("#95A5A6")))
        for item in (self.scatter_max, self.scatter_avg, self.scatter_min):
            self.plot_widget.addItem(item)

        # Estado interno
        self.generations = []
        self.best_history = []
        self.avg_history = []
        self.min_history = []
        self.cnt_max_history = []
        self.cnt_avg_history = []
        self.cnt_min_history = []
        self.highlight_items = []
        self.events = {}

        # Captura de movimiento de ratón
        self.proxy = pg.SignalProxy(
            self.plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved
        )
        self.layout.addWidget(self.plot_widget)

    def _init_legend_widget(self):
        legend_widget = QWidget()
        hl = QHBoxLayout(legend_widget)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(20)
        hl.setAlignment(Qt.AlignCenter)
        items = [
            ("●", "#E74C3C", "Resistencia Máxima"),
            ("■", "#3498DB", "Resistencia Promedio"),
            ("▲", "#95A5A6", "Resistencia Mínima"),
            ("★", "#F39C12", "Pico Genético"),
            ("★", "#E74C3C", "Valle Mutacional"),
        ]
        for sym, col, txt in items:
            lbl = QLabel(
                f"<span style='color:{col}; font-size:12px'>{sym}</span> {txt}"
            )
            lbl.setFont(QFont("Segoe UI", 9))
            hl.addWidget(lbl)
        self.layout.addWidget(legend_widget)

    def _highlight_extremes(self, gens, vals):
        """Detecta picos y valles y los resalta en el gráfico."""
        # Limpiar anteriores
        for item in self.highlight_items:
            self.plot_widget.removeItem(item)
        self.highlight_items.clear()
        self.events.clear()

        if len(vals) < 3:
            return

        mean, std = np.mean(vals), np.std(vals)
        up_th, lo_th = mean + 0.5 * std, mean - 0.5 * std

        for i in range(1, len(vals) - 1):
            if vals[i] > vals[i - 1] and vals[i] > vals[i + 1] and vals[i] > up_th:
                self._add_highlight(gens[i], vals[i], "Pico Genético", "#F39C12")
            elif vals[i] < vals[i - 1] and vals[i] < vals[i + 1] and vals[i] < lo_th:
                self._add_highlight(gens[i], vals[i], "Valle Mutacional", "#E74C3C")

    def _add_highlight(self, x, y, event_type, color):
        """Añade un marcador destacado y registra el evento."""
        pt = pg.ScatterPlotItem(
            [x],
            [y],
            symbol="star",
            size=12,
            pen=pg.mkPen(color, width=1),
            brush=pg.mkBrush(color),
        )
        self.plot_widget.addItem(pt)
        self.highlight_items.append(pt)
        self.events[(x, y)] = event_type

    def update_plot(
        self,
        generations,
        best_history,
        avg_history,
        min_history,
        cnt_max_history,
        cnt_avg_history,
        cnt_min_history,
    ):
        """Actualiza curvas y guarda contadores para tooltip."""
        self.generations = generations
        self.best_history = best_history
        self.avg_history = avg_history
        self.min_history = min_history
        self.cnt_max_history = cnt_max_history
        self.cnt_avg_history = cnt_avg_history
        self.cnt_min_history = cnt_min_history

        # Actualizar datos
        self.max_curve.setData(generations, best_history)
        self.avg_curve.setData(generations, avg_history)
        self.min_curve.setData(generations, min_history)
        self.range_curve.setCurves(self.max_curve, self.avg_curve)
        self.scatter_max.setData(generations, best_history, symbol="o", size=6)
        self.scatter_avg.setData(generations, avg_history, symbol="s", size=8)
        self.scatter_min.setData(generations, min_history, symbol="t", size=6)

        # Resaltar extremos
        self._highlight_extremes(generations, avg_history)

        # Ajuste de rangos
        if generations:
            x_min, x_max = min(generations), max(generations)
            x_min_plot, x_max_plot = x_min - 1, x_max + 1
            y_vals = best_history + avg_history + min_history
            y_min, y_max = min(y_vals), max(y_vals)
            span = y_max - y_min if y_max > y_min else 1.0
            margin = 0.05 * span
            self.plot_widget.setLimits(
                xMin=x_min_plot,
                xMax=x_max_plot,
                yMin=y_min - margin,
                yMax=y_max + margin,
            )
            self.plot_widget.setXRange(x_min_plot, x_max_plot)
            self.plot_widget.setYRange(y_min - margin, y_max + margin)

    def mouseMoved(self, evt):
        """Actualiza tooltip con valores y contadores de la generación más cercana."""
        pos = evt[0]
        mp = self.plot_widget.plotItem.vb.mapSceneToView(pos)
        min_d, closest, gen_idx = float("inf"), None, None

        # Buscar punto más cercano
        for idx, (x, y) in enumerate(zip(self.generations, self.best_history)):
            d = (mp.x() - x) ** 2 + (mp.y() - y) ** 2
            if d < min_d:
                min_d, closest, gen_idx = d, (x, y), idx
        for idx, (x, y) in enumerate(zip(self.generations, self.avg_history)):
            d = (mp.x() - x) ** 2 + (mp.y() - y) ** 2
            if d < min_d:
                min_d, closest, gen_idx = d, (x, y), idx
        for idx, (x, y) in enumerate(zip(self.generations, self.min_history)):
            d = (mp.x() - x) ** 2 + (mp.y() - y) ** 2
            if d < min_d:
                min_d, closest, gen_idx = d, (x, y), idx

        # Mostrar tooltip si está suficientemente cercano
        if closest and min_d < 0.05 and gen_idx is not None:
            x, y = closest
            txt = (
                f"Generación: {gen_idx}\n"
                f"Máxima: {self.best_history[gen_idx]:.3f} ({self.cnt_max_history[gen_idx]} ind.)\n"
                f"Promedio: {self.avg_history[gen_idx]:.3f} ({self.cnt_avg_history[gen_idx]} ind.)\n"
                f"Mínima: {self.min_history[gen_idx]:.3f} ({self.cnt_min_history[gen_idx]} ind.)"
            )
            self.value_label.setText(txt)
            self.value_label.setPos(x, y)
            self.value_label.show()
        else:
            self.value_label.hide()