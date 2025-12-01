import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import logging
from src.core.breakpoint_service import BreakpointService

logger = logging.getLogger(__name__)


@dataclass
class MICDeterminationResult:
    mic_virtual: float
    concentration_tested: List[float]
    od_final: List[float]
    growth_detected: List[bool]
    turbidity_threshold: float


class VirtualMICCalculator:
    def __init__(
        self,
        od_threshold: float = 0.3,
        incubation_hours: float = 18.0,
        standard: str = "EUCAST",
    ):
        self.od_threshold = od_threshold
        self.incubation_hours = incubation_hours
        self.standard = standard
        self.breakpoint_service = BreakpointService(use_cache=True)

    def get_turbidity_threshold(
        self, antibiotic: str, organism: str = "Pseudomonas aeruginosa"
    ) -> float:
        # UMBRAL EUCAST/CLSI: Consulta breakpoint S desde base de datos
        # El umbral de turbidez correlaciona con MIC sensible (S≤ breakpoint)
        breakpoint = self.breakpoint_service.get_breakpoint(antibiotic, self.standard)
        if breakpoint and breakpoint.s_mic:
            # Factor de conversión: OD correlaciona con concentración efectiva
            # OD_threshold ≈ 0.1 × log10(S_MIC) + 0.2 (calibración empírica)
            computed_threshold = 0.1 * np.log10(max(breakpoint.s_mic, 0.125)) + 0.2
            logger.debug(
                f"Using {self.standard} S_MIC={breakpoint.s_mic} → OD threshold={computed_threshold:.3f}"
            )
            return max(0.1, min(computed_threshold, 0.5))
        # Fallback: umbral por defecto si no hay breakpoint
        logger.warning(
            f"No {self.standard} breakpoint for {antibiotic}, using default OD={self.od_threshold}"
        )
        return self.od_threshold

    def determine_growth(
        self, od_final: float, threshold: Optional[float] = None
    ) -> bool:
        effective_threshold = threshold if threshold is not None else self.od_threshold
        return od_final >= effective_threshold

    def calculate_mic_from_od_series(
        self,
        concentrations: np.ndarray,
        od_values: np.ndarray,
        threshold: Optional[float] = None,
    ) -> float:
        # UMBRAL EUCAST/CLSI: Usa umbral dinámico si se proporciona
        effective_threshold = threshold if threshold is not None else self.od_threshold
        growth_status = od_values >= effective_threshold

        inhibited_indices = np.where(~growth_status)[0]

        if len(inhibited_indices) == 0:
            return concentrations[-1] * 2

        if inhibited_indices[0] == 0:
            return concentrations[0]

        mic_index = inhibited_indices[0]
        return concentrations[mic_index]

    def calculate_mic_interpolated(
        self,
        concentrations: np.ndarray,
        od_values: np.ndarray,
        threshold: Optional[float] = None,
    ) -> float:
        # UMBRAL EUCAST/CLSI: Usa umbral dinámico para interpolación precisa
        effective_threshold = threshold if threshold is not None else self.od_threshold

        if len(concentrations) < 2:
            return self.calculate_mic_from_od_series(
                concentrations, od_values, effective_threshold
            )

        growth_status = od_values >= effective_threshold
        inhibited_indices = np.where(~growth_status)[0]

        if len(inhibited_indices) == 0:
            return concentrations[-1] * 2

        if inhibited_indices[0] == 0:
            return concentrations[0]

        idx_below = inhibited_indices[0]
        idx_above = idx_below - 1

        c_below = concentrations[idx_below]
        c_above = concentrations[idx_above]
        od_below = od_values[idx_below]
        od_above = od_values[idx_above]

        if od_above == od_below:
            return c_below

        weight = (effective_threshold - od_below) / (od_above - od_below)
        mic_interpolated = c_below - weight * (c_below - c_above)

        return mic_interpolated

    def generate_concentration_series(
        self,
        min_conc: float = 0.125,
        max_conc: float = 256.0,
        dilution_factor: float = 2.0,
    ) -> np.ndarray:
        concentrations = []
        current = min_conc
        while current <= max_conc:
            concentrations.append(current)
            current *= dilution_factor
        return np.array(concentrations)

    def round_to_standard_dilution(self, mic_value: float) -> float:
        standard_dilutions = np.array(
            [
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
        )
        idx = np.argmin(np.abs(standard_dilutions - mic_value))
        return standard_dilutions[idx]

    def determine_mic(
        self,
        concentrations: List[float],
        od_values: List[float],
        interpolate: bool = False,
        antibiotic: Optional[str] = None,
        apply_noise: bool = False,
        noise_cv: float = 0.05,
    ) -> MICDeterminationResult:
        conc_array = np.array(concentrations)
        od_array = np.array(od_values)

        # RUIDO EXPERIMENTAL: Simula variabilidad inter-pozo (CLSI M07: CV 5%)
        # Aplica ruido gaussiano multiplicativo a lecturas OD
        if apply_noise:
            noise_factors = np.random.lognormal(0, noise_cv, size=len(od_array))
            od_array = od_array * noise_factors
            logger.debug(f"Applied inter-well noise: CV={noise_cv:.2%}")

        # UMBRAL EUCAST/CLSI: Obtener umbral específico del antibiótico si se proporciona
        if antibiotic:
            threshold = self.get_turbidity_threshold(antibiotic)
            logger.info(
                f"Using {self.standard} threshold for {antibiotic}: OD≥{threshold:.3f}"
            )
        else:
            threshold = self.od_threshold
            logger.debug(f"Using default threshold: OD≥{threshold:.3f}")

        growth_detected = od_array >= threshold

        if interpolate:
            mic_raw = self.calculate_mic_interpolated(conc_array, od_array, threshold)
        else:
            mic_raw = self.calculate_mic_from_od_series(conc_array, od_array, threshold)

        mic_rounded = self.round_to_standard_dilution(mic_raw)

        od_list = od_values if isinstance(od_values, list) else od_array.tolist()

        return MICDeterminationResult(
            mic_virtual=mic_rounded,
            concentration_tested=concentrations,
            od_final=od_list,
            growth_detected=growth_detected.tolist(),
            turbidity_threshold=threshold,
        )
