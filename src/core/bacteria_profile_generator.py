"""
Generador de perfiles bacterianos para Pseudomonas aeruginosa.

Este módulo genera perfiles bacterianos in-silico basados en escenarios clínicos.
Reemplaza la identificación física MALDI-TOF del flujo de trabajo real de MicroScan.

Funcionalidades:
- Generación de bacteria wild-type (sensible, sin exposición previa)
- Generación de bacteria con resistencia adquirida (basada en historial de antibióticos)
- Cálculo de MICs usando la regla multiplicativa: MIC_final = MIC_base × ∏(multiplicadores)
- Integración con tabla gene_class_multipliers para mutaciones científicas

Autor: Sistema SRB
Fecha: 11 de noviembre de 2025
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import random

ORGANISM_NAME = "Pseudomonas aeruginosa"


@dataclass
class BacteriaProfile:
    """
    Estructura de datos para un perfil bacteriano completo.

    Mapea directamente a la tabla SQL bacteria_profiles.

    Attributes:
        organismo: Nombre de la especie bacteriana
        genotipo: Diccionario gen → estado (wild-type, mutado, loss, etc.)
        mics_calculated: MICs finales después de aplicar multiplicadores
        escenario: Contexto clínico (comunitario/hospitalizado)
        origen_muestra: Tipo de muestra clínica (hemocultivo, esputo, etc.)
        antibioticos_previos: Lista de antibióticos a los que fue expuesta
        mutaciones_aplicadas: Lista de mutaciones con metadata científica
    """

    organismo: str
    genotipo: Dict[str, str]
    mics_calculated: Dict[str, float]
    escenario: str
    origen_muestra: Optional[str] = None
    antibioticos_previos: Optional[List[str]] = None
    mutaciones_aplicadas: Optional[List[Dict[str, Any]]] = None


def get_wild_type_genotype() -> Dict[str, str]:
    """
    Define el genotipo de P. aeruginosa wild-type sensible.

    Returns:
        Diccionario con 11 genes en estado basal (funcional, no mutado).
    """
    return {
        "gyrA": "wild-type",
        "parC": "wild-type",
        "oprD": "functional",
        "mexR": "functional",
        "ampC_promoter": "basal",
        "ampD": "functional",
        "ftsI": "wild-type",
        "mexZ": "functional",
        "nalC": "wild-type",
        "blaVIM_or_blaIMP": "absent",
        "pmrB": "wild-type",
    }


def get_baseline_mics() -> Dict[str, float]:
    """
    Obtiene MICs basales de P. aeruginosa wild-type desde la base de datos.

    Valores basados en distribución wild-type de literatura científica (EUCAST ECOFFs, CLSI).
    Todos los valores tienen referencias PMID verificadas en la tabla baseline_mics.

    Returns:
        Diccionario antibiótico → MIC basal en µg/mL (wild-type sensible).

    Raises:
        RuntimeError: Si no se pueden cargar los datos de la BD
    """
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

        baseline_dict = {
            record.antibiotico: record.mic_wt for record in baseline_records
        }

        return baseline_dict

    except Exception as e:
        # Fallback temporal para compatibilidad (se eliminará en futuro)
        import warnings

        warnings.warn(
            f"Could not load baseline MICs from database: {e}. "
            "Using hardcoded fallback values. Please run migration 019.",
            UserWarning,
        )

        # Valores fallback (mantenidos por compatibilidad temporal)
        return {
            "Meropenem": 0.5,
            "Imipenem": 1.0,
            "Doripenem": 0.5,
            "Ciprofloxacino": 0.125,
            "Levofloxacino": 0.5,
            "Amikacina": 2.0,
            "Tobramicina": 0.5,
            "Gentamicina": 1.0,
            "Piperacilina/Tazobactam": 8.0,
            "Ceftazidima": 1.0,
            "Cefepime": 2.0,
            "Colistina": 1.0,
        }


def generate_wild_type() -> BacteriaProfile:
    """
    Genera perfil de bacteria comunitaria sensible (sin exposición a antibióticos).

    Escenario típico: Paciente ambulatorio sin tratamientos previos.

    Returns:
        BacteriaProfile con genotipo wild-type y MICs basales.
    """
    return BacteriaProfile(
        organismo=ORGANISM_NAME,
        genotipo=get_wild_type_genotype(),
        mics_calculated=get_baseline_mics(),
        escenario="comunitario",
        origen_muestra=None,
        antibioticos_previos=None,
        mutaciones_aplicadas=None,
    )


def generate_from_history(
    antibioticos_previos: List[str], probabilidad_mutacion: float = 0.7
) -> BacteriaProfile:
    """
    Genera bacteria con resistencias adquiridas basadas en exposición previa.

    Algoritmo:
    1. Parte de genotipo wild-type
    2. Selecciona mutaciones relevantes según antibióticos previos
    3. Aplica mutaciones probabilísticamente
    4. Calcula MICs finales usando GenotypePhenotypeCalculator

    Args:
        antibioticos_previos: Lista de antibióticos usados previamente
        probabilidad_mutacion: P(mutación | exposición a antibiótico) [0.0-1.0]

    Returns:
        BacteriaProfile con genotipo mutado y MICs calculados.

    Example:
        >>> profile = generate_from_history(['Ciprofloxacino', 'Meropenem'])
        >>> profile.genotipo['gyrA']
        'T83I'  # Mutación en gyrA por exposición a Cipro
        >>> profile.mics_calculated['Ciprofloxacino']
        1.0  # MIC_base (0.125) × gyrA (8.0) = 1.0 µg/mL
    """
    genotipo = get_wild_type_genotype().copy()
    mutaciones_aplicadas = []

    # Genes candidatos a mutar según antibióticos previos
    genes_candidatos = {
        "Ciprofloxacino": ["gyrA_T83I", "parC_S87L", "mexR_frameshift", "nalC_Q83K"],
        "Levofloxacino": ["gyrA_T83I", "parC_S87L", "mexR_frameshift", "nalC_Q83K"],
        "Meropenem": ["oprD_loss", "blaVIM_or_blaIMP", "ftsI_PBP3_insertion_YRIN"],
        "Imipenem": ["oprD_loss", "blaVIM_or_blaIMP", "ftsI_PBP3_insertion_YRIN"],
        "Doripenem": ["oprD_loss", "blaVIM_or_blaIMP", "ftsI_PBP3_insertion_YRIN"],
        "Ceftazidima": [
            "ampC_promoter_-32C_T",
            "ampD_loss",
            "blaVIM_or_blaIMP",
            "mexR_frameshift",
            "ftsI_PBP3_insertion_YRIN",
        ],
        "Cefepime": [
            "ampC_promoter_-32C_T",
            "ampD_loss",
            "blaVIM_or_blaIMP",
            "mexR_frameshift",
            "ftsI_PBP3_insertion_YRIN",
        ],
        "Ceftazidima/Avibactam": [
            "ampD_loss",
            "blaVIM_or_blaIMP",
            "ftsI_PBP3_insertion_YRIN",
        ],
        "Ceftolozano/Tazobactam": [
            "ampD_loss",
            "blaVIM_or_blaIMP",
            "ftsI_PBP3_insertion_YRIN",
        ],
        "Aztreonam": ["ampC_promoter_-32C_T", "ampD_loss", "ftsI_PBP3_insertion_YRIN"],
        "Piperacilina/Tazobactam": [
            "ampC_promoter_-32C_T",
            "ampD_loss",
            "mexR_frameshift",
            "ftsI_PBP3_insertion_YRIN",
        ],
        "Amikacina": ["mexZ_loss"],
        "Tobramicina": ["mexZ_loss"],
        "Colistina": ["pmrB_mut"],
        "Cefiderocol": ["blaVIM_or_blaIMP"],
    }

    # Aplicar mutaciones probabilísticamente
    genes_mutados = []
    for antibiotico in antibioticos_previos:
        if antibiotico not in genes_candidatos:
            continue

        for gen_mutado in genes_candidatos[antibiotico]:
            # Evitar duplicados
            if gen_mutado in genes_mutados:
                continue

            # Aplicar mutación con probabilidad
            if random.random() < probabilidad_mutacion:
                # Actualizar genotipo
                gen_base = gen_mutado.split("_")[0]
                mutacion_tipo = "_".join(gen_mutado.split("_")[1:])
                genotipo[gen_base] = mutacion_tipo if mutacion_tipo else "mutated"

                genes_mutados.append(gen_mutado)

                # Registrar mutación aplicada
                mutaciones_aplicadas.append(
                    {
                        "gen": gen_mutado,
                        "trigger": antibiotico,
                        "tipo": mutacion_tipo or "loss",
                    }
                )

    # Calcular MICs finales usando el nuevo sistema genotipo→fenotipo
    try:
        from src.core.genotype_phenotype_calculator import calculate_mics_from_genotype
    except ImportError:
        # Fallback para ejecución directa del script
        import sys
        import os

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
        from src.core.genotype_phenotype_calculator import calculate_mics_from_genotype

    mics_calculated = calculate_mics_from_genotype(genes_mutados)

    return BacteriaProfile(
        organismo=ORGANISM_NAME,
        genotipo=genotipo,
        mics_calculated=mics_calculated,
        escenario="hospitalizado",
        origen_muestra=None,
        antibioticos_previos=antibioticos_previos,
        mutaciones_aplicadas=mutaciones_aplicadas,
    )


def format_profile_summary(profile: BacteriaProfile) -> str:
    """
    Genera resumen textual del perfil bacteriano para mostrar en GUI.

    Args:
        profile: Perfil bacteriano generado

    Returns:
        String multilinea con información educativa del perfil.

    Example:
        >>> profile = generate_wild_type()
        >>> print(format_profile_summary(profile))
        Organismo: Pseudomonas aeruginosa
        Escenario: comunitario
        Genotipo: wild-type (sensible)
        ---
        MICs calculados:
          Meropenem: 0.5 ug/mL
          Ciprofloxacino: 0.125 ug/mL
          ...
    """
    lines = [f"Organismo: {profile.organismo}", f"Escenario: {profile.escenario}", ""]

    # Genotipo
    if profile.mutaciones_aplicadas:
        lines.append(f"Mutaciones aplicadas: {len(profile.mutaciones_aplicadas)}")
        for mut in profile.mutaciones_aplicadas:
            lines.append(f"  - {mut['gen']} (trigger: {mut['trigger']})")
    else:
        lines.append("Genotipo: wild-type (sensible)")

    lines.append("")
    lines.append("MICs calculados (seleccion):")

    # Mostrar solo antibióticos clave
    antibioticos_clave = [
        "Meropenem",
        "Ciprofloxacino",
        "Ceftazidima",
        "Amikacina",
        "Colistina",
    ]
    for ab in antibioticos_clave:
        if ab in profile.mics_calculated:
            lines.append(f"  {ab}: {profile.mics_calculated[ab]} ug/mL")

    return "\n".join(lines)
