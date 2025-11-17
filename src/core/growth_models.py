"""
Módulo Growth Models - Modelos Matemáticos de Crecimiento Bacteriano

Este módulo implementa funciones matemáticas para simular el crecimiento
bacteriano en presencia de antibióticos, incluyendo:
- Curva logística de Verhulst
- Inhibición por antibióticos (ecuación de Hill)
- Ruido experimental multicapa REALISTA (MEJORADO v2.0)
- Variabilidad biológica en parámetros de crecimiento
- Wells que fallan (eventos raros)
- Clasificación de turbidez

Autor: Sistema AST Simulator
Fecha: 17 de noviembre de 2025
Versión: 2.0 - Ruido Experimental Realista
"""

import math
import random
from typing import Tuple, List, Optional
import numpy as np


def logistic_growth(
    t: float, od_max: float, k: float, t_mid: float, od_initial: float = 0.05
) -> float:
    """
    Modelo de crecimiento logístico de Verhulst.

    Simula el crecimiento bacteriano como una curva sigmoide que alcanza
    una densidad óptica máxima (capacidad de carga del medio).

    Ecuación:
        OD(t) = OD_initial + (OD_max - OD_initial) / (1 + exp(-k*(t - t_mid)))

    Args:
        t: Tiempo en minutos desde inicio de incubación
        od_max: Densidad óptica máxima alcanzable (capacidad de carga)
        k: Tasa de crecimiento (min⁻¹), típicamente 0.01-0.03
        t_mid: Tiempo del punto de inflexión en minutos (50% de crecimiento)
        od_initial: Densidad óptica inicial del inóculo

    Returns:
        Densidad óptica (OD600) en el tiempo t

    Ejemplo:
        >>> od = logistic_growth(t=480, od_max=2.0, k=0.02, t_mid=480, od_initial=0.05)
        >>> print(f"OD a las 8h: {od:.3f}")
        OD a las 8h: 1.025
    """
    exponente = -k * (t - t_mid)

    # Evitar overflow en exp()
    if exponente > 100:
        exponente = 100
    elif exponente < -100:
        exponente = -100

    od = od_initial + (od_max - od_initial) / (1 + math.exp(exponente))

    return od


def calculate_od_max_with_antibiotic(
    base_od_max: float,
    concentration: float,
    mic_real: float,
    hill_coefficient: float = 4.0,
) -> float:
    """
    Calcula OD máxima reducida por efecto del antibiótico.

    Usa la ecuación de Hill para modelar la inhibición del crecimiento
    bacteriano por antibióticos. A mayor concentración relativa al MIC,
    menor será la densidad máxima alcanzable.

    Ecuación de Hill:
        Supervivencia = 1 / (1 + (C/MIC)^n)
        OD_max_inhibido = OD_max_base × Supervivencia

    Args:
        base_od_max: OD máxima sin antibiótico (típicamente 2.0)
        concentration: Concentración de antibiótico en µg/mL
        mic_real: MIC real de la bacteria para ese antibiótico
        hill_coefficient: Coeficiente de Hill (n), típicamente 2-4
                         Valores altos = inhibición más abrupta

    Returns:
        OD máxima inhibida por el antibiótico

    Ejemplo:
        >>> # Bacteria con MIC=8, concentración del well=16
        >>> od_inhibido = calculate_od_max_with_antibiotic(2.0, 16.0, 8.0)
        >>> print(f"OD máxima inhibida: {od_inhibido:.3f}")
        OD máxima inhibida: 0.118
    """
    if mic_real <= 0:
        raise ValueError("MIC debe ser mayor que 0")

    if concentration <= 0:
        return base_od_max

    ratio = concentration / mic_real
    survival_fraction = 1.0 / (1.0 + math.pow(ratio, hill_coefficient))
    od_max_inhibited = base_od_max * survival_fraction

    return od_max_inhibited


