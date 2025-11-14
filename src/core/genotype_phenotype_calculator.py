"""
Calculador genotipo → fenotipo MIC para Pseudomonas aeruginosa.

Este módulo implementa el sistema de cálculo de MICs basado en mutaciones genéticas
usando la matriz gen×clase almacenada en la base de datos.

Funcionalidades:
- Calcular MICs a partir de lista de genes mutados
- Consultar matriz gene_class_multipliers eficientemente
- Aplicar regla multiplicativa: MIC_final = MIC_base × ∏(multiplicadores)
- Cachear datos de DB para performance

Integración:
- bacteria_profile_generator.py: Genera perfiles con MICs calculados
- genetic_algorithm.py: Calcula fitness basado en MICs de individuos evolucionados
- ast_simulator.py: Usa MICs como input para simulación

Autor: Sistema SRB - FASE 4
Fecha: 13 de noviembre de 2025
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MICCalculationResult:
    """
    Resultado del cálculo de MIC para un antibiótico específico.

    Attributes:
        antibiotico: Nombre del antibiótico
        mic_base: MIC basal (wild-type)
        mic_calculado: MIC final después de aplicar multiplicadores
        genes_aplicados: Lista de genes que contribuyeron al MIC
        multiplicadores: Lista de multiplicadores aplicados
        fold_change: Factor de cambio respecto a wild-type (MIC_calc / MIC_base)
    """

    antibiotico: str
    mic_base: float
    mic_calculado: float
    genes_aplicados: List[str]
    multiplicadores: List[float]

    @property
    def fold_change(self) -> float:
        """Calcula el fold-change respecto a wild-type."""
        if self.mic_base == 0:
            return 0.0
        return round(self.mic_calculado / self.mic_base, 2)


class GenotypePhenotypeCalculator:
    """
    Calculador de MICs basado en genotipo bacteriano.

    Usa la matriz gen×clase para calcular MICs específicos por antibiótico.
    Implementa caching para optimizar consultas repetidas.
    """

    def __init__(self):
        """Inicializa calculador con cache vacío."""
        self._multipliers_cache: Optional[Dict[str, Dict[str, float]]] = None
        self._baseline_mics: Optional[Dict[str, float]] = None
        logger.info("GenotypePhenotypeCalculator initialized")

    def get_baseline_mics(self) -> Dict[str, float]:
        """
        Obtiene MICs basales de P. aeruginosa wild-type.

        Returns:
            Diccionario antibiótico → MIC basal (µg/mL)
        """
        if self._baseline_mics is None:
            # Importar localmente para evitar circular import
            try:
                from src.core.bacteria_profile_generator import get_baseline_mics
            except ImportError:
                # Fallback para ejecución directa del script
                import sys
                import os

                sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
                from src.core.bacteria_profile_generator import get_baseline_mics

            self._baseline_mics = get_baseline_mics()
            logger.debug(f"Loaded {len(self._baseline_mics)} baseline MICs")

        return self._baseline_mics

    def load_multipliers_from_db(self) -> Dict[str, Dict[str, float]]:
        """
        Carga matriz gen×clase desde base de datos con cache.

        Estructura retornada:
            {
                'Meropenem': {
                    'oprD_loss': 8.0,
                    'blaVIM_or_blaIMP': 16.0,
                    'ftsI_PBP3_insertion_YRIN': 2.0
                },
                'Ciprofloxacino': {
                    'gyrA_T83I': 8.0,
                    'parC_S87L': 4.0,
                    'mexR_frameshift': 2.0,
                    'nalC_Q83K': 2.0
                },
                ...
            }

        Returns:
            Diccionario anidado: antibiotico → gen → multiplicador
        """
        if self._multipliers_cache is not None:
            return self._multipliers_cache

        from src.data.database import get_session
        from sqlalchemy import text

        session = get_session()

        query = text("""
            SELECT 
                ac.antibiotico,
                gcm.gen,
                gcm.multiplicador_mic
            FROM gene_class_multipliers gcm
            JOIN antibiotic_classes ac ON ac.clase = gcm.clase_antibiotica
            WHERE gcm.multiplicador_mic > 1.0
            ORDER BY ac.antibiotico, gcm.multiplicador_mic DESC
        """)

        result = {}
        rows = session.execute(query).fetchall()

        for antibiotico, gen, multiplicador in rows:
            if antibiotico not in result:
                result[antibiotico] = {}
            result[antibiotico][gen] = multiplicador

        session.close()

        self._multipliers_cache = result
        logger.info(f"Loaded multipliers for {len(result)} antibiotics from DB")

        return result

    def calculate_mic(
        self, antibiotico: str, genes_mutados: List[str]
    ) -> MICCalculationResult:
        """
        Calcula MIC para un antibiótico dado un genotipo.

        Formula:
            MIC_final = MIC_base × ∏(multiplicadores de genes mutados)

        Args:
            antibiotico: Nombre del antibiótico (ej: 'Meropenem')
            genes_mutados: Lista de genes mutados (ej: ['oprD_loss', 'blaVIM_or_blaIMP'])

        Returns:
            MICCalculationResult con detalles del cálculo

        Example:
            >>> calc = GenotypePhenotypeCalculator()
            >>> result = calc.calculate_mic('Meropenem', ['oprD_loss', 'blaVIM_or_blaIMP'])
            >>> result.mic_calculado
            64.0  # 0.5 × 8.0 × 16.0 = 64.0
            >>> result.fold_change
            128.0  # 64.0 / 0.5 = 128x increase
        """
        baseline_mics = self.get_baseline_mics()
        multipliers_db = self.load_multipliers_from_db()

        # Obtener MIC base
        if antibiotico not in baseline_mics:
            logger.warning(f"Antibiotico '{antibiotico}' not found in baseline MICs")
            raise ValueError(f"Unknown antibiotic: {antibiotico}")

        mic_base = baseline_mics[antibiotico]

        # Obtener multiplicadores aplicables
        genes_aplicados = []
        multiplicadores = []

        if antibiotico in multipliers_db:
            for gen in genes_mutados:
                if gen in multipliers_db[antibiotico]:
                    genes_aplicados.append(gen)
                    multiplicadores.append(multipliers_db[antibiotico][gen])

        # Aplicar regla multiplicativa
        mic_calculado = mic_base
        for mult in multiplicadores:
            mic_calculado *= mult

        mic_calculado = round(mic_calculado, 3)

        logger.debug(
            f"{antibiotico}: MIC_base={mic_base} × {multiplicadores} = {mic_calculado} "
            f"(genes: {genes_aplicados})"
        )

        return MICCalculationResult(
            antibiotico=antibiotico,
            mic_base=mic_base,
            mic_calculado=mic_calculado,
            genes_aplicados=genes_aplicados,
            multiplicadores=multiplicadores,
        )

    def calculate_all_mics(
        self, genes_mutados: List[str]
    ) -> Dict[str, MICCalculationResult]:
        """
        Calcula MICs para TODOS los antibióticos del panel dado un genotipo.

        Args:
            genes_mutados: Lista de genes mutados (ej: ['gyrA_T83I', 'oprD_loss'])

        Returns:
            Diccionario antibiótico → MICCalculationResult

        Example:
            >>> calc = GenotypePhenotypeCalculator()
            >>> results = calc.calculate_all_mics(['gyrA_T83I', 'oprD_loss'])
            >>> results['Ciprofloxacino'].mic_calculado
            1.0  # 0.125 × 8.0 = 1.0
            >>> results['Meropenem'].mic_calculado
            4.0  # 0.5 × 8.0 = 4.0
            >>> results['Amikacina'].mic_calculado
            2.0  # Sin genes aplicables, queda en baseline
        """
        baseline_mics = self.get_baseline_mics()
        results = {}

        for antibiotico in baseline_mics.keys():
            results[antibiotico] = self.calculate_mic(antibiotico, genes_mutados)

        logger.info(
            f"Calculated MICs for {len(results)} antibiotics "
            f"with {len(genes_mutados)} mutations"
        )

        return results

    def get_mics_as_dict(self, genes_mutados: List[str]) -> Dict[str, float]:
        """
        Versión simplificada que retorna solo el diccionario MIC.

        Útil para integración rápida con código existente.

        Args:
            genes_mutados: Lista de genes mutados

        Returns:
            Diccionario antibiótico → MIC calculado

        Example:
            >>> calc = GenotypePhenotypeCalculator()
            >>> mics = calc.get_mics_as_dict(['oprD_loss', 'blaVIM_or_blaIMP'])
            >>> mics['Meropenem']
            64.0
        """
        results = self.calculate_all_mics(genes_mutados)
        return {ab: result.mic_calculado for ab, result in results.items()}

    def clear_cache(self):
        """Limpia cache de multiplicadores (útil para testing)."""
        self._multipliers_cache = None
        self._baseline_mics = None
        logger.info("Cache cleared")


def calculate_mics_from_genotype(genes_mutados: List[str]) -> Dict[str, float]:
    """
    Función de utilidad para cálculo rápido de MICs.

    Esta es una función standalone que internamente usa GenotypePhenotypeCalculator.
    Útil para imports rápidos sin crear instancia.

    Args:
        genes_mutados: Lista de genes mutados

    Returns:
        Diccionario antibiótico → MIC calculado

    Example:
        >>> from src.core.genotype_phenotype_calculator import calculate_mics_from_genotype
        >>> mics = calculate_mics_from_genotype(['gyrA_T83I', 'parC_S87L'])
        >>> mics['Ciprofloxacino']
        4.0  # 0.125 × 8.0 × 4.0 = 4.0
    """
    calc = GenotypePhenotypeCalculator()
    return calc.get_mics_as_dict(genes_mutados)
