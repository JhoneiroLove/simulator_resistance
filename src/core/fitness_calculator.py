"""
Fitness Calculator - Cálculo de costos de fitness para genotipos resistentes.

Este módulo calcula el costo biológico acumulado de múltiples mecanismos de resistencia.
Esencial para modelar:
- Evolución bacteriana (algoritmo genético)
- Curvas de crecimiento realistas
- Competencia entre cepas
- Reversión evolutiva sin presión selectiva

Autor: Sistema AST - Fase B
Fecha: 14 de noviembre de 2025
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FitnessResult:
    """
    Resultado de cálculo de fitness para un genotipo.

    Attributes:
        genotype: Lista de genes mutados
        total_fitness_cost: Costo acumulado (0-1, donde 1 = letal)
        relative_growth_rate: Tasa de crecimiento relativa vs WT (0-1)
        doubling_time_min: Tiempo de duplicación en minutos
        competitive_index: Índice competitivo vs wild-type
        genes_with_cost: Genes que contribuyen al costo
        cost_breakdown: Dict gen → costo individual
    """

    genotype: List[str]
    total_fitness_cost: float
    relative_growth_rate: float
    doubling_time_min: float
    competitive_index: float
    genes_with_cost: List[str]
    cost_breakdown: Dict[str, float]


class FitnessCalculator:
    """
    Calculador de fitness para genotipos de P. aeruginosa resistente.

    Carga costos de fitness desde la base de datos y calcula métricas acumuladas
    para genotipos con múltiples mutaciones.

    Modelo multiplicativo:
        CI_total = product(CI_individual)
        Growth_rate_total = 1 - sum(penalties)

    Referencias:
        - PMID:19258524 - Fitness costs in P. aeruginosa
        - PMID:21876761 - OprD loss impacts
        - PMID:25691624 - Carbapenemase burden
    """

    # Constantes biológicas
    WT_DOUBLING_TIME_MIN = 20.0  # P. aeruginosa wild-type en LB broth 37°C

    def __init__(self):
        """Inicializa calculador con cache vacío."""
        self._fitness_cache: Optional[Dict[str, float]] = None
        self._ci_cache: Optional[Dict[str, float]] = None
        logger.info("FitnessCalculator initialized")

    def load_fitness_costs(self) -> Dict[str, Dict[str, float]]:
        """
        Carga costos de fitness desde la base de datos.

        Returns:
            Dict con estructura:
                {
                    'gen_name': {
                        'fitness_cost': 0.15,
                        'growth_rate_penalty': 12.0,
                        'doubling_time_increase': 8.0,
                        'competitive_index': 0.85
                    },
                    ...
                }
        """
        if self._fitness_cache is not None:
            return self._fitness_cache

        from src.data.database import get_session
        from src.data.models import FitnessCost

        session = get_session()
        records = session.query(FitnessCost).all()
        session.close()

        if not records:
            logger.warning("No fitness costs found in database. Using defaults.")
            return {}

        result = {}
        for record in records:
            result[record.gen] = {
                "fitness_cost": record.fitness_cost,
                "growth_rate_penalty": record.growth_rate_penalty,
                "doubling_time_increase": record.doubling_time_increase,
                "competitive_index": record.competitive_index,
            }

        self._fitness_cache = result
        logger.info(f"Loaded fitness costs for {len(result)} genes")
        return result

    def calculate_fitness(self, genes_mutados: List[str]) -> FitnessResult:
        """
        Calcula métricas de fitness para un genotipo.

        Args:
            genes_mutados: Lista de genes con mutaciones de resistencia

        Returns:
            FitnessResult con todas las métricas calculadas

        Example:
            >>> calc = FitnessCalculator()
            >>> result = calc.calculate_fitness(['oprD_loss', 'blaVIM_or_blaIMP'])
            >>> result.total_fitness_cost
            0.455  # ~45% costo acumulado
            >>> result.competitive_index
            0.553  # 0.85 × 0.65 = desventaja severa vs WT
            >>> result.doubling_time_min
            46.0  # 20 + 8 + 18 = duplica lentamente
        """
        fitness_data = self.load_fitness_costs()

        if not genes_mutados:
            # Wild-type: sin costo
            return FitnessResult(
                genotype=[],
                total_fitness_cost=0.0,
                relative_growth_rate=1.0,
                doubling_time_min=self.WT_DOUBLING_TIME_MIN,
                competitive_index=1.0,
                genes_with_cost=[],
                cost_breakdown={},
            )

        # Acumular costos
        total_cost = 0.0
        total_growth_penalty = 0.0
        total_doubling_increase = 0.0
        ci_product = 1.0
        genes_with_cost = []
        cost_breakdown = {}

        for gen in genes_mutados:
            if gen in fitness_data:
                data = fitness_data[gen]
                cost = data["fitness_cost"]
                growth_penalty = data["growth_rate_penalty"]
                doubling_increase = data["doubling_time_increase"]
                ci = data["competitive_index"]

                # Acumular (modelo aditivo para costos, multiplicativo para CI)
                total_cost += cost
                total_growth_penalty += growth_penalty
                total_doubling_increase += doubling_increase
                ci_product *= ci

                genes_with_cost.append(gen)
                cost_breakdown[gen] = cost

        # Normalizar costo total (máximo 1.0)
        total_cost = min(total_cost, 1.0)

        # Calcular tasa de crecimiento relativa
        relative_growth = max(1.0 - (total_growth_penalty / 100.0), 0.01)

        # Calcular tiempo de duplicación
        doubling_time = self.WT_DOUBLING_TIME_MIN + total_doubling_increase

        logger.debug(
            f"Fitness calculated for {len(genes_mutados)} genes: "
            f"cost={total_cost:.3f}, CI={ci_product:.3f}, "
            f"doubling_time={doubling_time:.1f}min"
        )

        return FitnessResult(
            genotype=genes_mutados,
            total_fitness_cost=total_cost,
            relative_growth_rate=relative_growth,
            doubling_time_min=doubling_time,
            competitive_index=ci_product,
            genes_with_cost=genes_with_cost,
            cost_breakdown=cost_breakdown,
        )

    def compare_genotypes(
        self, genotype_a: List[str], genotype_b: List[str]
    ) -> Dict[str, float]:
        """
        Compara fitness de dos genotipos.

        Args:
            genotype_a: Primer genotipo
            genotype_b: Segundo genotipo

        Returns:
            Dict con métricas comparativas:
                - 'ci_ratio': CI_A / CI_B (>1 = A es más fit)
                - 'growth_advantage': % ventaja en tasa crecimiento
                - 'doubling_time_diff': diferencia en minutos

        Example:
            >>> calc = FitnessCalculator()
            >>> comp = calc.compare_genotypes(['oprD_loss'], ['oprD_loss', 'blaVIM_or_blaIMP'])
            >>> comp['ci_ratio']
            1.31  # 0.85 / 0.65 = oprD_loss solo es más fit
        """
        fitness_a = self.calculate_fitness(genotype_a)
        fitness_b = self.calculate_fitness(genotype_b)

        ci_ratio = fitness_a.competitive_index / max(fitness_b.competitive_index, 0.01)
        growth_advantage = (
            fitness_a.relative_growth_rate - fitness_b.relative_growth_rate
        ) * 100
        doubling_diff = fitness_a.doubling_time_min - fitness_b.doubling_time_min

        return {
            "ci_ratio": ci_ratio,
            "growth_advantage_pct": growth_advantage,
            "doubling_time_diff_min": doubling_diff,
            "winner": "A" if ci_ratio > 1.0 else "B" if ci_ratio < 1.0 else "Tie",
        }

    def clear_cache(self):
        """Limpia cache (útil para testing)."""
        self._fitness_cache = None
        self._ci_cache = None
        logger.info("Cache cleared")


def calculate_fitness_from_genotype(genes_mutados: List[str]) -> FitnessResult:
    """
    Función standalone para cálculo rápido de fitness.

    Args:
        genes_mutados: Lista de genes mutados

    Returns:
        FitnessResult

    Example:
        >>> from src.core.fitness_calculator import calculate_fitness_from_genotype
        >>> result = calculate_fitness_from_genotype(['oprD_loss', 'mexR_frameshift'])
        >>> result.competitive_index
        0.697  # 0.85 × 0.82 = doble desventaja
    """
    calc = FitnessCalculator()
    return calc.calculate_fitness(genes_mutados)