def add_measurement_noise(od_value: float, noise_level: float = 0.05) -> float:
    """
    Agrega ruido gaussiano a una lectura de OD para simular variabilidad instrumental.

    DEPRECATED: Usar ExperimentalNoiseModel para ruido más realista.
    Mantenido por compatibilidad con código legacy.

    Los lectores de microplacas tienen variabilidad inherente debido a:
    - Precisión del fotómetro
    - Variabilidad en el volumen del pocillo
    - Temperatura no uniforme
    - Burbujas de aire

    Args:
        od_value: Valor de OD original
        noise_level: Nivel de ruido relativo (desviación estándar como fracción del valor)
                    Típicamente 0.02-0.10 (2-10%)

    Returns:
        Valor de OD con ruido agregado

    Ejemplo:
        >>> od_original = 1.5
        >>> od_medido = add_measurement_noise(od_original, noise_level=0.05)
        >>> print(f"OD original: {od_original}, OD medido: {od_medido:.3f}")
        OD original: 1.5, OD medido: 1.523
    """
    if od_value < 0:
        od_value = 0

    noise = random.gauss(0, noise_level * od_value)
    od_with_noise = od_value + noise

    od_with_noise = max(0.0, od_with_noise)

    return od_with_noise


class ExperimentalNoiseModel:
    """
    Modelo multicapa de ruido experimental realista para curvas de crecimiento.

    Simula las siguientes fuentes de variabilidad observadas en laboratorio:

    1. **Ruido Instrumental**: Variabilidad del lector de microplacas (2-5%)
    2. **Offset de Medio**: Absorción basal variable del medio de cultivo
    3. **Variabilidad de Volumen**: Errores de pipeteo (±5-10%)
    4. **Wells Fallidos**: Pocillos que no crecen (1-2% probabilidad)
    5. **Spikes Aleatorios**: Burbujas o partículas transitorias
    6. **Lags Extendidos**: Bacterias con adaptación lenta (5% probabilidad)

    Basado en:
    - CLSI M07-A11 (variabilidad instrumental aceptable: <5%)
    - Feedback de especialista en microbiología clínica
    - Literatura: J Microbiol Methods (2019)

    Autor: Sistema AST Simulator
    Fecha: 17 de noviembre de 2025
    """

    def __init__(
        self,
        instrumental_noise: float = 0.03,
        medium_offset_range: Tuple[float, float] = (-0.02, 0.02),
        volume_variability: float = 0.08,
        well_failure_prob: float = 0.015,
        spike_probability: float = 0.02,
        extended_lag_prob: float = 0.05,
        seed: int = None,
    ):
        """
        Inicializa el modelo de ruido experimental.

        Args:
            instrumental_noise: Desviación estándar del ruido del fotómetro (fracción)
            medium_offset_range: Rango de offset constante por absorción del medio
            volume_variability: Variabilidad en OD inicial por errores de pipeteo
            well_failure_prob: Probabilidad de que un well no crezca (0.0-1.0)
            spike_probability: Probabilidad de spike en cada medición
            extended_lag_prob: Probabilidad de lag phase extendido
            seed: Semilla para reproducibilidad (opcional)
        """
        self.instrumental_noise = instrumental_noise
        self.medium_offset_range = medium_offset_range
        self.volume_variability = volume_variability
        self.well_failure_prob = well_failure_prob
        self.spike_probability = spike_probability
        self.extended_lag_prob = extended_lag_prob

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Cada well tiene un offset único de medio (constante durante experimento)
        self.well_medium_offset = random.uniform(*medium_offset_range)

        # Determinar si este well falla completamente
        self.well_failed = random.random() < well_failure_prob

        # Determinar si tiene lag extendido
        self.has_extended_lag = random.random() < extended_lag_prob

    def apply_noise_to_od(self, od_value: float, time_index: int = 0) -> float:
        """
        Aplica ruido experimental multicapa a una lectura de OD.

        Args:
            od_value: Valor de OD sin ruido
            time_index: Índice temporal (para spikes dependientes del tiempo)

        Returns:
            Valor de OD con ruido experimental aplicado
        """
        # Si el well falló, retornar OD mínima
        if self.well_failed:
            return max(0.01, random.gauss(0.05, 0.02))

        # 1. Ruido instrumental (gaussiano proporcional al valor)
        instrumental = np.random.normal(0, self.instrumental_noise * max(od_value, 0.1))

        # 2. Offset constante del medio
        medium_offset = self.well_medium_offset

        # 3. Spike aleatorio (burbuja/partícula transitoria)
        spike = 0.0
        if random.random() < self.spike_probability:
            spike = random.uniform(0.05, 0.15)

        # Combinar todos los efectos
        od_noisy = od_value + instrumental + medium_offset + spike

        # Asegurar valores físicamente posibles
        od_noisy = max(0.0, od_noisy)

        # Saturación del lector (OD > 3.0 se satura)
        if od_noisy > 3.0:
            od_noisy = 3.0 + random.uniform(-0.1, 0.1)

        return od_noisy

    def perturb_initial_od(self, od_initial: float) -> float:
        """
        Perturba la OD inicial por variabilidad de pipeteo.

        Args:
            od_initial: OD inicial nominal

        Returns:
            OD inicial con variabilidad de volumen
        """
        if self.well_failed:
            return od_initial

        # Variabilidad de volumen (±8% típicamente)
        perturbation = np.random.normal(1.0, self.volume_variability)
        return od_initial * perturbation

    def get_lag_multiplier(self) -> float:
        """
        Obtiene multiplicador de lag phase si el well tiene lag extendido.

        Returns:
            Multiplicador para t_mid (1.0 = normal, >1.0 = lag extendido)
        """
        if self.has_extended_lag:
            # Lag extendido: +30% a +80% de retraso
            return random.uniform(1.3, 1.8)
        return 1.0

    def is_well_failed(self) -> bool:
        """Retorna True si este well falló completamente."""
        return self.well_failed


