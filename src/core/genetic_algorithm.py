from deap import base, creator, tools

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

class GeneticAlgorithm:
    def __init__(self, genes, mutation_rate=0.05, generations=50, pop_size=100):
        self.genes = genes
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.pop_size = pop_size

        # Configurar toolbox DEAP
        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self.init_individual)
        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutFlipBit, indpb=self.mutation_rate)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def init_individual(self):
        """Inicializa un individuo con todos los genes desactivados."""
        return creator.Individual([0] * len(self.genes))

    def evaluate(self, individual):
        """Calcula la resistencia basada en los genes activos."""
        resistencia = sum(
            gene.peso_resistencia * active
            for gene, active in zip(self.genes, individual)
        )
        return (resistencia,)

    def run(self, selected_gene_ids, progress_callback=None):
        """Ejecuta el algoritmo genético con callback para actualización en tiempo real."""
        active_genes = [1 if gene.id in selected_gene_ids else 0 for gene in self.genes]

        # Inicializar población
        population = self.toolbox.population(n=self.pop_size)
        for ind in population:
            ind[:] = active_genes

        fitness_history = []

        # Evolución
        for generation in range(self.generations):
            # Selección
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            # Cruzamiento
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                self.toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

            # Mutación
            for mutant in offspring:
                self.toolbox.mutate(mutant)
                del mutant.fitness.values

            # Evaluación
            invalid_individuals = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_individuals)
            for ind, fit in zip(invalid_individuals, fitnesses):
                ind.fitness.values = fit

            # Reemplazar población
            population[:] = offspring

            # Registrar y notificar progreso
            best_fitness = max(ind.fitness.values[0] for ind in population)
            fitness_history.append(best_fitness)

            if progress_callback:
                progress_callback(generation, best_fitness)

        return max(fitness_history)