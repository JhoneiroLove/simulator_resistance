from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field
import logging

from src.core.evolutionary_engine import EvolutionaryEngine
from src.core.pharmacodynamic_model import IntegratedGrowthInhibitionModel
from src.core.virtual_mic_calculator import VirtualMICCalculator
from src.core.genotype_phenotype_calculator import GenotypePhenotypeCalculator
from src.core.fitness_calculator import FitnessCalculator

logger = logging.getLogger(__name__)


@dataclass
class PopulationState:
    timestep: int
    genotype: List[str]
    population: float
    od: float
    mic_current: float
    fitness_cost: float


@dataclass
class SimulationResult:
    antibiotic: str
    concentration: float
    final_od: float
    final_population: float
    final_genotype: List[str]
    mic_virtual: float
    mutation_events: int
    population_history: List[PopulationState] = field(default_factory=list)
    time_array: np.ndarray = field(default_factory=lambda: np.array([]))
    od_array: np.ndarray = field(default_factory=lambda: np.array([]))


class MechanisticPredictionEngine:
    def __init__(
        self,
        base_mu: float = 0.69,
        base_K: float = 2e9,
        N0: float = 1e5,
        hill_coefficient: float = 4.0,
        od_threshold: float = 0.3,
        incubation_hours: float = 18.0,
        timestep_hours: float = 0.1,
        standard: str = "EUCAST",
        stochastic: bool = True,
        noise_sigma: float = 0.05,
        seed: Optional[int] = None,
    ):
        self.base_mu = base_mu
        self.base_K = base_K
        self.N0 = N0
        self.hill_coefficient = hill_coefficient
        self.od_threshold = od_threshold
        self.incubation_hours = incubation_hours
        self.timestep_hours = timestep_hours
        self.standard = standard
        self.stochastic = stochastic
        self.noise_sigma = noise_sigma
        self.seed = seed

        self.evolution_engine = EvolutionaryEngine()
        self.pd_model = IntegratedGrowthInhibitionModel(
            base_mu,
            base_K,
            N0,
            hill_coefficient,
            stochastic=stochastic,
            noise_sigma=noise_sigma,
            seed=seed,
        )
        # UMBRAL EUCAST/CLSI: Se pasa el estándar al calculador de MIC
        self.mic_calculator = VirtualMICCalculator(
            od_threshold, incubation_hours, standard
        )
        self.genotype_calc = GenotypePhenotypeCalculator()
        self.fitness_calc = FitnessCalculator()

    def simulate_well(
        self,
        antibiotic: str,
        concentration: float,
        initial_genotype: List[str] = None,
    ) -> SimulationResult:
        genotype = initial_genotype or []
        N_current = self.N0

        mic_result = self.genotype_calc.calculate_mic(antibiotic, genotype)
        mic_current = mic_result.mic_calculado
        ic50 = mic_current

        fitness_result = self.fitness_calc.calculate_fitness(genotype)
        mu_current = self.base_mu * fitness_result.relative_growth_rate

        self.pd_model.base_mu = mu_current

        steps = int(self.incubation_hours / self.timestep_hours)
        population_history = []
        mutation_count = 0

        for step in range(steps):
            N_current = self.pd_model.simulate_timestep(
                N_current, concentration, ic50, self.timestep_hours
            )
            od_current = N_current / 1e9

            genotype, mutated = self.evolution_engine.attempt_mutation(
                genotype, concentration, mic_current, step, self.timestep_hours
            )

            if mutated:
                mutation_count += 1
                mic_result = self.genotype_calc.calculate_mic(antibiotic, genotype)
                mic_current = mic_result.mic_calculado
                ic50 = mic_current

                fitness_result = self.fitness_calc.calculate_fitness(genotype)
                mu_current = self.base_mu * fitness_result.relative_growth_rate
                self.pd_model.base_mu = mu_current

            population_history.append(
                PopulationState(
                    step,
                    genotype.copy(),
                    N_current,
                    od_current,
                    mic_current,
                    fitness_result.total_fitness_cost,
                )
            )

        final_od = population_history[-1].od if population_history else 0.0
        final_population = (
            population_history[-1].population if population_history else 0
        )
        final_genotype = population_history[-1].genotype if population_history else []

        time_array = np.array(
            [s.timestep * self.timestep_hours for s in population_history]
        )
        od_array = np.array([s.od for s in population_history])

        return SimulationResult(
            antibiotic=antibiotic,
            concentration=concentration,
            final_od=final_od,
            final_population=final_population,
            final_genotype=final_genotype,
            mic_virtual=mic_current,
            mutation_events=mutation_count,
            population_history=population_history,
            time_array=time_array,
            od_array=od_array,
        )

    def simulate_mic_determination(
        self,
        antibiotic: str,
        initial_genotype: List[str] = None,
        concentration_range: Optional[Tuple[float, float]] = None,
    ) -> Dict[str, any]:
        if concentration_range is None:
            concentration_range = (0.125, 256.0)

        concentrations = self.mic_calculator.generate_concentration_series(
            concentration_range[0], concentration_range[1]
        )

        od_finals = []
        genotypes_final = []

        for conc in concentrations:
            result = self.simulate_well(antibiotic, conc, initial_genotype)
            od_finals.append(result.final_od)
            genotypes_final.append(result.final_genotype)

        # UMBRAL EUCAST/CLSI: Se pasa el nombre del antibiótico para usar su umbral específico
        mic_result = self.mic_calculator.determine_mic(
            concentrations.tolist(), od_finals, interpolate=True, antibiotic=antibiotic
        )

        return {
            "antibiotic": antibiotic,
            "mic_virtual": mic_result.mic_virtual,
            "concentrations": concentrations.tolist(),
            "od_finals": od_finals,
            "growth_detected": mic_result.growth_detected,
            "genotypes_final": genotypes_final,
            "standard_used": self.standard,
            "turbidity_threshold": mic_result.turbidity_threshold,
        }

    def batch_simulate_panel(
        self, antibiotics: List[str], initial_genotype: List[str] = None
    ) -> Dict[str, Dict]:
        results = {}
        for antibiotic in antibiotics:
            results[antibiotic] = self.simulate_mic_determination(
                antibiotic, initial_genotype
            )
        return results
