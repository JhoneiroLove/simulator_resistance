import sys
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QStatusBar,
    QMessageBox,
    QApplication,
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtCore import QPointF
import pyqtgraph as pg

from src.gui.widgets.map_window import MapWindow
from src.gui.widgets.input_form import InputForm
from src.gui.widgets.results_view import ResultsView
from src.gui.widgets.csv_validation import CSVValidationWidget
from src.gui.widgets.detailed_results import DetailedResults
from src.core.genetic_algorithm import GeneticAlgorithm
from src.core.schedule_optimizer import ScheduleOptimizer
from src.data.database import get_session
from src.data.models import Gen, Antibiotico, Recomendacion
from src.data.models import Simulacion

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador Evolutivo por Tratamientos")
        self.setGeometry(100, 100, 1280, 720)

        # ---- Widgets principales ----
        self.input_tab = InputForm()
        
        session = get_session()
        abs_q = session.query(
            Antibiotico.id, Antibiotico.nombre, Antibiotico.concentracion_minima
        ).all()
        session.close()
        antibiotics = [{"id": a[0], "nombre": a[1], "conc_min": a[2]} for a in abs_q]
        self.map_window = None
        self.results_tab = ResultsView(antibiotics)
        self.csv_tab = CSVValidationWidget()
        self.detail_tab = DetailedResults()

        # ---- Conectar señales ----
        self.input_tab.params_submitted.connect(self.on_params_saved)
        self.results_tab.simulate_requested.connect(self.handle_simulation)
        self.results_tab.optimize_requested.connect(self.handle_optimization)

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

        mut = self.saved_mut_rate
        death = self.saved_death_rate
        duration = self.saved_time_horizon
        environmental_factors = self.saved_environmental_factors

        session = get_session()
        genes_orm = session.query(Gen).all()
        genes = [
            {"id": g.id, "nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_orm
        ]

        sched_objs = []
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

        if sched_objs:
            antibiotico_id = sched_objs[0][1]["id"]
            concentracion = sched_objs[0][2]
        else:
            antibiotico_id = None
            concentracion = None

        simulacion = Simulacion(
            antibiotico_id=antibiotico_id,
            concentracion=concentracion if concentracion is not None else 0.0,
            resistencia_predicha=0.0
        )
        session.add(simulacion)
        session.commit()
        simulation_id = simulacion.id
        session.close()

        self._manual_schedule = sched_objs
        self._optimized_schedule = None

        self.ga = GeneticAlgorithm(
            genes=genes,
            antibiotic_schedule=sched_objs,
            mutation_rate=mut,
            generations=duration,
            pop_size=200,
            death_rate=death,
            environmental_factors=environmental_factors,
            simulation_id=simulation_id
        )
        self.ga.initialize(self.saved_genes)

        # Crear y mostrar la ventana de mapa de expansión bacteriana si no existe:
        if getattr(self, "map_window", None) is None:
            self.map_window = MapWindow(self.ga)
        else:
            self.map_window.ga = self.ga
            self.map_window.reset()

        self.map_window.show()

        self.results_tab.clear_plot()
        self.sim_timer.start(100)
        self.tabs.setCurrentWidget(self.results_tab)

        self.alert_shown_extinction = False
        self.alert_shown_resistance = False


    def handle_optimization(self):
        """Ejecuta el ScheduleOptimizer y luego simula el mejor plan."""
        session = get_session()
        genes = session.query(Gen).all()
        antibiotics = session.query(Antibiotico).all()
        session.close()

        optimizer = ScheduleOptimizer(
            genes=genes,
            antibiotics=antibiotics,
            n_events=3,
            generations=self.saved_time_horizon,  # iteraciones del optimizador
            pop_size=6,
            sim_generations=self.saved_time_horizon,  # duración real de cada GA
        )
        best_schedule, score = optimizer.run()

        # Informe rápido
        lines = [f"Resistencia final promedio: {score:.4f}", ""]
        for i, (t, ab, conc) in enumerate(best_schedule, 1):
            lines.append(f"{i}. Tiempo {t:.1f} – {ab['nombre']} ({conc:.2f})")
        QMessageBox.information(self, "Optimización completada", "\n".join(lines))

        # Guardar plan óptimo y simularlo
        self._optimized_schedule = best_schedule
        self.handle_simulation([(t, ab["id"], conc) for t, ab, conc in best_schedule])

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

                # 5) Añádelo sin que modifique el auto‐rango
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

        # Si aún hay generaciónes por ejecutar, actualizar gráficas y mapa
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())