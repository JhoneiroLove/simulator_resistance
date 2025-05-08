import random
import copy
from deap import base, creator, tools

# ——— DEFINICIÓN DE TIPOS DE DEAP ———
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

class GeneticAlgorithm:
    def __init__(self, genes, mutation_rate=0.05, generations=50, pop_size=100):
        """
        genes: lista de objetos con atributos .id y .peso_resistencia
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
        """Calcula la resistencia basada en los genes activos."""
        resistencia = sum(
            gene.peso_resistencia * active
            for gene, active in zip(self.genes, individual)
        )
        return (max(0.0, resistencia),)

    def run(self, selected_gene_ids, progress_callback=None):
        """
        Ejecuta el AG:
        - selected_gene_ids: iterable de IDs que el usuario marcó
        - progress_callback(generation, best, avg): opcional
        Devuelve: (best_history, avg_history)
        """
        # 1) Población inicial aleatoria
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

        # 3) Bucle evolutivo
        for gen in range(self.generations):
            # Selección y clonación
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            # Cruce
            for c1, c2 in zip(offspring[::2], offspring[1::2]):
                self.toolbox.mate(c1, c2)
                del c1.fitness.values
                del c2.fitness.values

            # Mutación
            for mutant in offspring:
                self.toolbox.mutate(mutant)
                del mutant.fitness.values

            # Evaluación de inválidos
            invalids = [ind for ind in offspring if not ind.fitness.valid]
            fits = map(self.toolbox.evaluate, invalids)
            for ind, fit in zip(invalids, fits):
                ind.fitness.values = fit

            # Reemplazo
            population[:] = offspring

            # Cálculo de métricas
            fitness_vals = [ind.fitness.values[0] for ind in population]
            best = max(fitness_vals)
            avg = sum(fitness_vals) / len(fitness_vals)

            best_history.append(best)
            avg_history.append(avg)

            # Callback para GUI
            if progress_callback:
                progress_callback(gen, best, avg)

        return best_history, avg_history