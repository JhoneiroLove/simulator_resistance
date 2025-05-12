import random, copy, math
from typing import Callable, List, Tuple
import numpy as np
from deap import base, creator, tools

# ——— DEAP setup ———
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

class GeneticAlgorithm:
    def __init__(
        self,
        genes,
        antibiotic_schedule: List[Tuple[float, object, float]] = None,
        mutation_rate: float = 0.05,
        generations: int = 50,
        pop_size: int = 100,
        reproduction_func: Callable = None,
        death_rate: float = 0.05,
    ):
        """
        :param genes: lista de objetos con .id y .peso_resistencia
        :param antibiotic_schedule: lista de tuplas (t_event, antibiotic_obj, concentration)
        :param mutation_rate: probabilidad de mutar cada bit
        :param generations: número de pasos de simulación
        :param pop_size: tamaño de la población
        :param reproduction_func: función (N0, r, t)→N(t) normalizada [0,1]
        :param death_rate: tasa de muerte natural por paso
        """
        self.genes = genes
        self.schedule = sorted(antibiotic_schedule or [], key=lambda e: e[0])
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.pop_size = pop_size
        self.reproduction_func = reproduction_func
        self.death_rate = death_rate

        # normalización de la resistencia genética → [0,1]
        self.total_weight = sum(g.peso_resistencia for g in genes) or 1e-8

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

        # para uso interno durante evaluate
        self.current_time = 0.0
        self.current_ab = None
        self.current_conc = 0.0

    def init_individual(self):
        """Cada individuo es una lista de bits (0/1)."""
        return creator.Individual([random.randint(0, 1) for _ in self.genes])

    def _update_antibiotic(self, t: float):
        """Selecciona el antibiótico y concentración activos en el tiempo t."""
        self.current_ab = None
        self.current_conc = 0.0
        for t_evt, ab, conc in self.schedule:
            if t >= t_evt:
                self.current_ab = ab
                self.current_conc = conc
            else:
                break

    def evaluate(self, individual):
        """
        Calcula fitness normalizado [0,1]:
            1) resistencia genética normalizada,
            2) crecimiento (reproduction_func),
            3) kill by antibiotic,
            4) muerte natural,
            devuelve (fitness,)
        """
        # 1) raw → N0 en [0,1]
        raw = sum(g.peso_resistencia * bit for g, bit in zip(self.genes, individual))
        N = raw / self.total_weight

        # 2) crecimiento
        if self.reproduction_func:
            N = self.reproduction_func(N, self.mutation_rate, self.current_time)
            N = min(1.0, max(0.0, N))

        # 3) kill by antibiotic (si hay uno activo)
        if self.current_ab:
            lo = self.current_ab.concentracion_minima
            hi = self.current_ab.concentracion_maxima
            if hi > lo:
                # supervivencia lineal de 1.0→0.0
                surv = max(0.0, min(1.0, 1 - (self.current_conc - lo) / (hi - lo)))
                N *= surv

        # 4) muerte natural
        N *= 1 - self.death_rate

        return (max(0.0, N),)

    def run(
        self,
        selected_gene_ids: List[int],
        time_horizon: float = 24.0,
        progress_callback=None,
    ) -> Tuple[List[float], List[float], List[float], List[float]]:
        """
        Ejecuta la simulación desde t=0 hasta t=time_horizon:
            - selected_gene_ids: always-on genes
            - devuelve 4 historias: best, avg, kill, mut
        """
        # inicializa población
        pop = self.toolbox.population(n=self.pop_size)
        forced = {i for i, g in enumerate(self.genes) if g.id in selected_gene_ids}
        for ind in pop:
            for idx in forced:
                ind[idx] = 1

        best_hist, avg_hist, kill_hist, mut_hist = [], [], [], []
        times = np.linspace(0, time_horizon, self.generations)

        for t in times:
            self.current_time = t
            self._update_antibiotic(t)

            # selección
            offspring = self.toolbox.select(pop, len(pop))
            offspring = list(map(self.toolbox.clone, offspring))

            # cruce
            for c1, c2 in zip(offspring[::2], offspring[1::2]):
                self.toolbox.mate(c1, c2)
                del c1.fitness.values, c2.fitness.values

            # mutación
            for m in offspring:
                self.toolbox.mutate(m)
                del m.fitness.values

            # evaluación
            invalid = [ind for ind in offspring if not ind.fitness.valid]
            fits = map(self.toolbox.evaluate, invalid)
            for ind, fit in zip(invalid, fits):
                ind.fitness.values = fit

            # reemplazo
            pop[:] = offspring

            # métricas
            vals = [ind.fitness.values[0] for ind in pop]
            best, avg = max(vals), sum(vals) / len(vals)

            # kill rate = (1 - surv) si hay antibiótico, else 0
            if self.current_ab:
                lo, hi = (
                    self.current_ab.concentracion_minima,
                    self.current_ab.concentracion_maxima,
                )
                kill = (
                    0.0
                    if hi <= lo
                    else max(0.0, min(1.0, (self.current_conc - lo) / (hi - lo)))
                )
            else:
                kill = 0.0

            best_hist.append(best)
            avg_hist.append(avg)
            kill_hist.append(kill)
            mut_hist.append(self.mutation_rate)

            if progress_callback:
                progress_callback(t, best, avg)

        return best_hist, avg_hist, kill_hist, mut_hist