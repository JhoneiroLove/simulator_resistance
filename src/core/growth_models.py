"""
Módulo Growth Models - Modelos Matemáticos de Crecimiento Bacteriano

Este módulo implementa funciones matemáticas para simular el crecimiento
bacteriano en presencia de antibióticos, incluyendo:
- Curva logística de Verhulst
- Inhibición por antibióticos (ecuación de Hill)
- Ruido de medición realista
- Clasificación de turbidez

Autor: Sistema AST Simulator
Fecha: 11 de noviembre de 2025
"""

import math
import random
from typing import Tuple


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
) -> list:
    """
    Simula curva de crecimiento completa para un pocillo.

    Función de alto nivel que combina todos los modelos para
    generar una serie temporal realista de lecturas de OD.

    Args:
        mic_value: MIC de la bacteria (µg/mL)
        concentration: Concentración en el pocillo (µg/mL)
        time_points: Lista de tiempos en minutos (ej: [0, 60, 120, ...])
        od_initial: OD inicial del inóculo
        add_noise: Si True, agrega ruido de medición
        noise_level: Nivel de ruido relativo (si add_noise=True)

    Returns:
        Lista de valores OD correspondientes a cada time_point

    Ejemplo:
        >>> times = [0, 60, 120, 180, 240, 300, 360, 420, 480]
        >>> ods = simulate_well_growth_curve(mic_value=8, concentration=4, time_points=times)
        >>> for t, od in zip(times, ods):
        ...     print(f"t={t:3d} min: OD={od:.3f}")
    """
    od_max, k, t_mid = calculate_growth_parameters(mic_value, concentration)

    od_values = []
    for t in time_points:
        od = logistic_growth(t, od_max, k, t_mid, od_initial)

        if add_noise:
            od = add_measurement_noise(od, noise_level)

        od_values.append(od)

    return od_values
