# src/gui/widgets/map_window.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QObject, pyqtProperty, QPointF
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from scipy.spatial import Voronoi
from scipy.interpolate import griddata

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


class FadePolygonItem(pg.GraphicsObject):
    """
    Subclase para mostrar polígonos con cross‐fade, exponiendo la opacidad
    como propiedad animable y permitiendo actualizar datos con setData().
    """
    def __init__(self, polygons=None, colors=None, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        self.polygons = polygons or []
        self.colors = colors or []
        self._bounding_rect = pg.QtCore.QRectF()
        self._border_width = 1.0
        self._border_color = QColor(0, 0, 0, 180)
        self._highlight_factor = 0.2
        self.generatePicture()

    def getOpacity(self):
        return self._opacity

    def setOpacityProp(self, val):
        # 1) Actualizar opacidad interna
        self._opacity = val
        # 2) Volver a generar dibujo con la nueva opacidad
        self.generatePicture()
        # 3) Forzar repaint
        self.update()

    opacityProp = pyqtProperty(float, fget=getOpacity, fset=setOpacityProp)

    def setBorderStyle(self, width=1.0, color=None):
        """Configurar estilo del borde de las regiones."""
        self._border_width = width
        if color:
            self._border_color = QColor(color)
        self.generatePicture()
        self.update()

    def setHighlightFactor(self, factor):
        """Ajustar cuánto se resaltan los colores."""
        self._highlight_factor = factor
        self.generatePicture()
        self.update()

    def setData(self, polygons, colors):
        """
        Actualiza la lista de polígonos y colores, genera el picture y repinta.
        Así es posible llamar desde fuera: setData(polygons, colors).
        """
        self.polygons = polygons or []
        self.colors = colors or []
        self.generatePicture()
        self.update()

    def generatePicture(self):
        """Construye internamente el QPicture con polígonos coloreados y opacidad."""
        self.picture = pg.QtGui.QPicture()
        painter = pg.QtGui.QPainter(self.picture)

        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = -float('inf'), -float('inf')

        for polygon, color in zip(self.polygons, self.colors):
            if len(polygon) < 3:
                continue

            # Convertir a QPolygonF
            qpoints = [QPointF(x, y) for x, y in polygon]
            qpolygon = pg.QtGui.QPolygonF(qpoints)

            # Actualizar bounding rect
            for x, y in polygon:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

            # Color base mejorado
            base_color = QColor(color)
            # Crear color resaltado
            h, s, v, a = base_color.getHsvF()
            s = min(1.0, s + self._highlight_factor)
            v = min(1.0, v + self._highlight_factor/2)
            highlighted_color = QColor.fromHsvF(h, s, v, a)

            # Ajustar la opacidad del color resaltado
            highlighted_color.setAlphaF(self._opacity * a)

            # Borde más oscuro con opacidad
            border_color = QColor(base_color).darker(150)
            border_color.setAlphaF(self._opacity * 0.8)

            # Dibujar sombra
            painter.setPen(Qt.NoPen)
            shadow_color = QColor(0, 0, 0, int(50 * self._opacity))
            painter.setBrush(QBrush(shadow_color))
            shadow_polygon = qpolygon.translated(2, 2)
            painter.drawPolygon(shadow_polygon)

            # Dibujar relleno
            painter.setBrush(QBrush(highlighted_color))
            painter.setPen(QPen(border_color, self._border_width))
            painter.drawPolygon(qpolygon)

        painter.end()

        if min_x != float('inf'):
            self._bounding_rect = pg.QtCore.QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
        else:
            self._bounding_rect = pg.QtCore.QRectF()

    def paint(self, p, *args):
        # Pintar todo el QPicture con la opacidad global
        p.setOpacity(self._opacity)
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return self._bounding_rect


class MapWindow(QDialog):
    """
    Muestra un mapa de expansión bacteriana con:
      1) Dos ImageItems (viejo/nuevo) para heatmap con cross‐fade.
      2) Dos PolygonItems (viejo/nuevo) para regiones con cross‐fade.
      3) Barra de color a la derecha, vinculada al heatmap "nuevo".
      4) Animaciones suaves de 300 ms en cada actualización.
      5) Etiqueta superior con "Generación" y "Población real".
    """
    def __init__(self, genetic_algorithm, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mapa de Expansión Bacteriana (Regiones)")
        self.setGeometry(200, 100, 850, 650)

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

        # 3) PlotItem que contendrá los heatmaps y polygon items
        self.plot_item = self.glw.addPlot(row=0, col=0)
        vb = self.plot_item.getViewBox()
        vb.setBackgroundColor((240, 240, 240))  # gris muy claro
        self.plot_item.showGrid(x=True, y=True, alpha=0.2)
        self.plot_item.getAxis("left").setStyle(tickFont=pg.QtGui.QFont("Arial", 8))
        self.plot_item.getAxis("bottom").setStyle(tickFont=pg.QtGui.QFont("Arial", 8))
        self.plot_item.setLabel("left", "Y", **{"color": (50,50,50), "font-size": "9pt"})
        self.plot_item.setLabel("bottom", "X", **{"color": (50,50,50), "font-size": "9pt"})

        # 4) Creamos los 2 heatmap items (viejo y nuevo)
        self.heatmap_old = FadeImageItem(opacity=0.0)
        self.heatmap_new = FadeImageItem(opacity=0.0)
        self.plot_item.addItem(self.heatmap_old)
        self.plot_item.addItem(self.heatmap_new)

        self.region_old = FadePolygonItem()
        self.region_old.setBorderStyle(width=1.5, color="#333333")  # Borde más oscuro
        self.region_old.setHighlightFactor(0.25)  # Colores más vivos
        self.region_old.setOpacityProp(0.0)

        self.region_new = FadePolygonItem()
        self.region_new.setBorderStyle(width=1.5, color="#333333")
        self.region_new.setHighlightFactor(0.25)
        self.region_new.setOpacityProp(0.0)

        self.plot_item.addItem(self.region_old)
        self.plot_item.addItem(self.region_new)

        # 6) Barra de color (ColorBarItem) a la derecha, vinculada al heatmap_new
        self.color_map = pg.colormap.get("viridis")
        self.bar = pg.ColorBarItem(
            colorMap=self.color_map,
            width=20,
            interactive=False,
            orientation='vertical',
            label="Tasa de Reproducción"
        )
        self.bar.setImageItem(self.heatmap_new)
        ticks = [(0.0, "0.0"), (0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6"), (0.8, "0.8"), (1.0, "1.0")]
        self.bar.setLevels((0.0, 1.0))
        self.bar.axis.setTicks([ticks])
        self.bar.axis.setStyle(tickFont=pg.QtGui.QFont("Arial", 8))
        self.glw.addItem(self.bar, row=0, col=1)

        self.margin = 10

        # Flag para saber si estamos en la primera llamada (no hay nada que fade‐out aún)
        self._primera = True

        # Mostrar el primer frame sin animación
        self.update_map(first_time=True)

    def _crossfade(self, old_item: QObject, new_item: QObject, old_opacity: float, new_opacity: float, duration=300):
        """
        Anima en paralelo:
          - old_item.opacityProp: old_opacity → 0.0
          - new_item.opacityProp: 0.0 → new_opacity
        duration en ms.
        """
        # Animación para el heatmap/region viejo
        anim_out = QPropertyAnimation(old_item, b"opacityProp", self)
        anim_out.setDuration(duration)
        anim_out.setStartValue(old_opacity)
        anim_out.setEndValue(0.0)
        anim_out.setEasingCurve(QEasingCurve.InOutQuad)

        # Animación para el heatmap/region nuevo
        anim_in = QPropertyAnimation(new_item, b"opacityProp", self)
        anim_in.setDuration(duration)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(new_opacity)
        anim_in.setEasingCurve(QEasingCurve.InOutQuad)

        # Ejecutamos simultáneamente (sin agrupación explícita)
        anim_out.start(QPropertyAnimation.DeleteWhenStopped)
        anim_in.start(QPropertyAnimation.DeleteWhenStopped)

    def _create_voronoi_regions(self, points, values, bounds):
        """
        Crea regiones de Voronoi a partir de puntos y valores.
        Devuelve polígonos y colores para cada región.
        """
        if len(points) < 3:
            return [], []
            
        # Calcular diagrama de Voronoi
        vor = Voronoi(points)
        
        polygons = []
        colors = []
        
        # Mapear valores a colores
        min_val, max_val = min(values), max(values)
        val_range = max_val - min_val if max_val > min_val else 1.0
        
        for i, point in enumerate(points):
            region_idx = vor.point_region[i]
            region = vor.regions[region_idx]
            
            if -1 in region or len(region) < 3:
                continue
                
            # Obtener vértices del polígono
            polygon = [vor.vertices[v] for v in region]
            
            # Normalizar valor para color
            norm_val = (values[i] - min_val) / val_range
            color = self.color_map.map(norm_val, mode='qcolor')
            
            polygons.append(polygon)
            colors.append(color)
            
        return polygons, colors

    def _create_grid_regions(self, points, values, bounds, grid_size=20):
        """
        Crea regiones basadas en interpolación en una grilla.
        """
        if len(points) < 3:
            return [], []
            
        # Crear grilla
        xi = np.linspace(bounds[0], bounds[1], grid_size)
        yi = np.linspace(bounds[2], bounds[3], grid_size)
        xi, yi = np.meshgrid(xi, yi)
        
        # Interpolar valores
        zi = griddata(points, values, (xi, yi), method='cubic')
        
        polygons = []
        colors = []
        
        # Mapear valores a colores
        min_val, max_val = np.nanmin(zi), np.nanmax(zi)
        val_range = max_val - min_val if max_val > min_val else 1.0
        
        # Crear polígonos para cada celda
        for i in range(grid_size-1):
            for j in range(grid_size-1):
                if np.isnan(zi[i,j]) or np.isnan(zi[i+1,j]) or np.isnan(zi[i,j+1]) or np.isnan(zi[i+1,j+1]):
                    continue
                    
                # Valor promedio de la celda
                cell_val = np.mean([zi[i,j], zi[i+1,j], zi[i,j+1], zi[i+1,j+1]])
                norm_val = (cell_val - min_val) / val_range
                color = self.color_map.map(norm_val, mode='qcolor')
                
                # Crear polígono cuadrangular
                polygon = [
                    (xi[i,j], yi[i,j]),
                    (xi[i+1,j], yi[i+1,j]),
                    (xi[i+1,j+1], yi[i+1,j+1]),
                    (xi[i,j+1], yi[i,j+1])
                ]
                
                polygons.append(polygon)
                colors.append(color)
                
        return polygons, colors

    def update_map(self, first_time=False):
        """
        Actualiza el mapa mostrando regiones en lugar de puntos.
        """
        # 1) Índice de generación actual
        t_idx = self.ga.current_step - 1
        if t_idx < 0:
            t_idx = 0

        # 2) Obtener población y atributos
        poblacion_real = self.ga.population_hist[t_idx]
        if len(self.ga.pop) == 0:
            # Si no hay individuos aún, limpiamos y salimos
            self.info_label.setText(f"Generación: {self.ga.current_step}    Población: 0")
            self.region_old.setData([], [])
            self.region_new.setData([], [])
            self.heatmap_old.clear()
            self.heatmap_new.clear()
            return

        rec_vals = np.array([ind.recubrimiento for ind in self.ga.pop])
        rep_vals = np.array([ind.reproduccion  for ind in self.ga.pop])
        let_vals = np.array([ind.letalidad    for ind in self.ga.pop])

        # Actualizamos la etiqueta con generación y población
        self.info_label.setText(
            f"Generación: {self.ga.current_step}    Población: {int(poblacion_real)}"
        )

        # 3) Heatmap de densidad
        rec_mean = float(np.mean(rec_vals)) if rec_vals.size > 0 else 0.0
        radio_max = rec_mean * 50.0

        n_heat = max(1000, int(poblacion_real))
        angs_heat = np.random.uniform(0, 2*np.pi, n_heat)
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

        # Cargamos el "nuevo" heatmap en heatmap_new
        self.heatmap_new.setImage(H_norm, levels=(0, 1))
        width = x_max - x_min
        height = y_max - y_min
        self.heatmap_new.setRect(x_min, y_min, width, height)
        self.heatmap_new.setLookupTable(self.color_map.getLookupTable())

        # 4) Regiones basadas en atributos
        poblacion_indiv = len(self.ga.pop)
        n_regions = min(poblacion_indiv, 100)  # Usamos menos puntos para las regiones

        indices = np.random.choice(poblacion_indiv, n_regions, replace=False)

        angs_reg = np.random.uniform(0, 2*np.pi, n_regions)
        radios_reg = np.random.uniform(0, radio_max, n_regions)
        xs_reg = radios_reg * np.cos(angs_reg)
        ys_reg = radios_reg * np.sin(angs_reg)
        
        # Usar reproducción como valor para colorear las regiones
        rep_reg = rep_vals[indices]
        
        # Crear regiones usando interpolación en grilla
        bounds = [x_min, x_max, y_min, y_max]
        polygons, colors = self._create_grid_regions(
            np.column_stack((xs_reg, ys_reg)),
            rep_reg,
            bounds,
            grid_size=25
        )
        
        # Cargar los datos en region_new
        self.region_new.setData(polygons, colors)

        # 5) Si es la primera vez, dejamos "nuevo" directo, sin animar
        if first_time or self._primera:
            self.heatmap_new.setOpacityProp(0.5)
            self.region_new.setOpacityProp(0.85)
            self.heatmap_old.setOpacityProp(0.0)
            self.region_old.setOpacityProp(0.0)
            # Después de mostrar "nuevo" una vez, pasamos a false
            self._primera = False
            # Ajustar rangos de ejes
            extra = self.margin
            self.plot_item.setXRange(x_min - extra, x_max + extra, padding=0)
            self.plot_item.setYRange(y_min - extra, y_max + extra, padding=0)
            return

        # 6) Cross‐fade: animamos opacity de old → 0 y new → 0.6/0.7
        old_heat_op = self.heatmap_old.getOpacity()
        old_region_op = self.region_old.getOpacity()
        
        duration = 300

        # Animamos heatmap
        self._crossfade(self.heatmap_old, self.heatmap_new, old_heat_op, 0.6, duration)
        # Animamos regiones
        self._crossfade(self.region_old, self.region_new, old_region_op, 0.7, duration)

        # 7) Tras iniciar el cross‐fade, intercambiamos referencias:
        self.heatmap_old, self.heatmap_new = self.heatmap_new, self.heatmap_old
        self.region_old, self.region_new = self.region_new, self.region_old

        # 8) Ajustar rangos de ejes
        extra = self.margin
        self.plot_item.setXRange(x_min - extra, x_max + extra, padding=0)
        self.plot_item.setYRange(y_min - extra, y_max + extra, padding=0)

    def reset(self):
        """
        Limpia cualquier contenido previo de heatmaps/regiones,
        vuelve a poner _primera=True y redibuja el frame inicial.
        """
        # 1) Marcar que vamos a volver a pintar como si fuese la primera vez
        self._primera = True

        # 2) Borrar datos antiguos de heatmap y regiones
        self.heatmap_old.clear()
        self.heatmap_new.clear()
        self.region_old.setData([], [])
        self.region_new.setData([], [])

        self.update_map(first_time=True)