import random
import copy
import numpy as np
from deap import base, creator, tools
from src.core.genetic_algorithm import GeneticAlgorithm

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("ScheduleIndividual", list, fitness=creator.FitnessMin)

class ScheduleOptimizer:
    def __init__(
        self,
        genes,
        antibiotics,
        n_events=3,
        generations=20,
        pop_size=10,
        mutation_rate=0.2,
        death_rate=0.05,
        sim_generations=50,
    ):
        """
        :param genes: Lista de objetos Gen ORM
        :param antibiotics: Lista de objetos Antibiotico ORM
        :param n_events: Cuántos eventos tendrá cada schedule
        :param generations: generaciones del optimizador
        :param pop_size: población de schedules a probar
        :param mutation_rate: probabilidad de mutación por evento
        :param death_rate: tasa usada en simulación interna
        :param sim_generations: duración de cada ejecución GA
        """
        self.genes = genes
        self.antibiotics = antibiotics
        self.n_events = n_events
        self.generations = generations
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.sim_generations = sim_generations
        self.death_rate = death_rate

        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self._create_individual)
        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )
        self.toolbox.register("evaluate", self._evaluate)
        self.toolbox.register("mate", self._crossover)
        self.toolbox.register("mutate", self._mutate)
        self.toolbox.register("select", tools.selTournament, tournsize=2)

    def _create_individual(self):
        ind = []
        for _ in range(self.n_events):
            ab = random.choice(self.antibiotics)
            t = random.uniform(0, self.sim_generations)
            conc = random.uniform(ab.concentracion_minima, ab.concentracion_maxima)
            ind.append((t, ab, conc))
        return creator.ScheduleIndividual(sorted(ind, key=lambda e: e[0]))

    def _evaluate(self, individual):
        ga = GeneticAlgorithm(
            genes=self.genes,
            antibiotic_schedule=individual,
            mutation_rate=self.mutation_rate,
            generations=self.sim_generations,
            pop_size=200,
            death_rate=self.death_rate,
        )
        ga.initialize([g.id for g in self.genes])  # asumir uso total
        while ga.step():
            pass
        return (ga.avg_hist[-1],)

    def _crossover(self, ind1, ind2):
        """Cruza eventos entre schedules."""
        cx_point = random.randint(1, self.n_events - 1)
        ind1[:cx_point], ind2[:cx_point] = ind2[:cx_point], ind1[:cx_point]
        return ind1, ind2

    def _mutate(self, individual):
        """Mutación por evento."""
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                t, ab, _ = individual[i]
                new_ab = random.choice(self.antibiotics)
                new_conc = random.uniform(
                    new_ab.concentracion_minima, new_ab.concentracion_maxima
                )
                individual[i] = (t, new_ab, new_conc)
        individual.sort(key=lambda e: e[0])
        return (individual,)

    def run(self):
        pop = self.toolbox.population(n=self.pop_size)
        fitnesses = map(self.toolbox.evaluate, pop)
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        for _ in range(self.generations):
            offspring = self.toolbox.select(pop, len(pop))
            offspring = list(map(copy.deepcopy, offspring))

            for c1, c2 in zip(offspring[::2], offspring[1::2]):
                self.toolbox.mate(c1, c2)
                del c1.fitness.values, c2.fitness.values

            for m in offspring:
                self.toolbox.mutate(m)
                del m.fitness.values

            invalid = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid)
            for ind, fit in zip(invalid, fitnesses):
                ind.fitness.values = fit

            pop[:] = offspring

        best = tools.selBest(pop, 1)[0]
        return best, best.fitness.values[0]