def add_biological_variability(
    k: float, t_mid: float, od_max: float
) -> Tuple[float, float, float]:
    """
    Agrega variabilidad biológica natural a los parámetros de crecimiento.

    En la vida real, incluso bacterias clonales muestran heterogeneidad en:
    - Tasa de crecimiento (k)
    - Momento de entrada a fase exponencial (t_mid)
    - Densidad máxima alcanzada (od_max)

    Args:
        k: Tasa de crecimiento nominal (min⁻¹)
        t_mid: Tiempo de punto medio nominal (minutos)
        od_max: OD máxima nominal

    Returns:
        Tupla (k_varied, t_mid_varied, od_max_varied) con variabilidad biológica

    Varianzas aplicadas:
        - k: ±15% (tasa de crecimiento)
        - t_mid: ±10% (duración de lag phase)
        - od_max: ±8% (capacidad de carga del medio)
    """
    k_varied = k * random.gauss(1.0, 0.15)  # ±15%
    t_mid_varied = t_mid * random.gauss(1.0, 0.10)  # ±10%
    od_max_varied = od_max * random.gauss(1.0, 0.08)  # ±8%

    # Asegurar valores positivos
    k_varied = max(0.001, k_varied)
    t_mid_varied = max(60, t_mid_varied)
    od_max_varied = max(0.1, od_max_varied)

    return k_varied, t_mid_varied, od_max_varied


def classify_turbidity(od_value: float) -> Tuple[str, str]:
    """
    Clasifica turbidez visual basada en OD600.

    Proporciona tanto una categoría cualitativa como una descripción
    para interpretación visual del crecimiento bacteriano.

    Args:
        od_value: Valor de densidad óptica (OD600)

    Returns:
        Tupla (categoría, descripción):
        - categoría: 'claro', 'ligero', 'moderado', 'turbio', 'muy_turbio'
        - descripción: Texto descriptivo del nivel de turbidez

    Rangos de OD:
        - OD < 0.1: Claro (sin crecimiento visible)
        - 0.1 ≤ OD < 0.3: Ligera turbidez (inicio de crecimiento)
        - 0.3 ≤ OD < 1.0: Moderada turbidez (crecimiento activo)
        - 1.0 ≤ OD < 2.0: Turbio (crecimiento abundante)
        - OD ≥ 2.0: Muy turbio (crecimiento máximo/saturación)

    Ejemplo:
        >>> categoria, desc = classify_turbidity(0.25)
        >>> print(f"{categoria}: {desc}")
        ligero: Crecimiento inicial visible
    """
    if od_value < 0.1:
        return "claro", "Sin crecimiento visible"
    elif od_value < 0.3:
        return "ligero", "Crecimiento inicial visible"
    elif od_value < 1.0:
        return "moderado", "Crecimiento activo"
    elif od_value < 2.0:
        return "turbio", "Crecimiento abundante"
    else:
        return "muy_turbio", "Crecimiento máximo / saturación"


