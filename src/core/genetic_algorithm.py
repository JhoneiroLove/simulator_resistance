import random
import copy
import numpy as np
from src.data.database import get_session
from src.data.models import SimulacionAtributos
from deap import base, creator, tools

# ——— DEAP setup ———
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

class GeneticAlgorithm: 
    def __init__(
        self,
        genes,
        antibiotic_schedule=None,
        mutation_rate: float = 0.05,
        generations: int = 50,
        pop_size: int = 100,
        death_rate: float = 0.05,
        environmental_factors=None,
        simulation_id=None,
    ):
        """
        :param genes: lista de objetos con .id y .peso_resistencia
        :param antibiotic_schedule: lista de tuplas (t_event, antibiotic_obj, concentration)
        :param mutation_rate: probabilidad de mutar cada bit
        :param generations: número de pasos (generaciones)
        :param pop_size: tamaño de la población
        :param death_rate: tasa de muerte natural
        :param environmental_factors: dict con factores ambientales como temperatura y pH
        """
        self.genes = genes
        self.schedule = sorted(antibiotic_schedule or [], key=lambda e: e[0])
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.pop_size = pop_size
        self.death_rate = death_rate
        self.environmental_factors = environmental_factors or {
            "temperature": 37.0,
            "pH": 7.4,
        }
        self.current_simulation_id = simulation_id

        # Normalización de resistencia genética → [0,1]
        self.total_weight = sum(g["peso_resistencia"] for g in genes) or 1e-8

        # DEAP toolbox
        self.toolbox = base.Toolbox()
        self.toolbox.register("clone", copy.deepcopy)
        self.toolbox.register("individual", self.init_individual)
        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=self.mutation_rate)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        # estado interno para dinámico
        self.pop = None
        self.times = None
        self.current_step = 0

        # historiales
        self.best_hist = []
        self.avg_hist = []
        self.kill_hist = []
        self.mut_hist = []
        self.div_hist = []

        self.expansion_index_hist = []  # Historial del índice de expansión bacteriana

        # variables para población bacteriana real
        self.population_total = None  # Población bacteriana real (N_t)
        self.population_hist = []  # Historial de población bacteriana

        self.degradation_hist = []  # Historial de degradación por generación

        # Parámetros del modelo logístico
        self.r_growth = 0.2  # Tasa de crecimiento (por defecto)
        self.K_capacity = 1e6  # Capacidad máxima del entorno (por defecto)

        # Parámetros de umbral
        self.extinction_threshold = 100  # Menos de 100 bacterias = extinción
        self.resistance_threshold = 0.8  # 80% resistencia = alarma

    def init_individual(self):
        """Cada individuo es una lista de bits (0/1)."""
        return creator.Individual([random.randint(0, 1) for _ in self.genes])

    def _update_antibiotic(self, t: float):
        """Selecciona antibiótico y concentración activos en el tiempo t."""
        self.current_ab = None
        self.current_conc = 0.0
        for t_evt, ab, conc in self.schedule:
            if t >= t_evt:
                self.current_ab = ab
                self.current_conc = conc
            else:
                break

    def growth_modifier(self):
        temp = self.environmental_factors.get("temperature", 37.0)
        if 35 <= temp <= 39:
            return 1.0
        else:
            return max(0.0, 1 - abs(temp - 37) * 0.1)

    def death_modifier(self):
        pH = self.environmental_factors.get("pH", 7.4)
        if 6.5 <= pH <= 7.5:
            return 1.0
        else:
            return 1.2

    def set_environmental_factor(self, key: str, value: float):
        self.environmental_factors[key] = value

    def get_environmental_factor(self, key: str) -> float:
        return self.environmental_factors.get(key)

    def evaluate(self, individual):
        """
        Calcula fitness normalizado [0,1]:
            1) resistencia genética
            2) kill por antibiótico
            3) muerte natural ajustada por ambiente
        """
        # 1) raw → N0 en [0,1]
        raw = sum(g["peso_resistencia"] * bit for g, bit in zip(self.genes, individual))
        N = raw / self.total_weight

        # 2) kill por antibiótico
        if self.current_ab:
            lo, hi = (
                self.current_ab["concentracion_minima"],
                self.current_ab["concentracion_maxima"],
            )
            if hi > lo:
                surv = max(0.0, min(1.0, 1 - (self.current_conc - lo) / (hi - lo)))
                N *= surv

        # 3) muerte natural ajustada por pH (u otro factor)
        death_rate_adj = self.death_rate * self.death_modifier()
        N *= 1 - death_rate_adj

        return (max(0.0, N),)

    def initialize(self, selected_gene_ids: list):
        """
        Prepara todo para una ejecución dinámica:
        - crea población
        - fuerza los genes seleccionados a 1
        - inicializa times y contadores
        """
        # población inicial
        pop = self.toolbox.population(n=self.pop_size)
        forced = {i for i, g in enumerate(self.genes) if g["id"] in selected_gene_ids}
        for ind in pop:
            for idx in forced:
                ind[idx] = 1
        self.pop = pop

        # discretizar tiempo en 'generations' pasos
        self.times = np.linspace(0, self.generations, self.generations)
        self.current_step = 0

        # limpiar historiales
        self.best_hist.clear()
        self.avg_hist.clear()
        self.kill_hist.clear()
        self.mut_hist.clear()
        self.div_hist.clear()

        # inicializar población bacteriana real
        self.population_total = 1e4  # Población inicial
        self.population_hist.clear()
        self.population_hist.append(self.population_total)

        self.expansion_index_hist.clear()
        self.expansion_index_hist.append(1.0)  # Primer valor es 1.0 por definición

        self.degradation_hist.clear()
        self.degradation_hist.append(0.0)  # El primer valor es 0

    def step(self) -> bool:
        """
        Ejecuta UNA generación. Devuelve False si ya no hay más pasos.
        """
        if self.current_step >= len(self.times):
            return False

        t = self.times[self.current_step]
        self.current_time = t

        # actualizar antibiótico según schedule dinámica
        self._update_antibiotic(t)

        # 1) selección
        offspring = self.toolbox.select(self.pop, len(self.pop))
        offspring = list(map(self.toolbox.clone, offspring))

        # 2) cruce
        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            self.toolbox.mate(c1, c2)
            del c1.fitness.values, c2.fitness.values

        # 3) mutación
        for m in offspring:
            self.toolbox.mutate(m)
            del m.fitness.values

        # 4) evaluación
        invalid = [ind for ind in offspring if not ind.fitness.valid]
        fits = map(self.toolbox.evaluate, invalid)
        for ind, fit in zip(invalid, fits):
            ind.fitness.values = fit

        # reemplazo
        self.pop[:] = offspring

        # 5) métricas
        vals = [ind.fitness.values[0] for ind in self.pop]
        best = max(vals)
        avg = sum(vals) / len(vals)

        # kill rate
        if self.current_ab:
            lo, hi = (
                self.current_ab["concentracion_minima"],
                self.current_ab["concentracion_maxima"],
            )
            kill = (
                0.0
                if hi <= lo
                else max(0.0, min(1.0, (self.current_conc - lo) / (hi - lo)))
            )
        else:
            kill = 0.0

        # mutación (constante)
        mut = self.mutation_rate

        # diversidad (Shannon)
        N = len(self.pop)
        H = 0.0
        for j in range(len(self.genes)):
            p_j = sum(ind[j] for ind in self.pop) / N
            if 0 < p_j < 1:
                H += -p_j * np.log2(p_j) - (1 - p_j) * np.log2(1 - p_j)

        # Rescate evolutivo por diversidad baja
        if H < 0.2:  # Diversidad muy baja
            for ind in self.pop:
                if random.random() < 0.02:  # 2% chance de mutación extra
                    idx = random.randint(0, len(ind) - 1)
                    ind[idx] = 1 - ind[idx]
                    del ind.fitness.values
            # Vuelve a evaluar después de las mutaciones extra
            invalid = [ind for ind in self.pop if not ind.fitness.valid]
            fits = map(self.toolbox.evaluate, invalid)
            for ind, fit in zip(invalid, fits):
                ind.fitness.values = fit

        # guardar
        self.best_hist.append(best)
        self.avg_hist.append(avg)
        self.kill_hist.append(kill)
        self.mut_hist.append(mut)
        self.div_hist.append(H)

        prev_population = self.population_total

        # Ajustes por factores ambientales
        growth_mod = self.growth_modifier()
        death_mod = self.death_modifier()

        r = self.r_growth * growth_mod
        death_rate = self.death_rate * death_mod

        # Actualizar población bacteriana real
        growth = r * prev_population * (1 - prev_population / self.K_capacity)
        deaths = death_rate * prev_population
        N_next = prev_population + growth - deaths
        N_next *= avg  # fitness promedio como presión antibiótica

        N_next = max(N_next, 1.0)  # evitar negativos
        self.population_total = N_next
        self.population_hist.append(self.population_total)

        # Calcular degradación relativa
        if prev_population > 0:
            degradation = 1 - (self.population_total / prev_population)
        else:
            degradation = 0.0
        self.degradation_hist.append(degradation)

        # Detectar extinción
        if self.population_total <= self.extinction_threshold:
            self.extinction_reached = True

        # Detectar resistencia crítica
        if self.avg_hist[-1] >= self.resistance_threshold:
            self.resistance_critical = True

        # Cálculo índice de expansión
        idx_exp = N_next / prev_population if prev_population > 0 else 0.0
        self.expansion_index_hist.append(idx_exp)

        # --- GUARDAR ATRIBUTOS SOLO AL FINAL ---

        # Si tus individuos tienen más atributos (por ejemplo, recubrimiento, reproducción...):
        # for atributo in ['recubrimiento', 'reproduccion', 'letalidad', 'permeabilidad', 'enzimas']:
        #     valores = [getattr(ind, atributo) for ind in self.pop]
        #     promedio = float(np.mean(valores)) if valores else 0.0
        #     std = float(np.std(valores)) if valores else 0.0
        #     sim_attr = SimulacionAtributos(
        #         simulacion_id=self.current_simulation_id,
        #         generacion=self.current_step,
        #         antibiotico_id=antibiotico_id,
        #         atributo=atributo,
        #         valor_promedio=promedio,
        #         desviacion_std=std
        #     )
        #     session.add(sim_attr)

        self.current_step += 1
        return True

    def save_final_gene_attributes(self, selected_gene_ids):
        """Guarda solo los genes activos (seleccionados por el usuario) al final de la simulación."""
        session = get_session()
        antibiotico_id = self.current_ab["id"] if self.current_ab else None
        generacion_final = self.current_step - 1  # Última generación
        
        for idx, gen in enumerate(self.genes):
            if gen["id"] in selected_gene_ids:
                valores = [ind[idx] for ind in self.pop]
                promedio = float(np.mean(valores)) if valores else 0.0
                std = float(np.std(valores)) if valores else 0.0
                sim_attr = SimulacionAtributos(
                    simulacion_id=self.current_simulation_id,
                    generacion=generacion_final,
                    antibiotico_id=antibiotico_id,
                    atributo=f"gen_{gen['nombre']}",
                    valor_promedio=promedio,
                    desviacion_std=std,
                )
                session.add(sim_attr)
        session.commit()
        session.close()