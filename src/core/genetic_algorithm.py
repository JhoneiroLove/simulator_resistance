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
    ):
        """
        :param genes: lista de objetos con .id y .peso_resistencia
        :param antibiotic_schedule: lista de tuplas (t_event, antibiotic_obj, concentration)
        :param mutation_rate: probabilidad de mutar cada bit
        :param generations: número de pasos (generaciones)
        :param pop_size: tamaño de la población
        :param death_rate: tasa de muerte natural
        """
        self.genes = genes
        self.schedule = sorted(antibiotic_schedule or [], key=lambda e: e[0])
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.pop_size = pop_size
        self.death_rate = death_rate

        # Normalización de resistencia genética → [0,1]
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

    def evaluate(self, individual):
        """
        Calcula fitness normalizado [0,1]:
            1) resistencia genética
            2) crecimiento logístico/exponencial opcional
            3) kill por antibiótico
            4) muerte natural
        """
        # 1) raw → N0 en [0,1]
        raw = sum(g.peso_resistencia * bit for g, bit in zip(self.genes, individual))
        N = raw / self.total_weight

        # 2) (si tuvieras reproduction_func se aplicaría aquí)

        # 3) kill por antibiótico
        if self.current_ab:
            lo, hi = (
                self.current_ab.concentracion_minima,
                self.current_ab.concentracion_maxima,
            )
            if hi > lo:
                surv = max(0.0, min(1.0, 1 - (self.current_conc - lo) / (hi - lo)))
                N *= surv

        # 4) muerte natural
        N *= 1 - self.death_rate

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
        forced = {i for i, g in enumerate(self.genes) if g.id in selected_gene_ids}
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

        # mutación (constante)
        mut = self.mutation_rate

        # diversidad (Shannon)
        N = len(self.pop)
        H = 0.0
        for j in range(len(self.genes)):
            p_j = sum(ind[j] for ind in self.pop) / N
            if 0 < p_j < 1:
                H += -p_j * np.log2(p_j) - (1 - p_j) * np.log2(1 - p_j)

        # guardar
        self.best_hist.append(best)
        self.avg_hist.append(avg)
        self.kill_hist.append(kill)
        self.mut_hist.append(mut)
        self.div_hist.append(H)

        self.current_step += 1
        return True