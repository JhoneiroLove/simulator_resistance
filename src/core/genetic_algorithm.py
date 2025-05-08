import random
import copy
from deap import base, creator, tools

# ——— DEFINICIÓN DE TIPOS DE DEAP ———
# Evitar recrear si ya existen
try:
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
except RuntimeError:
    pass

class GeneticAlgorithm:
    def __init__(self, genes, mutation_rate=0.05, generations=50, pop_size=100):
        """
        genes: lista de objetos con atributos .id y .peso_resistencia
        mutation_rate: probabilidad de mutación por gen
        generations: número de generaciones a ejecutar
        pop_size: tamaño de la población
        """
        self.genes = genes
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.pop_size = pop_size

        # ——— TOOLBOX DEAP ———
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

    def init_individual(self):
        """Inicializa un individuo con bits aleatorios (0 ó 1) para cada gen."""
        return creator.Individual([random.randint(0, 1) for _ in self.genes])

    def evaluate(self, individual):
        """Calcula la resistencia total de un individuo."""
        resistencia = sum(
            gene.peso_resistencia * active
            for gene, active in zip(self.genes, individual)
        )
        return (max(0.0, resistencia),)

    def run(self, selected_gene_ids=None, progress_callback=None):
        """
        Ejecuta el algoritmo genético.

        Args:
            selected_gene_ids: iterable de IDs de genes que deben forzarse a 1
            progress_callback: función opcional con firma
                               (gen, best, avg, minimum, cnt_max, cnt_avg, cnt_min)

        Returns:
            best_history: lista de fitness máximo por generación
            avg_history: lista de fitness promedio por generación
            min_history: lista de fitness mínimo por generación
            cnt_max_history: lista de conteos de individuos con fitness == best
            cnt_avg_history: lista de conteos de individuos cerca del promedio (3 decimales)
            cnt_min_history: lista de conteos de individuos con fitness == minimum
        """
        # 1) Crear población inicial
        population = self.toolbox.population(n=self.pop_size)

        # 2) Forzar genes seleccionados a 1
        if selected_gene_ids:
            sel_idxs = {
                idx for idx, g in enumerate(self.genes) if g.id in selected_gene_ids
            }
            for ind in population:
                for idx in sel_idxs:
                    ind[idx] = 1

        best_history = []
        avg_history = []
        min_history = []
        cnt_max_history = []
        cnt_avg_history = []
        cnt_min_history = []

        # 3) Bucle evolutivo
        for gen in range(self.generations):
            # Selección y clonación
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            # Cruce
            for c1, c2 in zip(offspring[::2], offspring[1::2]):
                self.toolbox.mate(c1, c2)
                del c1.fitness.values, c2.fitness.values

            # Mutación
            for mutant in offspring:
                self.toolbox.mutate(mutant)
                del mutant.fitness.values

            # Evaluación de inválidos
            invalids = [ind for ind in offspring if not ind.fitness.valid]
            for ind in invalids:
                ind.fitness.values = self.evaluate(ind)

            # Reemplazo de población
            population[:] = offspring

            # Calcular métricas de fitness
            fitness_vals = [ind.fitness.values[0] for ind in population]
            best = max(fitness_vals)
            avg = sum(fitness_vals) / len(fitness_vals)
            minimum = min(fitness_vals)

            # Conteos de individuos
            cnt_max = fitness_vals.count(best)
            avg_rounded = round(avg, 3)
            cnt_avg = sum(1 for v in fitness_vals if round(v, 3) == avg_rounded)
            cnt_min = fitness_vals.count(minimum)

            # Guardar historia
            best_history.append(best)
            avg_history.append(avg)
            min_history.append(minimum)
            cnt_max_history.append(cnt_max)
            cnt_avg_history.append(cnt_avg)
            cnt_min_history.append(cnt_min)

            # Callback para GUI
            if progress_callback:
                progress_callback(gen, best, avg, minimum, cnt_max, cnt_avg, cnt_min)

        return (
            best_history,
            avg_history,
            min_history,
            cnt_max_history,
            cnt_avg_history,
            cnt_min_history,
        )