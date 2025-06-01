from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGroupBox,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QTableWidget,
    QHeaderView,
    QMessageBox,
    QLabel,
    QFrame,
    QSizePolicy
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
import pyqtgraph as pg
import numpy as np

def value_to_color_hex(value, thresholds, colors):
    """
    Convierte un valor numérico a color HEX basado en thresholds y colores.
    thresholds: lista ordenada de umbrales (ejemplo: [0.4, 0.8])
    colors: lista de tuplas RGB correspondiente a cada rango
    """
    for i, thresh in enumerate(thresholds):
        if value < thresh:
            r, g, b = colors[i]
            return f"#{r:02x}{g:02x}{b:02x}"
    r, g, b = colors[-1]
    return f"#{r:02x}{g:02x}{b:02x}"

class ResultsView(QWidget):
    simulate_requested = pyqtSignal(list)
    optimize_requested = pyqtSignal()

    def __init__(self, antibiotics, parent=None):
        super().__init__(parent)
        self.antibiotics = antibiotics  # list of dicts: {id, nombre, conc_min}
        self._event_items = []
        self._schedule_events = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # ——— Calendario de Tratamientos ———
        grp_schedule = QGroupBox("Secuencia de Tratamientos")
        schedule_layout = QVBoxLayout(grp_schedule)

        # Columnas: Antibiótico, Concentración, Tiempo
        self.schedule_table = QTableWidget(0, 3)
        self.schedule_table.setHorizontalHeaderLabels(
            ["Antibiótico", "Concentración (mg/l)", "Tiempo (Generacion)"]
        )
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.schedule_table.setFixedHeight(120)                    
        self.schedule_table.setSizePolicy(
            QSizePolicy.Expanding, 
            QSizePolicy.Fixed
        )
        self.schedule_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.schedule_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        schedule_layout.addWidget(self.schedule_table)

        # Botones Agregar/Eliminar filas
        btn_hbox = QHBoxLayout()
        btn_add = QPushButton("Agregar")
        btn_del = QPushButton("Eliminar")
        btn_add.setFixedWidth(100)
        btn_del.setFixedWidth(100)
        btn_add.clicked.connect(self._add_schedule_row)
        btn_del.clicked.connect(self._del_schedule_row)
        btn_hbox.addWidget(btn_add)
        btn_hbox.addWidget(btn_del)
        btn_hbox.addStretch()
        schedule_layout.addLayout(btn_hbox)

        main_layout.addWidget(grp_schedule)

        # ——— Botones de acción ———
        actions_hbox = QHBoxLayout()
        actions_hbox.addStretch()

        # Botón simular
        self.run_button = QPushButton("Iniciar Simulación")
        self.run_button.clicked.connect(self._emit_simulation)
        actions_hbox.addWidget(self.run_button)

        # Botón optimizar
        self.optimize_button = QPushButton("Optimizar Tratamiento")
        self.optimize_button.setToolTip("Encuentra el plan óptimo")
        self.optimize_button.clicked.connect(lambda: self.optimize_requested.emit())
        actions_hbox.addWidget(self.optimize_button)

        main_layout.addLayout(actions_hbox)

        # ——— Pestañas de gráfica ———
        self.plot_tabs = QTabWidget()

        # • Tab Principal - Resistencia
        self.tab_main = QWidget()
        lay_main = QHBoxLayout(self.tab_main)
        lay_main.setContentsMargins(0, 0, 0, 0)
        lay_main.setSpacing(0)
        plot_container_main = QWidget()
        plot_layout_main = QVBoxLayout(plot_container_main)
        plot_layout_main.setContentsMargins(0, 0, 0, 0)
        plot_layout_main.setSpacing(0)
        self.plot_main = pg.PlotWidget()
        self.plot_main.setBackground("#fff")
        self.plot_main.showGrid(x=True, y=True, alpha=0.3)
        self.plot_main.setLabel("left", "Nivel de Resistencia")
        self.plot_main.setLabel("bottom", "Tiempo (Generaciones)")
        self.plot_main.setMouseEnabled(x=False, y=False)
        plot_layout_main.addWidget(self.plot_main)
        self.curve_avg = self.plot_main.plot(pen=pg.mkPen("#3498DB", width=2))
        self.resistance_threshold = 0.8
        self.resistance_line = pg.InfiniteLine(
            pos=self.resistance_threshold,
            angle=0,
            pen=pg.mkPen("r", width=1, style=Qt.DashLine),
            movable=False,
        )
        self.plot_main.addItem(self.resistance_line)
        self.legend_main_widget = QWidget()
        self.legend_main_widget.setFixedWidth(200)
        legend_layout_main = QVBoxLayout(self.legend_main_widget)
        legend_layout_main.setContentsMargins(5, 5, 5, 5)
        legend_layout_main.setSpacing(6)
        lbl_subtitulo = QLabel("Niveles de la curva")
        lbl_subtitulo.setAlignment(Qt.AlignCenter)
        lbl_subtitulo.setStyleSheet("font-weight: bold;")
        legend_layout_main.addWidget(lbl_subtitulo)
        lbl_res_azul = QLabel()
        lbl_res_azul.setText(
            '<span style="background-color:#0000FF;">&nbsp;&nbsp;&nbsp;&nbsp;</span> '
            'Resistencia &lt; 0.4 (Baja)'
        )
        legend_layout_main.addWidget(lbl_res_azul)
        lbl_res_naranja = QLabel()
        lbl_res_naranja.setText(
            '<span style="background-color:#FFA500;">&nbsp;&nbsp;&nbsp;&nbsp;</span> '
            'Resistencia 0.4 - 0.8 (Media)'
        )
        legend_layout_main.addWidget(lbl_res_naranja)
        lbl_res_rojo = QLabel()
        lbl_res_rojo.setText(
            '<span style="background-color:#FF0000;">&nbsp;&nbsp;&nbsp;&nbsp;</span> '
            'Resistencia ≥ 0.8 (Alta)'
        )
        legend_layout_main.addWidget(lbl_res_rojo)

        dash_widget = QFrame()
        dash_widget.setFixedSize(20, 5)            
        dash_widget.setFrameShape(QFrame.HLine)       
        dash_widget.setFrameShadow(QFrame.Plain)
        dash_widget.setStyleSheet("border-top: 1px dashed red;")
   
        legend_layout_main.addSpacing(10)
   
        container = QWidget()
        hbox = QHBoxLayout(container)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(4)                     
        hbox.addWidget(dash_widget)
        hbox.addWidget(QLabel("Umbral máximo (0.8)"))
        legend_layout_main.addWidget(container)

        legend_layout_main.addSpacing(10)

        self.lbl_interpretacion_header = QLabel("Interpretación")
        self.lbl_interpretacion_header.setAlignment(Qt.AlignCenter)
        self.lbl_interpretacion_header.setStyleSheet("font-weight: bold;")
        self.lbl_interpretacion_header.setVisible(False)
        legend_layout_main.addWidget(self.lbl_interpretacion_header)

        self.lbl_caso_baja = QLabel(
            "Resistencia menor que 0.4, muy buena respuesta; la curva de resistencia finalizó en nivel bajo."
        )
        self.lbl_caso_baja.setWordWrap(True)
        self.lbl_caso_baja.setVisible(False)
        legend_layout_main.addWidget(self.lbl_caso_baja)
        self.lbl_caso_media = QLabel(
            "Resistencia entre 0.4 y 0.8, respuesta intermedia; la curva de resistencia finalizó en nivel moderado."
        )
        self.lbl_caso_media.setWordWrap(True)
        self.lbl_caso_media.setVisible(False)
        legend_layout_main.addWidget(self.lbl_caso_media)
        self.lbl_caso_alta = QLabel(
            "Resistencia mayor o igual a 0.8, respuesta débil; la curva de resistencia finalizó en nivel alto."
        )
        self.lbl_caso_alta.setWordWrap(True)
        self.lbl_caso_alta.setVisible(False)
        legend_layout_main.addWidget(self.lbl_caso_alta)

        legend_layout_main.addStretch()

        lay_main.addWidget(plot_container_main, stretch=1)
        lay_main.addWidget(self.legend_main_widget, stretch=0)
        self.plot_tabs.addTab(self.tab_main, "Resistencia")

        # • Tab Diversidad
        self.tab_div = QWidget()
        lay_div = QHBoxLayout(self.tab_div)
        lay_div.setContentsMargins(0, 0, 0, 0)
        lay_div.setSpacing(0)

        plot_container_div = QWidget()
        plot_layout_div = QVBoxLayout(plot_container_div)
        plot_layout_div.setContentsMargins(0, 0, 0, 0)
        plot_layout_div.setSpacing(0)

        self.plot_div = pg.PlotWidget()
        self.plot_div.setBackground("#fff")
        self.plot_div.showGrid(x=True, y=True, alpha=0.3)
        self.plot_div.setLabel("left", "Diversidad")
        self.plot_div.setLabel("bottom", "Tiempo (Generaciones)")
        self.plot_div.setMouseEnabled(x=False, y=False)
        plot_layout_div.addWidget(self.plot_div)

        self.curve_div_tab = self.plot_div.plot(pen=pg.mkPen("#CC2EBF", width=2))

        self.legend_div_widget = QWidget()
        self.legend_div_widget.setFixedWidth(150)
        legend_layout_div = QVBoxLayout(self.legend_div_widget)
        legend_layout_div.setContentsMargins(5, 5, 5, 5)
        legend_layout_div.setSpacing(8)

        lbl_subtitulo_div = QLabel("Linea de Curva")
        lbl_subtitulo_div.setAlignment(Qt.AlignCenter)
        lbl_subtitulo_div.setStyleSheet("font-weight: bold;")
        legend_layout_div.addWidget(lbl_subtitulo_div)

        lbl_div = QLabel()
        lbl_div.setText('<span style="background-color:#CC2EBF;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Diversidad')
        legend_layout_div.addWidget(lbl_div)

        legend_layout_div.addStretch()

        lay_div.addWidget(plot_container_div, stretch=1)
        lay_div.addWidget(self.legend_div_widget, stretch=0)
        self.plot_tabs.addTab(self.tab_div, "Diversidad")


        # • Tab Población Bacteriana
        self.tab_population = QWidget()
        lay_pop = QHBoxLayout(self.tab_population)
        lay_pop.setContentsMargins(0, 0, 0, 0)
        lay_pop.setSpacing(0)

        plot_container_pop = QWidget()
        plot_layout_pop = QVBoxLayout(plot_container_pop)
        plot_layout_pop.setContentsMargins(0, 0, 0, 0)
        plot_layout_pop.setSpacing(0)

        self.plot_population = pg.PlotWidget()
        self.plot_population.setBackground("#fff")
        self.plot_population.showGrid(x=True, y=True, alpha=0.3)
        self.plot_population.setLabel("left", "Población Bacteriana (Nₜ)")
        self.plot_population.setLabel("bottom", "Tiempo (Generaciones)")
        self.plot_population.setMouseEnabled(x=False, y=False)
        plot_layout_pop.addWidget(self.plot_population)

        self.curve_population = self.plot_population.plot(pen=pg.mkPen("#46BD0F", width=2))

        self.legend_pop_widget = QWidget()
        self.legend_pop_widget.setFixedWidth(200)
        legend_layout_pop = QVBoxLayout(self.legend_pop_widget)
        legend_layout_pop.setContentsMargins(5, 5, 5, 5)
        legend_layout_pop.setSpacing(6)

        lbl_umbral_title = QLabel("Línea de Umbral")
        lbl_umbral_title.setAlignment(Qt.AlignCenter)
        lbl_umbral_title.setStyleSheet("font-weight: bold;")
        legend_layout_pop.addWidget(lbl_umbral_title)

        lbl_umbral_rojo = QLabel()
        lbl_umbral_rojo.setText('<span style="background-color:#FF0000;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Población ≤ 100 (Crítico)')
        legend_layout_pop.addWidget(lbl_umbral_rojo)

        lbl_umbral_amarillo = QLabel()
        lbl_umbral_amarillo.setText('<span style="background-color:#FFFF00;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Población 101 – 200 (Alerta)')
        legend_layout_pop.addWidget(lbl_umbral_amarillo)

        lbl_umbral_verde = QLabel()
        lbl_umbral_verde.setText('<span style="background-color:#00FF00;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Población > 200 (Normal)')
        legend_layout_pop.addWidget(lbl_umbral_verde)

        legend_layout_pop.addSpacing(10)

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

        legend_layout_pop.addWidget(umbral_hbox)

        legend_layout_pop.addSpacing(10)

        lbl_subtitulo_curva = QLabel("Linea de Curva")
        lbl_subtitulo_curva.setAlignment(Qt.AlignCenter)
        lbl_subtitulo_curva.setStyleSheet("font-weight: bold;")
        legend_layout_pop.addWidget(lbl_subtitulo_curva)

        lbl_pop = QLabel()
        lbl_pop.setText('<span style="background-color:#46BD0F;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Tamaño de Población')
        legend_layout_pop.addWidget(lbl_pop)

        legend_layout_pop.addSpacing(10)

        self.lbl_interpretacion_pop_header = QLabel("Interpretación")
        self.lbl_interpretacion_pop_header.setAlignment(Qt.AlignCenter)
        self.lbl_interpretacion_pop_header.setStyleSheet("font-weight: bold;")
        self.lbl_interpretacion_pop_header.setVisible(False)
        legend_layout_pop.addWidget(self.lbl_interpretacion_pop_header)

        self.lbl_caso_pop_baja = QLabel("Población en zona crítica; riesgo de extinción.")
        self.lbl_caso_pop_baja.setWordWrap(True)
        self.lbl_caso_pop_baja.setVisible(False)
        legend_layout_pop.addWidget(self.lbl_caso_pop_baja)

        self.lbl_caso_pop_media = QLabel("Población en rango de advertencia; monitorear evolución.")
        self.lbl_caso_pop_media.setWordWrap(True)
        self.lbl_caso_pop_media.setVisible(False)
        legend_layout_pop.addWidget(self.lbl_caso_pop_media)

        self.lbl_caso_pop_alta = QLabel("Población suficientemente alta; condiciones favorables.")
        self.lbl_caso_pop_alta.setWordWrap(True)
        self.lbl_caso_pop_alta.setVisible(False)
        legend_layout_pop.addWidget(self.lbl_caso_pop_alta)

        legend_layout_pop.addStretch()

        lay_pop.addWidget(plot_container_pop, stretch=1)
        lay_pop.addWidget(self.legend_pop_widget, stretch=0)
        self.plot_tabs.addTab(self.tab_population, "Población")

        # • Tab Expansión Bacteriana
        self.tab_expansion = QWidget()
        lay_exp = QHBoxLayout(self.tab_expansion)
        plot_container_exp = QWidget()
        plot_layout_exp = QVBoxLayout(plot_container_exp)
        plot_layout_exp.setContentsMargins(0, 0, 0, 0)
        plot_layout_exp.setSpacing(0)

        self.plot_expansion = pg.PlotWidget()
        self.plot_expansion.setBackground("#fff")
        self.plot_expansion.showGrid(x=True, y=True, alpha=0.3)
        self.plot_expansion.setLabel("left", "Índice de Expansión (Nₜ₊₁ / Nₜ)")
        self.plot_expansion.setLabel("bottom", "Tiempo (Generaciones)")
        self.plot_expansion.setMouseEnabled(x=False, y=False)
        plot_layout_exp.addWidget(self.plot_expansion)

        self.curve_expansion = self.plot_expansion.plot(pen=pg.mkPen("#8E44AD", width=2))

        self.legend_exp_widget = QWidget()
        self.legend_exp_widget.setFixedWidth(150)
        legend_layout_exp = QVBoxLayout(self.legend_exp_widget)
        legend_layout_exp.setContentsMargins(5, 5, 5, 5)
        legend_layout_exp.setSpacing(8)

        lbl_subtitulo_exp = QLabel("Linea de Curva")
        lbl_subtitulo_exp.setAlignment(Qt.AlignCenter)
        lbl_subtitulo_exp.setStyleSheet("font-weight: bold;")
        legend_layout_exp.addWidget(lbl_subtitulo_exp)

        lbl_exp = QLabel()
        lbl_exp.setText('<span style="background-color:#8E44AD;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Índice de Expansión')
        legend_layout_exp.addWidget(lbl_exp)

        legend_layout_exp.addStretch()

        lay_exp.addWidget(plot_container_exp, stretch=1)
        lay_exp.addWidget(self.legend_exp_widget, stretch=0)
        self.plot_tabs.addTab(self.tab_expansion, "Expansión")


        # • Tab Degradación
        self.tab_degradation = QWidget()
        lay_deg = QHBoxLayout(self.tab_degradation)
        lay_deg.setContentsMargins(0, 0, 0, 0)
        lay_deg.setSpacing(0)

        plot_container_deg = QWidget()
        plot_layout_deg = QVBoxLayout(plot_container_deg)
        plot_layout_deg.setContentsMargins(0, 0, 0, 0)
        plot_layout_deg.setSpacing(0)

        self.plot_degradation = pg.PlotWidget()
        self.plot_degradation.setBackground("#fff")
        self.plot_degradation.showGrid(x=True, y=True, alpha=0.3)
        self.plot_degradation.setLabel("left", "Índice de Degradación")
        self.plot_degradation.setLabel("bottom", "Tiempo (Generaciones)")
        self.plot_degradation.setMouseEnabled(x=False, y=False)
        plot_layout_deg.addWidget(self.plot_degradation)

        self.curve_degradation = self.plot_degradation.plot(pen=pg.mkPen("#FFB764", width=2))

        self.legend_deg_widget = QWidget()
        self.legend_deg_widget.setFixedWidth(200)
        legend_layout_deg = QVBoxLayout(self.legend_deg_widget)
        legend_layout_deg.setContentsMargins(5, 5, 5, 5)
        legend_layout_deg.setSpacing(8)

        lbl_subtitulo_deg = QLabel("Linea de Curva")
        lbl_subtitulo_deg.setAlignment(Qt.AlignCenter)
        lbl_subtitulo_deg.setStyleSheet("font-weight: bold;")
        legend_layout_deg.addWidget(lbl_subtitulo_deg)

        lbl_umbral_deg_1 = QLabel()
        lbl_umbral_deg_1.setText(
            '<span style="background-color:#008000;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Degradación &lt; 0.2 (Baja)'
        )
        legend_layout_deg.addWidget(lbl_umbral_deg_1)

        lbl_umbral_deg_2 = QLabel()
        lbl_umbral_deg_2.setText(
            '<span style="background-color:#FFA500;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Degradación 0.2 – 0.5 (Media)'
        )
        legend_layout_deg.addWidget(lbl_umbral_deg_2)

        lbl_umbral_deg_3 = QLabel()
        lbl_umbral_deg_3.setText(
            '<span style="background-color:#FF0000;">&nbsp;&nbsp;&nbsp;&nbsp;</span> Degradación ≥ 0.5 (Alta)'
        )
        legend_layout_deg.addWidget(lbl_umbral_deg_3)

        legend_layout_deg.addSpacing(10)

        self.lbl_interpretacion_deg_header = QLabel("Interpretación")
        self.lbl_interpretacion_deg_header.setAlignment(Qt.AlignCenter)
        self.lbl_interpretacion_deg_header.setStyleSheet("font-weight: bold;")
        self.lbl_interpretacion_deg_header.setVisible(False)
        legend_layout_deg.addWidget(self.lbl_interpretacion_deg_header)

        self.lbl_caso_deg_baja = QLabel(
            "El pico máximo de degradación alcanzado se mantuvo por debajo de 0.2, \n"
            "lo cual indica que la actividad bacteriana se ha mantenido estable."
        )
        self.lbl_caso_deg_baja.setWordWrap(True)
        self.lbl_caso_deg_baja.setVisible(False)
        legend_layout_deg.addWidget(self.lbl_caso_deg_baja)

        self.lbl_caso_deg_media = QLabel(
            "El valor más alto de degradación estuvo entre 0.2 y 0.5, \n"
            "lo que sugiere un inicio de deterioro en la población bacteriana."
        )
        self.lbl_caso_deg_media.setWordWrap(True)
        self.lbl_caso_deg_media.setVisible(False)
        legend_layout_deg.addWidget(self.lbl_caso_deg_media)

        self.lbl_caso_deg_alta = QLabel(
            "El pico máximo de degradación superó 0.5, \n"
            "indicando que la bacteria se encuentra en rápida declinación."
        )
        self.lbl_caso_deg_alta.setWordWrap(True)
        self.lbl_caso_deg_alta.setVisible(False)
        legend_layout_deg.addWidget(self.lbl_caso_deg_alta)

        legend_layout_deg.addStretch()

        lay_deg.addWidget(plot_container_deg, stretch=1)
        lay_deg.addWidget(self.legend_deg_widget, stretch=0)
        self.plot_tabs.addTab(self.tab_degradation, "Degradación")

        # Fin de los tabs

        main_layout.addWidget(self.plot_tabs)
        # Datos internos
        self.times = np.array([])
        self.avg_vals = np.array([])
        self.div_vals = np.array([])

        # Timer para animación
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)

        # Thresholds para visualización
        self.extinction_threshold = 100
        self.resistance_threshold = 0.8

        # Líneas horizontales para thresholds
        self.extinction_line = pg.InfiniteLine(
            pos=self.extinction_threshold,
            angle=0,
            pen=pg.mkPen("r", width=1, style=Qt.DashLine),
            movable=False,
        )
        self.resistance_line = pg.InfiniteLine(
            pos=self.resistance_threshold,
            angle=0,
            pen=pg.mkPen("r", width=1, style=Qt.DashLine),
            movable=False,
        )
        
        # Thresholds para visualización
        self.extinction_threshold = 100
        self.resistance_threshold = 0.8

        # Definir colores para resistencia y degradación
        self.resistance_thresholds = [0.4, 0.8]
        self.resistance_colors = [
            (0, 128, 0),
            (255, 165, 0),
            (255, 0, 0),
        ]  # verde, naranja, rojo

        self.degradation_thresholds = [0.2, 0.5]
        self.degradation_colors = [
            (0, 128, 0),
            (255, 165, 0),
            (255, 0, 0),
        ]  # verde, naranja, rojo

        # Líneas horizontales para thresholds
        self.extinction_line = pg.InfiniteLine(
            pos=self.extinction_threshold,
            angle=0,
            pen=pg.mkPen("r", width=1, style=Qt.DashLine),
            movable=False,
        )
        self.resistance_line = pg.InfiniteLine(
            pos=self.resistance_threshold,
            angle=0,
            pen=pg.mkPen("r", width=1, style=Qt.DashLine),
            movable=False,
        )

    def _add_schedule_row(self):
        row = self.schedule_table.rowCount()
        self.schedule_table.insertRow(row)

        # Selector de antibiótico
        ab_cb = QComboBox()
        for a in self.antibiotics:
            ab_cb.addItem(a["nombre"], a["id"])

        # SpinBox de concentración
        conc_sb = QDoubleSpinBox()
        conc_sb.setRange(0, 1e6)
        conc_sb.setValue(self.antibiotics[0].get("conc_min", 0))

        # SpinBox de tiempo (generación)
        time_sb = QDoubleSpinBox()
        time_sb.setRange(0, 1e6)
        time_sb.setValue(0)

        # Colocar en columnas
        self.schedule_table.setCellWidget(row, 0, ab_cb)
        self.schedule_table.setCellWidget(row, 1, conc_sb)
        self.schedule_table.setCellWidget(row, 2, time_sb)

    def _del_schedule_row(self):
        row = self.schedule_table.currentRow()
        if row != -1:
            self.schedule_table.removeRow(row)

    def _emit_simulation(self):
        sched = []
        for r in range(self.schedule_table.rowCount()):
            ab_id = self.schedule_table.cellWidget(r, 0).currentData()
            conc = self.schedule_table.cellWidget(r, 1).value()
            t = self.schedule_table.cellWidget(r, 2).value()
            sched.append((t, ab_id, conc))

        # Registrar eventos para dibujo
        self._schedule_events = []
        for t_evt, ab_id, conc in sched:
            name = next(
                (a["nombre"] for a in self.antibiotics if a["id"] == ab_id), str(ab_id)
            )
            self._schedule_events.append((t_evt, name, conc))

        print(f"DEBUG ResultsView._emit_simulation -> schedule={sched}")
        self.simulate_requested.emit(sched)

    def clear_plot(self):
        self.curve_avg.setData([], [])
        self.curve_div_tab.setData([], [])
        for it in self._event_items:
            self.plot_main.removeItem(it)
        self._event_items.clear()

    def _update_frame(self):
        if hasattr(self, "_idx") and self._idx >= len(self.times):
            return
        idx = self._idx
        x = self.times[: idx + 1]
        y = self.avg_vals[: idx + 1]
        self.curve_avg.setData(x, y)
        último_valor = y[-1]
        if último_valor < self.resistance_thresholds[0]:        
            curvas_color = "#008000"   
        elif último_valor < self.resistance_thresholds[1]:      
            curvas_color = "#ffa500" 
        else:
            curvas_color = "#ff0000"  
        self.curve_avg.setPen(pg.mkPen(curvas_color, width=2))
        self._idx += 1

    def show_interpretation(self, final_value: float):
        """
        Este método se llamará desde MainWindow cuando termine la simulación,
        para mostrar SOLO el texto correspondiente a final_value.
        """
        # Mostrar el encabezado “Interpretación”
        self.lbl_interpretacion_header.setVisible(True)

        # Dependiendo de final_value, mostrar únicamente el caso que corresponda:
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

    def show_population_interpretation(self, final_value: float):
        """
        Muestra solo la casuística que corresponda según final_value:
        - ≤ 100: caso crítico
        - 101–200: caso advertencia
        - > 200: caso normal
        """
        # Hacer visible el encabezado “Interpretación”
        self.lbl_interpretacion_pop_header.setVisible(True)

        # Mostrar solo la etiqueta correspondiente
        if final_value <= self.extinction_threshold:  # extinción_threshold = 100
            self.lbl_caso_pop_baja.setVisible(True)
            self.lbl_caso_pop_media.setVisible(False)
            self.lbl_caso_pop_alta.setVisible(False)
        elif final_value <= self.extinction_threshold * 2:  # 200
            self.lbl_caso_pop_baja.setVisible(False)
            self.lbl_caso_pop_media.setVisible(True)
            self.lbl_caso_pop_alta.setVisible(False)
        else:
            self.lbl_caso_pop_baja.setVisible(False)
            self.lbl_caso_pop_media.setVisible(False)
            self.lbl_caso_pop_alta.setVisible(True)
    
    def show_degradation_interpretation(self, peak_value: float):
        self.lbl_interpretacion_deg_header.setVisible(True)
        if peak_value < self.degradation_thresholds[0]:
            self.lbl_caso_deg_baja.setVisible(True)
            self.lbl_caso_deg_media.setVisible(False)
            self.lbl_caso_deg_alta.setVisible(False)
        elif peak_value < self.degradation_thresholds[1]:
            self.lbl_caso_deg_baja.setVisible(False)
            self.lbl_caso_deg_media.setVisible(True)
            self.lbl_caso_deg_alta.setVisible(False)
        else:
            self.lbl_caso_deg_baja.setVisible(False)
            self.lbl_caso_deg_media.setVisible(False)
            self.lbl_caso_deg_alta.setVisible(True)
    
    def update_degradation_plot(self, times, degradation_hist):
        n = min(len(times), len(degradation_hist))
        self.curve_degradation.setData(times[:n], degradation_hist[:n])
        self.plot_degradation.enableAutoRange()
        if n > 0:
            last_val = degradation_hist[n - 1]
            color_hex = value_to_color_hex(
                last_val, self.degradation_thresholds, self.degradation_colors
            )
            self.curve_degradation.setPen(pg.mkPen(color_hex, width=2))
        else:
            self.curve_degradation.setPen(
                pg.mkPen("#8E44AD", width=2)
            )  

    def update_population_plot(self, times, population_hist):
        n = min(len(times), len(population_hist))
        self.curve_population.setData(times[:n], population_hist[:n])
        self.plot_population.enableAutoRange()
        if hasattr(self, "extinction_line_pop"):
            try:
                self.plot_population.removeItem(self.extinction_line_pop)
            except Exception:
                pass

        current_pop = population_hist[-1] if population_hist else 0
        if current_pop > self.extinction_threshold * 2:
            umbral_color = "green"
        elif current_pop > self.extinction_threshold:
            umbral_color = "yellow"
        else:
            umbral_color = "red"

        self.extinction_line_pop = pg.InfiniteLine(
            pos=self.extinction_threshold,
            angle=0,
            pen=pg.mkPen(umbral_color, width=1, style=Qt.DashLine),
            movable=False,
        )
        self.plot_population.addItem(self.extinction_line_pop)

    def update_expansion_plot(self, times, expansion_hist):
        n = min(len(times), len(expansion_hist))
        self.curve_expansion.setData(times[:n], expansion_hist[:n])
        self.plot_expansion.enableAutoRange()


    def show_alert(self, title, message):
        QMessageBox.warning(self, title, message, QMessageBox.Ok)