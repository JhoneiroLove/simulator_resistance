import sys
import numpy as np
import pyqtgraph as pg
import sys, os
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QStatusBar,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import QTimer, Qt
from src.gui.widgets.map_window import MapWindow
from src.gui.widgets.input_form import InputForm
from src.gui.widgets.results_view import ResultsView
from src.gui.widgets.csv_validation import CSVValidationWidget
from src.gui.widgets.detailed_results import DetailedResults
from src.gui.widgets.expand_window import ExpandWindow
from src.core.genetic_algorithm import GeneticAlgorithm

from src.data.database import get_session
from src.data.models import Gen, Antibiotico, Recomendacion
from src.data.models import Simulacion
from PyQt5.QtGui import QIcon

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

def get_app_icon():
    if hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.abspath(os.path.dirname(__file__))
    icon_path = os.path.join(base_dir, 'simulador_evolutivo.ico')
    if not os.path.exists(icon_path):
        icon_path = os.path.join(base_dir, '..', '..', 'simulador_evolutivo.ico')
    return QIcon(icon_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRB")
        self.resize(1280, 720)
        # Centrar la ventana en la pantalla
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowIcon(get_app_icon())

        # ---- Widgets principales ----
        self.input_tab = InputForm()
        
        session = get_session()
        abs_q = session.query(
            Antibiotico.id, Antibiotico.nombre, Antibiotico.concentracion_minima, Antibiotico.concentracion_maxima
        ).all()
        session.close()
        antibiotics = [{"id": a[0], "nombre": a[1], "conc_min": a[2], "conc_max": a[3]} for a in abs_q]
        self.map_window = None
        self.expand_window = None 
        self.results_tab = ResultsView(antibiotics)
        self.csv_tab = CSVValidationWidget()
        self.detail_tab = DetailedResults()

        # ---- Conectar señales ----
        self.input_tab.params_submitted.connect(self.on_params_saved)
        self.results_tab.simulate_requested.connect(self.handle_simulation)


        # ---- Pestañas ----
        self.tabs = QTabWidget()
        self.tabs.addTab(self.input_tab, "1. Selección y Parámetros")
        self.tabs.addTab(self.results_tab, "2. Secuencia y Simulación")
        self.tabs.addTab(self.csv_tab, "3. Validación CSV")
        self.tabs.addTab(self.detail_tab, "4. Resultados Detallados")
        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())

        # ---- Timer para animación ----
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._on_sim_step)

        # ---- Parámetros guardados ----
        self.saved_genes = []
        self.saved_mut_rate = 0.05
        self.saved_death_rate = 0.05
        self.saved_time_horizon = 100
        self.saved_environmental_factors = {"temperature": 37.0, "pH": 7.4}

        # Flags para mostrar alertas solo una vez
        self.alert_shown_extinction = False
        self.alert_shown_resistance = False

    def on_params_saved(
        self, genes, unit, mut_rate, death_rate, time_horizon, environmental_factors
    ):
        """Se llama cuando el usuario guarda parámetros en la pestaña 1."""
        self.saved_genes = genes
        self.saved_mut_rate = mut_rate
        self.saved_death_rate = death_rate
        self.saved_time_horizon = time_horizon
        self.saved_environmental_factors = environmental_factors
        QMessageBox.information(
            self,
            "Éxito",
            "Parámetros guardados satisfactoriamente",
            QMessageBox.Ok,
        )
        self.tabs.setCurrentWidget(self.results_tab)

    def handle_simulation(self, schedule):
        if not self.saved_genes:
            QMessageBox.warning(self, "Error", "Seleccione al menos un gen.")
            self.tabs.setCurrentWidget(self.input_tab)
            return

        # Recuperar información de genes desde la base de datos
        session = get_session()
        genes_orm = session.query(Gen).all()
        genes = [
            {"id": g.id, "nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_orm
        ]
        session.close()

        # Construir la lista de tuplas (tiempo, antibiótico, concentración)
        sched_objs = []
        session = get_session()
        for t, ab_id, conc in schedule:
            ab_orm = session.query(Antibiotico).get(ab_id)
            ab = {
                "id": ab_orm.id,
                "nombre": ab_orm.nombre,
                "tipo": ab_orm.tipo,
                "concentracion_minima": ab_orm.concentracion_minima,
                "concentracion_maxima": ab_orm.concentracion_maxima,
            }
            sched_objs.append((t, ab, conc))
        session.close()

        # Determinar el primer antibiótico y concentración (para guardar la simulación)
        if sched_objs:
            antibiotico_id = sched_objs[0][1]["id"]
            concentracion = sched_objs[0][2]
        else:
            antibiotico_id = None
            concentracion = None

        # Crear registro de Simulación en la base de datos
        session = get_session()
        simulacion = Simulacion(
            antibiotico_id=antibiotico_id,
            concentracion=concentracion if concentracion is not None else 0.0,
            resistencia_predicha=0.0,
        )
        session.add(simulacion)
        session.commit()
        simulation_id = simulacion.id
        session.close()

        # Guardar horarios manuales y despejar cualquier horario optimizado previo
        self._manual_schedule = sched_objs
        self._optimized_schedule = None

        # Instanciar el algoritmo genético con los parámetros
        self.ga = GeneticAlgorithm(
            genes=genes,
            antibiotic_schedule=sched_objs,
            mutation_rate=self.saved_mut_rate,
            generations=self.saved_time_horizon,
            pop_size=200,
            death_rate=self.saved_death_rate,
            environmental_factors=self.saved_environmental_factors,
            simulation_id=simulation_id,
            pressure_factor=0.25,  # Reducir la presión para fomentar supervivencia
        )
        self.ga.initialize(self.saved_genes)

        # --- Posicionamiento de ventanas de gráficos ---
        main_window_geom = self.geometry()
        screen = QApplication.primaryScreen().geometry()
        margin = 10

        # Crear/actualizar y posicionar la ventana del mapa de calor a la izquierda
        if self.map_window is None:
            self.map_window = MapWindow(self.ga)
        else:
            self.map_window.ga = self.ga
            self.map_window.reset()
        
        map_geom = self.map_window.frameGeometry()
        map_x = main_window_geom.x() - map_geom.width() - margin
        map_x = max(0, map_x)  # Asegurarse de que no se salga de la pantalla
        self.map_window.move(map_x, main_window_geom.y())
        self.map_window.show()

        # Crear/actualizar y posicionar la ventana de expansión a la derecha
        if self.expand_window is None:
            self.expand_window = ExpandWindow(self.ga)
        else:
            self.expand_window.ga = self.ga
            self.expand_window.reset()

        expand_geom = self.expand_window.frameGeometry()
        expand_x = main_window_geom.x() + main_window_geom.width() + margin
        # Asegurarse de que no se salga de la pantalla
        if expand_x + expand_geom.width() > screen.width():
            expand_x = screen.width() - expand_geom.width()
        self.expand_window.move(expand_x, main_window_geom.y())
        self.expand_window.show()

        # Limpiar gráfica en la pestaña de resultados y arrancar el timer
        self.results_tab.clear_plot()
        self.sim_timer.start(100)
        self.tabs.setCurrentWidget(self.results_tab)

        # Reiniciar flags de alerta
        self.alert_shown_extinction = False
        self.alert_shown_resistance = False

    def _on_sim_step(self):
        """Avanza la simulación paso a paso y al final actualiza Resultados Detallados."""
        if not self.ga.step():
            self.sim_timer.stop()
            self._show_threshold_alerts()

            self.ga.save_final_gene_attributes(self.saved_genes)

            # Dibujar líneas de eventos (manual u óptimo)
            schedule = self._optimized_schedule or self._manual_schedule or []
            for t, ab, conc in schedule:
                # 1) Obtén el color según el tipo de antibiótico
                color_line = ANTIBIOTIC_COLORS.get(ab["tipo"], DEFAULT_COLOR)

                # 2) Dibuja la línea vertical en t con ese color
                line = pg.InfiniteLine(
                    pos=t,
                    angle=90,
                    pen=pg.mkPen(color_line, width=2, style=Qt.DashLine)
                )

                # 3) Prepara el texto (nombre + concentración) con el mismo color
                texto = f"{ab['nombre']}\n{conc:.2f}"
                label = pg.TextItem(texto, color=color_line, anchor=(0, 1))

                # 4) Colócalo un poco por encima de y_min (porcentaje del rango en Y)
                y_min, y_max = self.results_tab.plot_main.viewRange()[1]
                rango_y = y_max - y_min
                porcentaje = 0.08  # 8% por encima de y_min
                y_pos = y_min + rango_y * porcentaje
                label.setPos(t, y_pos)

                # 5) Añádelo sin que modifique el auto-rango
                self.results_tab.plot_main.addItem(line)
                self.results_tab.plot_main.addItem(label, ignoreBounds=True)

                # 6) Guarda referencias para luego poder limpiar
                self.results_tab._event_items.extend([line, label])

            # Construir lista de resultados por antibiótico
            session = get_session()
            antibioticos_results = []
            for t_evt, ab, _ in schedule:
                # buscamos el índice de la generación más cercana a t_evt
                idx = np.searchsorted(self.ga.times, t_evt, side="right") - 1
                valor = self.ga.avg_hist[idx]  # supervivencia/promedio en ese instante
                # cargamos la recomendación de BD
                reco = (
                    session.query(Recomendacion)
                    .filter_by(antibiotico_id=ab["id"])
                    .first()
                )
                texto = reco.texto if reco else ""
                antibioticos_results.append((ab["nombre"], valor, texto))
            session.close()

            # Actualizar pestaña 4: Resultados Detallados
            self.detail_tab.update_results(
                avg_resistencia=self.ga.avg_hist[-1],
                max_resistencia=max(self.ga.best_hist),
                antibiotico="Plan de Tratamiento",
                antibioticos_results=antibioticos_results,
                best_hist=self.ga.best_hist,
                avg_hist=self.ga.avg_hist,
                div_hist=self.ga.div_hist,
            )

            final_res = self.ga.avg_hist[-1]
            self.results_tab.show_interpretation(final_res)
            final_pop = self.ga.population_hist[-1] if self.ga.population_hist else 0.0
            self.results_tab.show_population_interpretation(final_pop)
            peak_deg = max(self.ga.degradation_hist) if self.ga.degradation_hist else 0.0
            self.results_tab.show_degradation_interpretation(peak_deg)

            return

        # Si aún hay generaciones por ejecutar, actualizar gráficas y ventanas
        t = np.linspace(0, self.ga.generations, len(self.ga.avg_hist))
        y = np.array(self.ga.avg_hist)

        self.results_tab.curve_avg.setData(t, y)
        ultimo_valor = y[-1]
        if ultimo_valor < self.results_tab.resistance_thresholds[0]:
            curvas_color = "#0000FF"
        elif ultimo_valor < self.results_tab.resistance_thresholds[1]:
            curvas_color = "#FFA500"
        else:
            curvas_color = "#FF0000"
        self.results_tab.curve_avg.setPen(pg.mkPen(curvas_color, width=2))

        self.results_tab.curve_div_tab.setData(t, self.ga.div_hist)
        self.results_tab.update_population_plot(t, self.ga.population_hist)
        self.results_tab.update_expansion_plot(t, self.ga.expansion_index_hist)
        self.results_tab.update_degradation_plot(t, self.ga.degradation_hist)

        # Actualizar también el mapa de expansión bacteriana
        if getattr(self, "map_window", None) is not None:
            self.map_window.update_map()

        # Actualizar la ventana ExpandWindow (si existe)
        if getattr(self, "expand_window", None) is not None:
            self.expand_window.update_expand()

    def _show_threshold_alerts(self):
        """Mostrar alertas al alcanzar umbrales críticos solo una vez."""
        if (
            not self.alert_shown_extinction
            and self.ga.population_total <= self.ga.extinction_threshold
        ):
            self.alert_shown_extinction = True
            QMessageBox.warning(
                self,
                "Alerta de Extinción",
                f"La población bacteriana ha caído por debajo del umbral crítico de {self.ga.extinction_threshold}.",
            )
        if (
            not self.alert_shown_resistance
            and self.ga.avg_hist[-1] >= self.ga.resistance_threshold
        ):
            self.alert_shown_resistance = True
            QMessageBox.warning(
                self,
                "Alerta de Resistencia Crítica",
                f"La resistencia promedio ha superado el umbral crítico de {self.ga.resistance_threshold:.2f}.",
            )

    def closeEvent(self, event):
        """
        Maneja el evento de cierre de la ventana principal para asegurar
        que toda la aplicación se termine correctamente.
        """
        # Cierra las ventanas secundarias explícitamente si existen
        if hasattr(self, 'map_window') and self.map_window:
            self.map_window.close()
        if hasattr(self, 'expand_window') and self.expand_window:
            self.expand_window.close()
            
        event.accept()  # Acepta el evento de cierre para la ventana principal

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
