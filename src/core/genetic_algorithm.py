import random
import copy
import numpy as np
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
        gen_to_hour: float = 1.0,
        environmental_factors: dict = None,
        mutation_boost_factor: float = 1.5,
    ):
        """
        :param genes: lista de objetos con .id y .peso_resistencia
        :param antibiotic_schedule: lista de tuplas (t_evt, ab, conc[, latency, duration])
        :param mutation_rate: probabilidad base de mutar cada bit
        :param mutation_boost_factor: factor multiplicativo de mut_rate durante exposición
        :param generations: número de pasos (generaciones)
        :param pop_size: tamaño de la población
        :param death_rate: tasa de muerte natural
        :param gen_to_hour: factor de conversión generaciones → horas
        :param environmental_factors: dict de multiplicadores ambientales
        """
        self.genes = genes
        self.mutation_rate = mutation_rate
        self.mutation_boost_factor = mutation_boost_factor
        self.generations = generations
        self.pop_size = pop_size
        self.death_rate = death_rate
        self.gen_to_hour = gen_to_hour
        self.environmental_factors = environmental_factors or {}

        # Normalización de resistencia genética
        self.total_weight = sum(g.peso_resistencia for g in genes) or 1e-8

        # Procesar schedule: t_evt, ab, conc, latency, duration
        raw = antibiotic_schedule or []
        self.schedule = []
        for entry in raw:
            if len(entry) == 3:
                t_evt, ab, conc = entry
                latency, duration = 0.0, generations
            elif len(entry) == 5:
                t_evt, ab, conc, latency, duration = entry
            else:
                raise ValueError("Schedule debe tener 3 o 5 elementos")
            self.schedule.append(
                {
                    "t_evt": t_evt,
                    "ab": ab,
                    "conc": conc,
                    "latency": latency,
                    "duration": duration,
                }
            )
        self.schedule.sort(key=lambda e: e["t_evt"])

        # DEAP toolbox
        self.toolbox = base.Toolbox()
        self.toolbox.register("clone", copy.deepcopy)
        self.toolbox.register("individual", self.init_individual)
        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", tools.cxTwoPoint)
        # No se registra mutate convencional
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        # Estado interno
        self.pop = None
        self.times = None
        self.current_step = 0

        # Historiales
        self.best_hist = []
        self.avg_hist = []
        self.kill_hist = []
        self.mut_hist = []  # ahora almacenará mutaciones efectivas
        self.div_hist = []

    def init_individual(self):
        return creator.Individual([random.randint(0, 1) for _ in self.genes])

    def _update_antibiotic(self, t: float):
        current_hour = t * self.gen_to_hour
        self.current_ab = None
        self.current_conc = 0.0
        for evt in self.schedule:
            start_h = (evt["t_evt"] + evt["latency"]) * self.gen_to_hour
            end_h = start_h + evt["duration"] * self.gen_to_hour
            if start_h <= current_hour < end_h:
                self.current_ab = evt["ab"]
                self.current_conc = evt["conc"]

    def _dynamic_mutation(self, individual):
        # Ajuste de tasa según exposición a antibiótico
        rate = self.mutation_rate * (
            self.mutation_boost_factor if self.current_ab else 1.0
        )
        mutations = 0
        for i in range(len(individual)):
            if random.random() < rate:
                individual[i] = 1 - individual[i]
                mutations += 1
        return mutations

    def evaluate(self, individual):
        raw = sum(g.peso_resistencia * bit for g, bit in zip(self.genes, individual))
        N = raw / self.total_weight
        # Ambiental
        if self.environmental_factors:
            mult = np.prod(list(self.environmental_factors.values()))
            N *= mult
        # Antibiótico
        if self.current_ab:
            lo, hi = (
                self.current_ab.concentracion_minima,
                self.current_ab.concentracion_maxima,
            )
            if hi > lo:
                surv = max(0.0, min(1.0, 1 - (self.current_conc - lo) / (hi - lo)))
                N *= surv
        # Muerte natural
        N *= 1 - self.death_rate
        return (max(0.0, N),)

    def initialize(self, selected_gene_ids):
        # Población inicial y forzar genes
        pop = self.toolbox.population(n=self.pop_size)
        forced = {i for i, g in enumerate(self.genes) if g.id in selected_gene_ids}
        for ind in pop:
            for idx in forced:
                ind[idx] = 1
        self.pop = pop
        self.times = np.linspace(0, self.generations, self.generations)
        self.current_step = 0
        self.best_hist.clear()
        self.avg_hist.clear()
        self.kill_hist.clear()
        self.mut_hist.clear()
        self.div_hist.clear()

    def step(self):
        if self.current_step >= len(self.times):
            return False
        t = self.times[self.current_step]
        self._update_antibiotic(t)
        # Selección
        offspring = list(
            map(self.toolbox.clone, self.toolbox.select(self.pop, len(self.pop)))
        )
        # Cruce
        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            self.toolbox.mate(c1, c2)
            del c1.fitness.values
            del c2.fitness.values
        # Mutación dinámica
        total_mut = 0
        for ind in offspring:
            total_mut += self._dynamic_mutation(ind)
            del ind.fitness.values
        # Evaluación
        invalid = [ind for ind in offspring if not ind.fitness.valid]
        for ind in invalid:
            ind.fitness.values = self.evaluate(ind)
        # Reemplazo
        self.pop[:] = offspring
        # Métricas
        fits = [ind.fitness.values[0] for ind in self.pop]
        best, avg = max(fits), sum(fits) / len(fits)
        kill = 0.0
        if self.current_ab:
            lo, hi = (
                self.current_ab.concentracion_minima,
                self.current_ab.concentracion_maxima,
            )
            if hi > lo:
                kill = max(0.0, min(1.0, (self.current_conc - lo) / (hi - lo)))
        # Diversidad Shannon
        H = 0
        Npop = len(self.pop)
        for j in range(len(self.genes)):
            p = sum(ind[j] for ind in self.pop) / Npop
            if 0 < p < 1:
                H += -p * np.log2(p) - (1 - p) * np.log2(1 - p)
        # Guardar historial
        self.best_hist.append(best)
        self.avg_hist.append(avg)
        self.kill_hist.append(kill)
        self.mut_hist.append(total_mut)
        self.div_hist.append(H)
        self.current_step += 1
        return True