def calculate_growth_parameters(
    mic_value: float,
    concentration: float,
    base_od_max: float = 2.0,
    base_k: float = 0.02,
    base_t_mid: float = 480.0,
) -> Tuple[float, float, float]:
    """
    Calcula parámetros de curva logística ajustados para un pocillo específico.

    Adapta los parámetros de crecimiento según la relación entre
    concentración de antibiótico y MIC de la bacteria.

    Args:
        mic_value: MIC de la bacteria (µg/mL)
        concentration: Concentración en el pocillo (µg/mL)
        base_od_max: OD máxima base sin antibiótico
        base_k: Tasa de crecimiento base (min⁻¹)
        base_t_mid: Tiempo medio base (minutos)

    Returns:
        Tupla (od_max, k, t_mid) ajustados para ese pocillo

    Lógica:
        - Si concentración < MIC: crecimiento normal
        - Si concentración ≈ MIC: crecimiento reducido y retardado
        - Si concentración >> MIC: crecimiento mínimo y muy retardado
    """
    if concentration < mic_value:
        od_max = base_od_max
        k = base_k
        t_mid = base_t_mid
    elif concentration < mic_value * 2:
        od_max = calculate_od_max_with_antibiotic(base_od_max, concentration, mic_value)
        k = base_k * 0.7
        t_mid = base_t_mid * 1.3
    else:
        od_max = calculate_od_max_with_antibiotic(base_od_max, concentration, mic_value)
        k = base_k * 0.5
        t_mid = base_t_mid * 1.5

    return od_max, k, t_mid


def simulate_well_growth_curve(
    mic_value: float,
    concentration: float,
    time_points: list,
    od_initial: float = 0.05,
    add_noise: bool = True,
    noise_level: float = 0.05,
    use_realistic_noise: bool = True,
    biological_variability: bool = True,
) -> list:
    """
    Simula curva de crecimiento completa para un pocillo.

    Función de alto nivel que combina todos los modelos para
    generar una serie temporal realista de lecturas de OD.

    **NUEVO v2.0**: Soporta ruido experimental multicapa realista.

    Args:
        mic_value: MIC de la bacteria (µg/mL)
        concentration: Concentración en el pocillo (µg/mL)
        time_points: Lista de tiempos en minutos (ej: [0, 60, 120, ...])
        od_initial: OD inicial del inóculo
        add_noise: Si True, agrega ruido experimental
        noise_level: Nivel de ruido si use_realistic_noise=False (legacy)
        use_realistic_noise: Si True, usa ExperimentalNoiseModel (RECOMENDADO)
        biological_variability: Si True, agrega variabilidad biológica a parámetros

    Returns:
        Lista de valores OD correspondientes a cada time_point

    Ejemplo:
        >>> times = [0, 60, 120, 180, 240, 300, 360, 420, 480]
        >>> # Modo realista (RECOMENDADO)
        >>> ods = simulate_well_growth_curve(
        ...     mic_value=8,
        ...     concentration=4,
        ...     time_points=times,
        ...     use_realistic_noise=True
        ... )
        >>> for t, od in zip(times, ods):
        ...     print(f"t={t:3d} min: OD={od:.3f}")
    """
    # Obtener parámetros base de crecimiento
    od_max, k, t_mid = calculate_growth_parameters(mic_value, concentration)

    # NUEVO: Agregar variabilidad biológica a parámetros
    if biological_variability:
        k, t_mid, od_max = add_biological_variability(k, t_mid, od_max)

    # NUEVO: Inicializar modelo de ruido experimental realista
    noise_model = None
    if add_noise and use_realistic_noise:
        noise_model = ExperimentalNoiseModel()

        # Aplicar variabilidad de volumen a OD inicial
        od_initial = noise_model.perturb_initial_od(od_initial)

        # Aplicar multiplicador de lag si corresponde
        lag_mult = noise_model.get_lag_multiplier()
        t_mid = t_mid * lag_mult

        # Si el well falló, retornar curva plana
        if noise_model.is_well_failed():
            return [max(0.01, random.gauss(0.05, 0.02)) for _ in time_points]

    # Generar curva de crecimiento
    od_values = []
    for idx, t in enumerate(time_points):
        od = logistic_growth(t, od_max, k, t_mid, od_initial)

        # Aplicar ruido experimental
        if add_noise:
            if use_realistic_noise and noise_model:
                # NUEVO: Ruido experimental multicapa
                od = noise_model.apply_noise_to_od(od, time_index=idx)
            else:
                # LEGACY: Ruido simple
                od = add_measurement_noise(od, noise_level)

        od_values.append(od)

    return od_values
