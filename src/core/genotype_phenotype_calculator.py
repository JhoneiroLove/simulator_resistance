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
        Obtiene MICs basales de P. aeruginosa wild-type desde la base de datos.

        Los valores se cargan una sola vez y se cachean en memoria.
        Todos los valores tienen referencias PMID verificadas (ver tabla baseline_mics).

        Returns:
            Diccionario antibiótico → MIC basal (µg/mL)

        Raises:
            RuntimeError: Si no hay datos en baseline_mics (migración no ejecutada).
        """
        if self._baseline_mics is None:
            from src.data.database import get_session
            from src.data.models import BaselineMIC

            try:
                session = get_session()
                baseline_records = session.query(BaselineMIC).all()
                session.close()

                if not baseline_records:
                    raise RuntimeError(
                        "No baseline MICs found in database. "
                        "Run migration 019_baseline_mics.sql first."
                    )

                self._baseline_mics = {
                    record.antibiotico: record.mic_wt for record in baseline_records
                }
                logger.debug(
                    f"Loaded {len(self._baseline_mics)} baseline MICs from database"
                )

            except Exception as e:
                # Fallback temporal: delegar a bacteria_profile_generator
                import warnings
                from src.core.bacteria_profile_generator import get_baseline_mics

                warnings.warn(
                    f"Could not load baseline MICs from database: {e}. "
                    "Using fallback function. Please run migration 019.",
                    UserWarning,
                )
                self._baseline_mics = get_baseline_mics()
                logger.debug(
                    f"Loaded {len(self._baseline_mics)} baseline MICs (fallback)"
                )

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
        self, antibiotico: str, genes_mutados: List[str], stochastic: bool = False
    ) -> MICCalculationResult:
        """
        Calcula MIC para un antibiótico dado un genotipo.

        Formula:
            MIC_determinístico = MIC_base × ∏(multiplicadores de genes mutados)
            MIC_estocástico = MIC_determinístico × factor_aleatorio

        donde factor_aleatorio ~ LogNormal(μ=0, σ=0.3), equivalente a variabilidad ±1 dilución.

        Args:
            antibiotico: Nombre del antibiótico (ej: 'Meropenem')
            genes_mutados: Lista de genes mutados (ej: ['oprD_loss', 'blaVIM_or_blaIMP'])
            stochastic: Si True, aplica variabilidad biológica estocástica (default: False)

        Returns:
            MICCalculationResult con detalles del cálculo

        Example:
            >>> calc = GenotypePhenotypeCalculator()
            >>> result = calc.calculate_mic('Meropenem', ['oprD_loss', 'blaVIM_or_blaIMP'])
            >>> result.mic_calculado
            64.0  # 0.5 × 8.0 × 16.0 = 64.0 (determinístico)
            >>> result_stoch = calc.calculate_mic('Meropenem', ['oprD_loss'], stochastic=True)
            >>> result_stoch.mic_calculado
            3.2  # Podría variar: 2.0-8.0 (±1 dilución respecto a 4.0 base)
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

        # Aplicar variabilidad estocástica si se requiere
        if stochastic:
            import numpy as np

            # Log-normal con σ=0.3 → rango típico ±1 dilución (0.5x - 2x)
            # PMID:29021270 (CLSI M07): variabilidad biológica ±1 dilución es aceptable
            random_factor = np.random.lognormal(mean=0, sigma=0.3)
            mic_calculado *= random_factor

            # Redondear al nearest standard dilution (serie de 2x)
            mic_calculado = self._round_to_standard_dilution(mic_calculado)
            logger.debug(
                f"Applied stochastic factor {random_factor:.3f} → {mic_calculado}"
            )
        else:
            mic_calculado = round(mic_calculado, 3)

        logger.debug(
            f"{antibiotico}: MIC_base={mic_base} × {multiplicadores} = {mic_calculado} "
            f"(genes: {genes_aplicados}, stochastic={stochastic})"
        )

        return MICCalculationResult(
            antibiotico=antibiotico,
            mic_base=mic_base,
            mic_calculado=mic_calculado,
            genes_aplicados=genes_aplicados,
            multiplicadores=multiplicadores,
        )

    def calculate_all_mics(
        self, genes_mutados: List[str], stochastic: bool = False
    ) -> Dict[str, MICCalculationResult]:
        """
        Calcula MICs para TODOS los antibióticos del panel dado un genotipo.

        Args:
            genes_mutados: Lista de genes mutados (ej: ['gyrA_T83I', 'oprD_loss'])
            stochastic: Si True, aplica variabilidad biológica estocástica (default: False)

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
            results[antibiotico] = self.calculate_mic(
                antibiotico, genes_mutados, stochastic
            )

        logger.info(
            f"Calculated MICs for {len(results)} antibiotics "
            f"with {len(genes_mutados)} mutations (stochastic={stochastic})"
        )

        return results

    def get_mics_as_dict(
        self, genes_mutados: List[str], stochastic: bool = False
    ) -> Dict[str, float]:
        """
        Versión simplificada que retorna solo el diccionario MIC.

        Útil para integración rápida con código existente.

        Args:
            genes_mutados: Lista de genes mutados
            stochastic: Si True, aplica variabilidad biológica estocástica (default: False)

        Returns:
            Diccionario antibiótico → MIC calculado

        Example:
            >>> calc = GenotypePhenotypeCalculator()
            >>> mics = calc.get_mics_as_dict(['oprD_loss', 'blaVIM_or_blaIMP'])
            >>> mics['Meropenem']
            64.0
        """
        results = self.calculate_all_mics(genes_mutados, stochastic)
        return {ab: result.mic_calculado for ab, result in results.items()}

    def clear_cache(self):
        """Limpia cache de multiplicadores (útil para testing)."""
        self._multipliers_cache = None
        self._baseline_mics = None
        logger.info("Cache cleared")

    def _round_to_standard_dilution(self, mic_value: float) -> float:
        """
        Redondea MIC al nearest standard dilution en serie de 2x.

        La serie estándar CLSI/EUCAST es: 0.03, 0.06, 0.125, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256...

        Args:
            mic_value: MIC calculado (puede ser cualquier valor)

        Returns:
            MIC redondeado al valor estándar más cercano

        Example:
            >>> calc._round_to_standard_dilution(3.7)
            4.0
            >>> calc._round_to_standard_dilution(0.18)
            0.25
        """
        import numpy as np

        # Serie estándar de diluciones (CLSI M07-A11, EUCAST)
        standard_dilutions = [
            0.015,
            0.03,
            0.06,
            0.125,
            0.25,
            0.5,
            1.0,
            2.0,
            4.0,
            8.0,
            16.0,
            32.0,
            64.0,
            128.0,
            256.0,
            512.0,
            1024.0,
        ]

        # Encontrar el valor más cercano
        closest_idx = np.argmin(np.abs(np.array(standard_dilutions) - mic_value))
        return standard_dilutions[closest_idx]

    def calculate_mic_distribution(
        self,
        antibiotico: str,
        genes_mutados: List[str],
        n_samples: int = 1000,
    ) -> Dict[str, any]:
        """
        Calcula distribución de MICs para modelar heteroresistencia.

        Simula variabilidad poblacional mediante distribución log-normal basada en
        datos experimentales de heteroresistencia (tabla heteroresistance_distributions).

        Args:
            antibiotico: Nombre del antibiótico
            genes_mutados: Lista de genes mutados
            n_samples: Número de muestras a generar (default: 1000 = población bacteriana típica)

        Returns:
            Dict con:
                - 'mean_mic': MIC medio poblacional
                - 'median_mic': MIC mediana
                - 'std_mic': Desviación estándar
                - 'samples': Array de MICs simulados
                - 'heteroresistant': Bool indicando si hay heteroresistencia documentada
                - 'prevalence': Prevalencia de subpoblación resistente (si aplica)

        Example:
            >>> calc = GenotypePhenotypeCalculator()
            >>> dist = calc.calculate_mic_distribution('Meropenem', ['oprD_loss'], n_samples=1000)
            >>> dist['mean_mic']
            4.2  # Promedio considerando heteroresistencia
            >>> dist['heteroresistant']
            True  # Heteroresistencia documentada para oprD_loss + Meropenem
        """
        import numpy as np
        from src.data.database import get_session
        from src.data.models import HeteroresistanceDistribution

        # Calcular MIC base determinístico
        base_result = self.calculate_mic(antibiotico, genes_mutados, stochastic=False)
        base_mic = base_result.mic_calculado

        # Buscar distribución heteroresistente en BD
        session = get_session()
        genotype_sig = "+".join(sorted(genes_mutados)) if genes_mutados else "wildtype"

        hetero_record = (
            session.query(HeteroresistanceDistribution)
            .filter_by(antibiotico=antibiotico, genotype_signature=genotype_sig)
            .first()
        )
        session.close()

        if hetero_record:
            # Usar parámetros documentados de heteroresistencia
            mean_log = hetero_record.mean_log_mic
            std_log = hetero_record.std_log_mic
            prevalence = hetero_record.prevalence

            # Generar muestras log-normal
            log_mics = np.random.normal(mean_log, std_log, n_samples)
            samples = np.power(10, log_mics)

            # Redondear a diluciones estándar
            samples = np.array(
                [self._round_to_standard_dilution(mic) for mic in samples]
            )

            return {
                "mean_mic": float(np.mean(samples)),
                "median_mic": float(np.median(samples)),
                "std_mic": float(np.std(samples)),
                "samples": samples,
                "heteroresistant": True,
                "prevalence": prevalence,
                "base_mic": base_mic,
                "pmid_reference": hetero_record.pmid_reference,
            }

        else:
            # Sin datos de heteroresistencia: distribución estrecha alrededor del MIC base
            # Variabilidad técnica típica (σ ≈ 0.3 en log10)
            log_base = np.log10(base_mic)
            log_mics = np.random.normal(log_base, 0.3, n_samples)
            samples = np.power(10, log_mics)
            samples = np.array(
                [self._round_to_standard_dilution(mic) for mic in samples]
            )

            return {
                "mean_mic": float(np.mean(samples)),
                "median_mic": float(np.median(samples)),
                "std_mic": float(np.std(samples)),
                "samples": samples,
                "heteroresistant": False,
                "prevalence": None,
                "base_mic": base_mic,
                "pmid_reference": None,
            }


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
