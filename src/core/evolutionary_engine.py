from typing import List, Tuple, Dict
import random
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MutationEvent:
    timestep: int
    gene: str
    mutation_probability: float


class EvolutionaryEngine:
    def __init__(
        self,
        base_mutation_rate: float = 1e-7,
        antibiotic_stress_multiplier: float = 100.0,
        available_resistance_genes: List[str] = None,
    ):
        self.base_mutation_rate = base_mutation_rate
        self.antibiotic_stress_multiplier = antibiotic_stress_multiplier
        self.available_genes = available_resistance_genes or self._default_genes()
        self.mutation_history: List[MutationEvent] = []

    def _default_genes(self) -> List[str]:
        return [
            "oprD_loss",
            "blaVIM_or_blaIMP",
            "gyrA_T83I",
            "parC_S87L",
            "mexR_frameshift",
            "nalC_Q83K",
        ]

    def calculate_mutation_probability(
        self, antibiotic_concentration: float, mic_current: float, timestep_hours: float
    ) -> float:
        if antibiotic_concentration == 0:
            return self.base_mutation_rate * timestep_hours

        stress_factor = antibiotic_concentration / max(mic_current, 0.001)
        effective_rate = (
            self.base_mutation_rate
            * (1.0 + self.antibiotic_stress_multiplier * stress_factor)
            * timestep_hours
        )
        return min(effective_rate, 0.1)

    def attempt_mutation(
        self,
        current_genotype: List[str],
        antibiotic_concentration: float,
        mic_current: float,
        timestep: int,
        timestep_hours: float = 0.1,
    ) -> Tuple[List[str], bool]:
        mutation_prob = self.calculate_mutation_probability(
            antibiotic_concentration, mic_current, timestep_hours
        )

        if random.random() < mutation_prob:
            available_new = [
                g for g in self.available_genes if g not in current_genotype
            ]
            if available_new:
                new_gene = random.choice(available_new)
                new_genotype = current_genotype + [new_gene]
                self.mutation_history.append(
                    MutationEvent(timestep, new_gene, mutation_prob)
                )
                logger.debug(
                    f"t={timestep}: Mutation {new_gene} | P={mutation_prob:.2e}"
                )
                return new_genotype, True

        return current_genotype, False

    def reset_history(self):
        self.mutation_history = []
