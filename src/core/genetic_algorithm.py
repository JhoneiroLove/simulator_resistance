import logging
import random
import copy
import time
import numpy as np
from src.data.database import get_session
from src.data.models import SimulacionAtributos
from deap import base, creator, tools

class BacteriaIndividual(list):
    """Individuo: genes (bits) + atributos biológicos."""

    def __init__(
        self, genes_bits, recubrimiento, reproduccion, letalidad, permeabilidad, enzimas
    ):
        super().__init__(genes_bits)
        self.recubrimiento = recubrimiento
        self.reproduccion = reproduccion
        self.letalidad = letalidad
        self.permeabilidad = permeabilidad
        self.enzimas = enzimas


# ——— DEAP setup ———
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", BacteriaIndividual, fitness=creator.FitnessMax)


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
        reproduction_rate: float = 1.0,
        phenotype_mutation_prob: float = 0.02,
        phenotype_mutation_sigma: float = 0.05,
        evo_rescue_threshold: float = 0.2,
        evo_rescue_prob: float = 0.02,
        r_growth: float = 0.2,
        K_capacity: float = 1e6,
        pressure_factor: float = 0.5,
        huesped=None,
        sitio_infeccion=None,
    ):
        logging.info(
            f"Initializing Genetic Algorithm with simulation_id={simulation_id}"
        )
        logging.debug(
            f"GA params: mutation_rate={mutation_rate}, generations={generations}, pop_size={pop_size}, death_rate={death_rate}"
        )
        logging.debug(f"Environmental factors: {environmental_factors}")
        logging.debug(f"Antibiotic schedule: {antibiotic_schedule}")
        if huesped:
            logging.debug(
                f"Guest parameters: age={huesped.age}, weight={huesped.weight}, sex={huesped.sex}"
            )
        if sitio_infeccion:
            logging.debug(
                f"Infection site parameters: nombre={sitio_infeccion.nombre}, pH={sitio_infeccion.ph}, "
                f"perfusion={sitio_infeccion.perfusion_sanguinea}, capacidad_carga={sitio_infeccion.capacidad_carga}"
            )
        """
        :param genes: lista de objetos con .id y .peso_resistencia
        :param antibiotic_schedule: lista de tuplas (t_event, antibiotic_obj, concentration)
        :param mutation_rate: probabilidad de mutar cada bit
        :param generations: número de pasos (generaciones)
        :param pop_size: tamaño de la población
        :param death_rate: tasa de muerte natural
        :param environmental_factors: dict con factores ambientales como temperatura y pH
        :param huesped: objeto Guest opcional con parámetros del paciente
        :param sitio_infeccion: objeto InfectionSite opcional con características del sitio
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
        self.reproduction_rate = reproduction_rate
        self.resistance_threshold = self.environmental_factors.get(
            "resistance_threshold", 0.9
        )
        self.current_simulation_id = simulation_id

        self.phenotype_mutation_prob = phenotype_mutation_prob
        self.phenotype_mutation_sigma = phenotype_mutation_sigma
        self.evo_rescue_threshold = evo_rescue_threshold
        self.evo_rescue_prob = evo_rescue_prob
        self.r_growth = r_growth
        self.K_capacity = K_capacity
        self.pressure_factor = pressure_factor

        self.total_weight = sum(g["peso_resistencia"] for g in genes) or 1e-8

        self.extinction_reached = False
        self.resistance_critical = False

        # Almacenar huésped y aplicar modificadores si está presente
        self.huesped = huesped
        if self.huesped:
            from src.core.guest_service import GuestService

            # Aplicar modificadores del huésped
            death_modifier = GuestService.get_death_rate_modifier(self.huesped)
            self.death_rate *= death_modifier

            repro_modifier = GuestService.get_reproduction_rate_modifier(
                self.huesped.estado_inmune
            )
            self.reproduction_rate *= repro_modifier

            logging.info(
                f"Guest modifiers applied: death_rate={self.death_rate:.4f}, reproduction_rate={self.reproduction_rate:.4f}"
            )

        # Almacenar sitio de infección y aplicar modificadores si está presente
        self.sitio_infeccion = sitio_infeccion
        if self.sitio_infeccion:
            # Actualizar pH ambiental con el pH del sitio
            self.environmental_factors["pH"] = self.sitio_infeccion.ph

            # Actualizar capacidad de carga con la del sitio
            self.K_capacity = self.sitio_infeccion.capacidad_carga

            # El modificador de perfusión afectará la tasa de muerte
            perfusion_modifier = 0.5 + (self.sitio_infeccion.perfusion_sanguinea * 0.5)
            self.death_rate *= perfusion_modifier

            logging.info(
                f"Infection site modifiers applied: pH={self.sitio_infeccion.ph}, "
                f"K_capacity={self.K_capacity:.2f}, perfusion_modifier={perfusion_modifier:.4f}, "
                f"adjusted_death_rate={self.death_rate:.4f}"
            )

        self.toolbox = base.Toolbox()
        self.toolbox.register("clone", copy.deepcopy)
        self.toolbox.register("individual", self.init_individual)
        self.toolbox.register(
            "population", tools.initRepeat, list, self.toolbox.individual
        )
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", self._mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

        self.pop = None
        self.times = None
        self.current_step = 0

        self.best_hist = []
        self.avg_hist = []
        self.kill_hist = []
        self.mut_hist = []
        self.div_hist = []

        self.expansion_index_hist = []

        self.population_total = None
        self.population_hist = []

        self.degradation_hist = []

        self.extinction_threshold = 100
        self.resistance_threshold = 0.8

        self.recubrimiento_vals = []
        self.reproduccion_vals = []
        self.letalidad_vals = []
        self.permeabilidad_vals = []
        self.enzimas_vals = []

        # Parámetros para optimización adaptativa
        self.target_time_per_generation = 0.5
        self.min_pop_size = 50
        self.max_pop_size = pop_size
        self.base_mutation_rate = mutation_rate
        self.diversity_threshold = 0.3

        self.fitness_hist = []

    def init_individual(self):
        genes_bits = [random.randint(0, 1) for _ in self.genes]
        recubrimiento = random.uniform(0.5, 1.0)
        reproduccion = random.uniform(0.5, 1.0)
        letalidad = random.uniform(0.5, 1.0)
        permeabilidad = random.uniform(0.5, 1.0)
        enzimas = random.uniform(0.5, 1.0)
        return creator.Individual(
            genes_bits, recubrimiento, reproduccion, letalidad, permeabilidad, enzimas
        )

    def _mutate_individual(self, individual):
        tools.mutFlipBit(individual, indpb=self.mutation_rate)

        bio_attrs = [
            individual.recubrimiento,
            individual.reproduccion,
            individual.letalidad,
            individual.permeabilidad,
            individual.enzimas,
        ]

        tools.mutGaussian(
            bio_attrs,
            mu=0.0,
            sigma=self.phenotype_mutation_sigma,
            indpb=self.phenotype_mutation_prob,
        )

        individual.recubrimiento = min(1.0, max(0.0, bio_attrs[0]))
        individual.reproduccion = min(1.0, max(0.0, bio_attrs[1]))
        individual.letalidad = min(1.0, max(0.0, bio_attrs[2]))
        individual.permeabilidad = min(1.0, max(0.0, bio_attrs[3]))
        individual.enzimas = min(1.0, max(0.0, bio_attrs[4]))

        return (individual,)

    def _update_antibiotic(self, t: float):
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

        if self.sitio_infeccion and self.current_ab:
            from src.core.infection_site_service import InfectionSiteService

            ph_modifier = InfectionSiteService.get_ph_modifier(
                self.sitio_infeccion.ph, self.current_ab.get("tipo", "")
            )
            return 2.0 - ph_modifier

        if 6.5 <= pH <= 7.5:
            return 1.0
        else:
            return 1.2

    def set_environmental_factor(self, key: str, value: float):
        self.environmental_factors[key] = value

    def get_environmental_factor(self, key: str) -> float:
        return self.environmental_factors.get(key)
    
    def calcular_dosis_ajustada(self, dosis_estandar: float, antibiotico_tipo: str) -> float:
        """
        Calcula la dosis ajustada según la función renal del huésped.
        
        Args:
            dosis_estandar: Dosis estándar del antibiótico (mg)
            antibiotico_tipo: Tipo de antibiótico
            
        Returns:
            float: Dosis ajustada según clearance de creatinina
        """
        if not self.huesped or not self.huesped.clearance_creatinina:
            return dosis_estandar
        
        from src.core.guest_service import GuestService
        
        clearance = self.huesped.clearance_creatinina
        kidney_status = GuestService.get_kidney_function_status(clearance)
        
        # Factores de ajuste según función renal y tipo de antibiótico
        # Antibióticos con excreción renal requieren mayor ajuste
        ajuste_renal = {
            "normal": 1.0,
            "leve_disminucion": 1.0,
            "moderada_disminucion": 0.75,
            "severa_disminucion": 0.5,
            "fallo_renal": 0.25
        }
        
        # Algunos antibióticos requieren ajuste más agresivo
        antibioticos_alta_excrecion_renal = [
            "aminoglucósido", 
            "carbapenémico", 
            "cefalosporina",
            "polimixina"
        ]
        
        factor_base = ajuste_renal.get(kidney_status, 1.0)
        
        # Ajuste adicional para antibióticos de alta excreción renal
        if antibiotico_tipo.lower() in antibioticos_alta_excrecion_renal:
            if kidney_status in ["severa_disminucion", "fallo_renal"]:
                factor_base *= 0.8  # Reducción adicional del 20%
        
        dosis_ajustada = dosis_estandar * factor_base
        
        logging.info(
            f"Dosis ajustada: {dosis_estandar:.2f} mg → {dosis_ajustada:.2f} mg "
            f"(kidney_status={kidney_status}, clearance={clearance:.2f} mL/min)"
        )
        
        return dosis_ajustada

    def _sigmoid_survival(self, concentration, lo, hi):
        """Calcula la supervivencia con una función sigmoidal."""
        if hi - lo <= 0:
            return 1.0 if concentration < lo else 0.0

        c50 = (lo + hi) / 2.0
        k = 10 / (hi - lo)

        survival = 1.0 / (1.0 + np.exp(k * (concentration - c50)))
        return survival

    def evaluate(self, individual):
        raw_resistance = sum(
            g["peso_resistencia"] * bit for g, bit in zip(self.genes, individual)
        )

        adaptive_cost = (individual.recubrimiento + individual.enzimas) / 2.0

        N = (raw_resistance / self.total_weight) * (1 - adaptive_cost)

        if self.current_ab:
            lo, hi = (
                self.current_ab["concentracion_minima"],
                self.current_ab["concentracion_maxima"],
            )

            # Concentración efectiva considerando penetración del sitio
            effective_conc = self.current_conc
            if self.sitio_infeccion:
                from src.core.infection_site_service import InfectionSiteService

                penetration_factor = (
                    InfectionSiteService.calcular_penetracion_antibiotico(
                        self.sitio_infeccion, self.current_ab
                    )
                )
                effective_conc = self.current_conc * penetration_factor

            surv = self._sigmoid_survival(effective_conc, lo, hi)
            
            # Aplicar factor inmune del huésped
            if self.huesped:
                from src.core.guest_service import GuestService
                factor_inmune = GuestService.obtener_factor_inmune(self.huesped.estado_inmune)
                # Factor inmune bajo = sistema inmune débil = mayor supervivencia bacteriana
                # Invertir el factor: si factor_inmune=0.1 (débil), bacterias sobreviven más
                surv *= (2.0 - factor_inmune)
            
            N *= surv

        death_rate_adj = self.death_rate * self.death_modifier()
        N *= 1 - death_rate_adj

        return (max(0.0, N),)

    def initialize(self, selected_gene_ids: list):
        logging.info(f"Initializing population for genes: {selected_gene_ids}")
        pop = self.toolbox.population(n=self.pop_size)
        forced = {i for i, g in enumerate(self.genes) if g["id"] in selected_gene_ids}
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

        self.population_total = 1e4
        self.population_hist.clear()
        self.population_hist.append(self.population_total)

        self.expansion_index_hist.clear()
        self.expansion_index_hist.append(1.0)

        self.degradation_hist.clear()
        self.degradation_hist.append(0.0)

    def step(self) -> bool:
        if self.current_step >= len(self.times):
            return False

        t = self.times[self.current_step]
        self.current_time = t

        self._update_antibiotic(t)

        start_time = time.perf_counter()

        offspring = self.toolbox.select(self.pop, len(self.pop))
        offspring = list(map(self.toolbox.clone, offspring))

        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            self.toolbox.mate(c1, c2)
            del c1.fitness.values, c2.fitness.values

        for m in offspring:
            self.toolbox.mutate(m)
            del m.fitness.values

        invalid = [ind for ind in offspring if not ind.fitness.valid]
        fits = map(self.toolbox.evaluate, invalid)
        for ind, fit in zip(invalid, fits):
            ind.fitness.values = fit

        self.pop[:] = offspring

        vals = [ind.fitness.values[0] for ind in self.pop]
        best = max(vals)
        avg = sum(vals) / len(vals)

        self.fitness_hist.append(avg)

        convergence_rate = 0.0
        if len(self.fitness_hist) > 10:
            window = self.fitness_hist[-10:]
            slope = np.polyfit(range(10), window, 1)[0]
            convergence_rate = abs(slope)
            logging.info(f"Tasa de convergencia: {convergence_rate:.6f}")

            if convergence_rate < 0.001:
                new_mutation_rate = min(0.5, self.mutation_rate * 1.2)
                logging.warning(
                    f"¡Convergencia lenta! Aumentando mutación a {new_mutation_rate}"
                )
                self.mutation_rate = new_mutation_rate

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

        mut = self.mutation_rate

        N = len(self.pop)
        H = 0.0
        for j in range(len(self.genes)):
            p_j = sum(ind[j] for ind in self.pop) / N
            if 0 < p_j < 1:
                H += -p_j * np.log2(p_j) - (1 - p_j) * np.log2(1 - p_j)

        if H < self.evo_rescue_threshold:
            for ind in self.pop:
                if random.random() < self.evo_rescue_prob:
                    idx = random.randint(0, len(ind) - 1)
                    ind[idx] = 1 - ind[idx]
                    del ind.fitness.values
            invalid = [ind for ind in self.pop if not ind.fitness.valid]
            fits = map(self.toolbox.evaluate, invalid)
            for ind, fit in zip(invalid, fits):
                ind.fitness.values = fit

        self.best_hist.append(best)
        self.avg_hist.append(avg)
        self.kill_hist.append(kill)
        self.mut_hist.append(mut)
        self.div_hist.append(H)

        prev_population = self.population_total

        growth_mod = self.growth_modifier()
        death_mod = self.death_modifier()

        r = self.r_growth * self.reproduction_rate * growth_mod
        death_rate = self.death_rate * death_mod

        growth = r * prev_population * (1 - prev_population / self.K_capacity)
        deaths = death_rate * prev_population
        N_next = prev_population + growth - deaths

        log_details = f"Pop dynamics: N_prev={prev_population:.2f}, growth={growth:.2f}, deaths={deaths:.2f}, N_after_growth/death={N_next:.2f}"

        if self.current_ab:
            pressure = (1 - avg) * self.pressure_factor
            N_next *= 1 - pressure
            log_details += f", avg_fitness={avg:.4f}, pressure_applied={pressure:.4f}, N_after_pressure={N_next:.2f}"

        N_next = max(N_next, 1.0)
        self.population_total = N_next
        self.population_hist.append(self.population_total)
        logging.debug(log_details)

        if self.current_ab and self.current_conc > 0.0 and prev_population > 0:
            degradation = 1 - (self.population_total / prev_population)
        else:
            degradation = 0.0
        self.degradation_hist.append(degradation)

        if self.population_total <= self.extinction_threshold:
            if not self.extinction_reached:
                logging.warning(
                    f"Extinction threshold reached at step {self.current_step}."
                )
            self.extinction_reached = True

        if self.avg_hist[-1] >= self.resistance_threshold:
            if not self.resistance_critical:
                logging.warning(
                    f"Critical resistance threshold reached at step {self.current_step}."
                )
            self.resistance_critical = True

        idx_exp = N_next / prev_population if prev_population > 0 else 0.0
        self.expansion_index_hist.append(idx_exp)

        generation_time = time.perf_counter() - start_time

        if generation_time > self.target_time_per_generation:
            reduction_factor = max(
                0.7, self.target_time_per_generation / generation_time
            )
            new_pop_size = max(self.min_pop_size, int(len(self.pop) * reduction_factor))
            if new_pop_size < len(self.pop):
                logging.info(
                    f"Adaptación: reduciendo población de {len(self.pop)} a {new_pop_size} por eficiencia"
                )
                self.pop = tools.selBest(self.pop, new_pop_size)

        if H < self.diversity_threshold:
            increase_factor = min(2.0, 1.0 + (self.diversity_threshold - H))
            new_mutation_rate = min(0.2, self.mutation_rate * increase_factor)
            if new_mutation_rate > self.mutation_rate:
                logging.info(
                    f"Adaptación: aumentando mutación de {self.mutation_rate} a {new_mutation_rate} por baja diversidad"
                )
                self.mutation_rate = new_mutation_rate
        elif self.mutation_rate > self.base_mutation_rate:
            self.mutation_rate = max(self.base_mutation_rate, self.mutation_rate * 0.9)

        logging.debug(
            f"Step {self.current_step}: best_fit={best:.4f}, avg_fit={avg:.4f}, pop_size={self.population_total:.2f}, kill_rate={kill:.4f}, diversity={H:.4f}"
        )

        self.current_step += 1
        return True

    def get_average_attributes(self):
        """Calcula el promedio de los atributos biológicos de la población actual."""
        if not self.pop:
            return {
                "recubrimiento": 0,
                "reproduccion": 0,
                "letalidad": 0,
                "permeabilidad": 0,
                "enzimas": 0,
            }

        avg_attributes = {
            "recubrimiento": float(np.mean([ind.recubrimiento for ind in self.pop])),
            "reproduccion": float(np.mean([ind.reproduccion for ind in self.pop])),
            "letalidad": float(np.mean([ind.letalidad for ind in self.pop])),
            "permeabilidad": float(np.mean([ind.permeabilidad for ind in self.pop])),
            "enzimas": float(np.mean([ind.enzimas for ind in self.pop])),
        }
        return avg_attributes

    def save_final_gene_attributes(self, selected_gene_ids):
        logging.info(
            f"Saving final gene attributes for simulation_id={self.current_simulation_id}"
        )
        """Guarda solo los genes activos (seleccionados por el usuario) al final de la simulación."""
        session = get_session()
        antibiotico_id = self.current_ab["id"] if self.current_ab else None
        generacion_final = self.current_step - 1

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

        atributos = [
            "recubrimiento",
            "reproduccion",
            "letalidad",
            "permeabilidad",
            "enzimas",
        ]

        for atributo in atributos:
            valores = [getattr(ind, atributo) for ind in self.pop]
            promedio = float(np.mean(valores)) if valores else 0.0
            std = float(np.std(valores)) if valores else 0.0
            sim_attr = SimulacionAtributos(
                simulacion_id=self.current_simulation_id,
                generacion=generacion_final,
                antibiotico_id=antibiotico_id,
                atributo=atributo,
                valor_promedio=promedio,
                desviacion_std=std,
            )
            session.add(sim_attr)
        session.commit()
        session.close()