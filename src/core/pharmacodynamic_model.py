import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PharmacodynamicParameters:
    e_max: float = 1.0
    ic50: float = 1.0
    hill_coefficient: float = 4.0


class HillInhibitionModel:
    def __init__(
        self,
        e_max: float = 1.0,
        hill_coefficient: float = 4.0,
    ):
        self.e_max = e_max
        self.hill_coefficient = hill_coefficient

    def calculate_inhibition_fraction(self, concentration: float, ic50: float) -> float:
        if concentration <= 0 or ic50 <= 0:
            return 0.0

        ratio = concentration / ic50
        inhibition = (
            self.e_max
            * (ratio**self.hill_coefficient)
            / (1.0 + ratio**self.hill_coefficient)
        )
        return min(inhibition, 1.0)

    def calculate_survival_fraction(self, concentration: float, ic50: float) -> float:
        return 1.0 - self.calculate_inhibition_fraction(concentration, ic50)

    def modulate_growth_rate(
        self, base_mu: float, concentration: float, ic50: float
    ) -> float:
        survival = self.calculate_survival_fraction(concentration, ic50)
        return base_mu * survival

    def modulate_carrying_capacity(
        self, base_k: float, concentration: float, ic50: float
    ) -> float:
        survival = self.calculate_survival_fraction(concentration, ic50)
        return base_k * survival


class LogisticGrowthModel:
    def __init__(self, mu: float, K: float, N0: float = 1e5):
        self.mu = mu
        self.K = K
        self.N0 = N0

    def calculate_population(self, t: float) -> float:
        exp_term = np.exp(-self.mu * t)
        N = (self.K * self.N0) / (self.N0 + (self.K - self.N0) * exp_term)
        return N

    def od_from_population(self, N: float) -> float:
        return N / 1e9


class IntegratedGrowthInhibitionModel:
    def __init__(
        self,
        base_mu: float = 0.69,
        base_K: float = 2e9,
        N0: float = 1e5,
        hill_coefficient: float = 4.0,
        e_max: float = 1.0,
        stochastic: bool = True,
        noise_sigma: float = 0.05,
        seed: Optional[int] = None,
    ):
        self.base_mu = base_mu
        self.base_K = base_K
        self.N0 = N0
        self.stochastic = stochastic
        self.noise_sigma = noise_sigma
        self.hill_model = HillInhibitionModel(e_max, hill_coefficient)

        if seed is not None:
            np.random.seed(seed)

    def simulate_timestep(
        self, N_current: float, concentration: float, ic50: float, dt: float
    ) -> float:
        mu_effective = self.hill_model.modulate_growth_rate(
            self.base_mu, concentration, ic50
        )
        K_effective = self.hill_model.modulate_carrying_capacity(
            self.base_K, concentration, ic50
        )

        if K_effective == 0:
            return N_current

        dN_dt = mu_effective * N_current * (1.0 - N_current / K_effective)

        # RUIDO EXPERIMENTAL: Término estocástico Langevin (variabilidad biológica)
        # Basado en CLSI M07: CV típico 5% en crecimiento bacteriano
        if self.stochastic and N_current > 0:
            noise_term = np.random.normal(0, self.noise_sigma * np.sqrt(N_current * dt))
            dN_dt += noise_term

        N_next = N_current + dN_dt * dt
        return max(N_next, 0)

    def simulate_growth_curve(
        self, concentration: float, ic50: float, time_hours: float, dt: float = 0.1
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        steps = int(time_hours / dt)
        time = np.linspace(0, time_hours, steps)
        population = np.zeros(steps)
        od = np.zeros(steps)

        # RUIDO EXPERIMENTAL: Variabilidad inicial (pipeteo de inóculo)
        # CLSI M07: CV 5-10% en diluciones de inóculo
        N0_effective = self.N0
        if self.stochastic:
            pipette_cv = 0.05
            N0_effective = self.N0 * np.random.lognormal(0, pipette_cv)

        population[0] = N0_effective
        od[0] = population[0] / 1e9

        for i in range(1, steps):
            population[i] = self.simulate_timestep(
                population[i - 1], concentration, ic50, dt
            )
            # RUIDO EXPERIMENTAL: Variabilidad en lectura de OD (fotómetro)
            # CLSI M07: CV instrumental 2-5%
            od_raw = population[i] / 1e9
            if self.stochastic and od_raw > 0:
                od[i] = od_raw * np.random.lognormal(0, 0.03)
            else:
                od[i] = od_raw

        return time, population, od
