from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QObject, pyqtProperty
import pyqtgraph as pg
import numpy as np

class FadeImageItem(pg.ImageItem):
    """
    Subclase de ImageItem que expone la opacidad como propiedad animable.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opacity = kwargs.get("opacity", 1.0)

    def getOpacity(self):
        return self._opacity

    def setOpacityProp(self, val):
        self._opacity = val
        super().setOpacity(val)

    opacityProp = pyqtProperty(float, fget=getOpacity, fset=setOpacityProp)


class FadeScatterItem(pg.ScatterPlotItem):
    """
    Subclase de ScatterPlotItem que expone la opacidad como propiedad animable.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opacity = kwargs.get("opacity", 1.0)

    def getOpacity(self):
        return self._opacity

    def setOpacityProp(self, val):
        self._opacity = val
        super().setOpacity(val)

    opacityProp = pyqtProperty(float, fget=getOpacity, fset=setOpacityProp)


class ExpandWindow(QDialog):
    """
    Ventana para mostrar un mapa de calor radial de expansión bacteriana,
    donde la “fondo” (heatmap) mantiene el colormap por defecto y los
    círculos pequeños (scatter) usan un gradiente de verde a rojo.
    """

    def __init__(self, genetic_algorithm, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SRB - mapa de expansión bacteriana")
        self.setGeometry(250, 120, 850, 650)
        from ..main_window import get_app_icon
        self.setWindowIcon(get_app_icon())

        self.ga = genetic_algorithm

        # Layout vertical principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 1) Etiqueta informativa
        self.info_label = QLabel("Generación: 0    Población: 0", self)
        font = self.info_label.font()
        font.setPointSize(10)
        font.setBold(True)
        self.info_label.setFont(font)
        main_layout.addWidget(self.info_label)

        # 2) GraphicsLayoutWidget para PlotItem + ColorBarItem
        self.glw = pg.GraphicsLayoutWidget()
        main_layout.addWidget(self.glw)

        # 3) PlotItem que contendrá los heatmaps y scatteritems
        self.plot_item = self.glw.addPlot(row=0, col=0)
        vb = self.plot_item.getViewBox()
        vb.setBackgroundColor((240, 240, 240))  # gris muy claro
        self.plot_item.showGrid(x=True, y=True, alpha=0.2)
        self.plot_item.getAxis("left").setStyle(tickFont=pg.QtGui.QFont("Arial", 8))
        self.plot_item.getAxis("bottom").setStyle(tickFont=pg.QtGui.QFont("Arial", 8))
        self.plot_item.setLabel("left", "Y", **{"color": (50, 50, 50), "font-size": "9pt"})
        self.plot_item.setLabel("bottom", "X", **{"color": (50, 50, 50), "font-size": "9pt"})

        # 4) Creamos los 2 heatmap items (viejo y nuevo), ambos invisibles inicialmente
        self.heatmap_old = FadeImageItem(opacity=0.0)
        self.heatmap_new = FadeImageItem(opacity=0.0)
        self.plot_item.addItem(self.heatmap_old)
        self.plot_item.addItem(self.heatmap_new)

        # 5) Creamos los 2 scatter items (viejo y nuevo)
        self.scatter_old = FadeScatterItem(
            pen=pg.mkPen((0, 0, 0, 180), width=0.5),
            brush=pg.mkBrush(0, 0, 0, 0),
            size=0
        )
        self.scatter_old.setOpacity(0.0)

        self.scatter_new = FadeScatterItem(
            pen=pg.mkPen((0, 0, 0, 180), width=0.5),
            brush=pg.mkBrush(0, 0, 0, 0),
            size=0
        )
        self.scatter_new.setOpacity(0.0)

        self.plot_item.addItem(self.scatter_old)
        self.plot_item.addItem(self.scatter_new)

        # 6) Colormap por defecto para el heatmap (inferno)
        self.heatmap_cmap = pg.colormap.get("inferno")

        # 7) Colormap personalizado para scatter (rojo → verde)
        # Rojo = valor bajo, Verde = valor alto
        pos = np.array([0.0, 1.0])
        colors = [
            (255, 0, 0, 255),    # Rojo (bajo)
            (255, 255, 0, 255),  # Amarillo (medio)
            (0, 255, 0, 255)     # Verde (alto)
        ]
        self.scatter_cmap = pg.ColorMap([0.0, 0.5, 1.0], colors)
        # Se elimina la leyenda textual horizontal para evitar duplicidad visual

        # 8) Barra de color a la derecha, vinculada al scatter (verde→amarillo→rojo)
        self.bar = pg.ColorBarItem(
            colorMap=self.scatter_cmap,  # ¡Ahora usa el colormap de los puntos!
            width=15,
            interactive=False,
            orientation='vertical'
        )
        # No se vincula a un ImageItem, solo muestra el gradiente

        # Etiquetas de ticks en 0.0, 0.5, 1.0
        ticks = [
            (0.0, "Bajo"), (0.5, "Medio"), (1.0, "Alto")
        ]
        self.bar.setLevels((0.0, 1.0))
        self.bar.axis.setTicks([ticks])
        self.bar.axis.setStyle(tickFont=pg.QtGui.QFont("Arial", 8))
        self.glw.addItem(self.bar, row=0, col=1)

        self.margin = 10
        self._primera = True  # Para la primera actualización sin animación

        # Mostrar el primer frame sin animación
        self.update_expand(first_time=True)

    def _crossfade(self, old_item: QObject, new_item: QObject,
                   old_opacity: float, new_opacity: float, duration=300):
        """
        Anima en paralelo:
          - old_item.opacityProp: old_opacity → 0.0
          - new_item.opacityProp: 0.0 → new_opacity
        duration en milisegundos.
        """
        anim_out = QPropertyAnimation(old_item, b"opacityProp", self)
        anim_out.setDuration(duration)
        anim_out.setStartValue(old_opacity)
        anim_out.setEndValue(0.0)
        anim_out.setEasingCurve(QEasingCurve.InOutQuad)

        anim_in = QPropertyAnimation(new_item, b"opacityProp", self)
        anim_in.setDuration(duration)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(new_opacity)
        anim_in.setEasingCurve(QEasingCurve.InOutQuad)

        anim_out.start(QPropertyAnimation.DeleteWhenStopped)
        anim_in.start(QPropertyAnimation.DeleteWhenStopped)

    def update_expand(self, first_time=False):
        """
        Se llama en cada paso de la simulación para:
            1) Construir un heatmap radial de recubrimiento (sin cambiar su colormap).
            2) Dibujar scatter de letalidad/reproducción usando verde→rojo.
            3) Aplicar cross‐fade entre viejo y nuevo.
            Si first_time=True, pinta el “nuevo” directamente (sin animar).
        """
        t_idx = self.ga.current_step - 1
        if t_idx < 0:
            t_idx = 0

        poblacion_real = self.ga.population_hist[t_idx]

        # Si no hay individuos, limpiar y salir
        if len(self.ga.pop) == 0:
            self.info_label.setText(f"Generación: {self.ga.current_step}    Población: 0")
            self.scatter_old.clear()
            self.scatter_new.clear()
            self.heatmap_old.clear()
            self.heatmap_new.clear()
            return

        # Extraer atributos de la población actual
        rec_vals = np.array([ind.recubrimiento for ind in self.ga.pop])
        rep_vals = np.array([ind.reproduccion for ind in self.ga.pop])
        let_vals = np.array([ind.letalidad for ind in self.ga.pop])

        # Actualizar etiqueta superior
        self.info_label.setText(
            f"Generación: {self.ga.current_step}    Población: {int(poblacion_real)}"
        )

        # 1) Calcular heatmap radial a partir de 'recubrimiento'
        # Usamos el índice de expansión como radio máximo para una visualización más representativa
        radio_max = self.ga.expansion_index_hist[-1] * 50.0 if self.ga.expansion_index_hist else 50.0

        n_heat = max(1000, int(poblacion_real))
        angs_heat = np.random.uniform(0, 2 * np.pi, n_heat)
        radios_heat = np.random.uniform(0, radio_max, n_heat)
        xs_heat = radios_heat * np.cos(angs_heat)
        ys_heat = radios_heat * np.sin(angs_heat)

        x_min, x_max = xs_heat.min() - self.margin, xs_heat.max() + self.margin
        y_min, y_max = ys_heat.min() - self.margin, ys_heat.max() + self.margin

        bins = 50
        H, xedges, yedges = np.histogram2d(
            xs_heat, ys_heat,
            bins=bins,
            range=[[x_min, x_max], [y_min, y_max]]
        )
        H = np.flipud(H.T)
        H_norm = H / np.max(H) if H.max() > 0 else H

        # Cargar el heatmap “nuevo” usando el colormap inferno (fondo)
        self.heatmap_new.setImage(H_norm, levels=(0, 1))
        width = x_max - x_min
        height = y_max - y_min
        self.heatmap_new.setRect(x_min, y_min, width, height)
        self.heatmap_new.setLookupTable(self.heatmap_cmap.getLookupTable())

        # 2) Construir scatter de individuos (submuestreo)
        poblacion_indiv = len(self.ga.pop)
        n_scatter = min(poblacion_indiv, 300)
        indices = np.random.choice(poblacion_indiv, n_scatter, replace=False)

        angs_scat = np.random.uniform(0, 2 * np.pi, n_scatter)
        radios_scat = np.random.uniform(0, radio_max, n_scatter)
        xs_scat = radios_scat * np.cos(angs_scat)
        ys_scat = radios_scat * np.sin(angs_scat)

        let_sub = let_vals[indices]
        rep_sub = rep_vals[indices]
        tamanos = 4 + (let_sub * 8)

        diff = np.ptp(rep_sub)
        if diff < 1e-9:
            rep_norm = np.zeros_like(rep_sub)
        else:
            rep_norm = (rep_sub - rep_sub.min()) / diff

        # Para el scatter, mapeamos rep_norm [0,1] a la colormap rojo→amarillo→verde
        # Rojo = valor bajo, Amarillo = valor medio, Verde = valor alto
        brushes = [self.scatter_cmap.map(r, mode='qcolor') for r in rep_norm]
        spots_new = [
            {
                'pos': (xs_scat[i], ys_scat[i]),
                'brush': brushes[i],
                'pen': pg.mkPen((0, 0, 0, 180), width=0.5),
                'size': tamanos[i]
            }
            for i in range(n_scatter)
        ]
        self.scatter_new.setData(spots_new)

        # 3) Primera vez: mostrar “nuevo” sin animar
        if first_time or self._primera:
            self.heatmap_new.setOpacityProp(0.6)
            self.scatter_new.setOpacityProp(0.8)
            self.heatmap_old.setOpacityProp(0.0)
            self.scatter_old.setOpacityProp(0.0)
            self._primera = False

            extra = self.margin
            self.plot_item.setXRange(x_min - extra, x_max + extra, padding=0)
            self.plot_item.setYRange(y_min - extra, y_max + extra, padding=0)
            return

        # 4) Cross‐fade: animar viejo → transparente y nuevo → visible
        old_heat_op = self.heatmap_old.getOpacity()
        old_scat_op = self.scatter_old.getOpacity()
        duration = 300

        self._crossfade(self.heatmap_old, self.heatmap_new, old_heat_op, 0.6, duration)
        self._crossfade(self.scatter_old, self.scatter_new, old_scat_op, 0.8, duration)

        # 5) Intercambiar referencias para el siguiente ciclo
        self.heatmap_old, self.heatmap_new = self.heatmap_new, self.heatmap_old
        self.scatter_old, self.scatter_new = self.scatter_new, self.scatter_old

        # 6) Ajustar rangos de ejes
        extra = self.margin
        self.plot_item.setXRange(x_min - extra, x_max + extra, padding=0)
        self.plot_item.setYRange(y_min - extra, y_max + extra, padding=0)

    def reset(self):
        """
        Limpia cualquier contenido previo de heatmaps/scatters y
        restaura el estado de “primera actualización”.
        """
        self._primera = True
        self.heatmap_old.clear()
        self.heatmap_new.clear()
        self.scatter_old.clear()
        self.scatter_new.clear()
        self.update_expand(first_time=True)
