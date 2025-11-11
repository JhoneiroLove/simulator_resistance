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
    Define los MICs basales de P. aeruginosa sensible (sin mutaciones).

    Valores basados en distribución wild-type de literatura científica.
    Referencias:
    - Livermore DM. 2002. Clinical Microbiology Reviews (PMID: 12364371)
    - EUCAST MIC Distribution (www.eucast.org/mic_distributions)
    - Pang Z et al. 2019. Front Microbiol (PMID: 30838007)

    Estos valores se modifican mediante multiplicadores de la tabla gene_class_multipliers.

    Returns:
        Diccionario antibiótico → MIC basal en µg/mL (wild-type sensible).
    """
    return {
        # Carbapenémicos (PMID: 12364371, EUCAST MIC dist)
        "Meropenem": 0.5,  # Wild-type modal: 0.25-1.0
        "Imipenem": 1.0,  # Wild-type modal: 0.5-2.0
        "Doripenem": 0.5,  # Similar a Meropenem
        # Cefalosporinas (PMID: 30838007)
        "Ceftazidima": 1.0,  # Wild-type modal: 0.5-2.0
        "Cefepime": 2.0,  # Wild-type modal: 1.0-4.0
        "Ceftazidima/Avibactam": 2.0,  # Con inhibidor
        "Ceftolozano/Tazobactam": 0.5,  # Resistente a AmpC
        # Monobactams
        "Aztreonam": 4.0,  # Wild-type modal: 2.0-8.0
        # Penicilinas + inhibidor
        "Piperacilina/Tazobactam": 4.0,  # Wild-type modal: 2.0-8.0
        # Aminoglucósidos (PMID: 31296920)
        "Amikacina": 2.0,  # Wild-type modal: 1.0-4.0
        "Tobramicina": 0.5,  # Wild-type modal: 0.25-1.0
        # Fluoroquinolonas (PMID: 30756138)
        "Ciprofloxacino": 0.125,  # Wild-type modal: 0.06-0.25
        "Levofloxacino": 0.5,  # Wild-type modal: 0.25-1.0
        # Polimixinas (EUCAST)
        "Colistina": 1.0,  # Wild-type modal: 0.5-2.0
        # Sideróforo
        "Cefiderocol": 0.25,  # Nuevo, modal: 0.125-0.5
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


def calculate_mic_with_multipliers(base_mic: float, multipliers: List[float]) -> float:
    """
    Calcula MIC final aplicando la regla multiplicativa.

    Formula: MIC_final = MIC_base × ∏(multiplicadores)

    Args:
        base_mic: Valor MIC basal (bacteria wild-type)
        multipliers: Lista de multiplicadores de genes mutados

    Returns:
        MIC calculado, redondeado a 2 decimales.

    Example:
        >>> calculate_mic_with_multipliers(0.5, [8.0, 16.0])
        64.0  # Meropenem con oprD_loss (×8) + blaVIM (×16)
    """
    result = base_mic
    for mult in multipliers:
        result *= mult
    return round(result, 2)


def generate_from_history(
    antibioticos_previos: List[str], probabilidad_mutacion: float = 0.7
) -> BacteriaProfile:
    """
    Genera bacteria con resistencias adquiridas basadas en exposición previa.

    Algoritmo:
    1. Parte de genotipo wild-type
    2. Consulta tabla gene_class_multipliers (via get_multipliers_from_db)
    3. Selecciona mutaciones relevantes según antibióticos previos
    4. Aplica mutaciones probabilísticamente
    5. Calcula MICs finales usando regla multiplicativa

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
    base_mics = get_baseline_mics()
    mics_calculated = base_mics.copy()
    mutaciones_aplicadas = []

    # Obtener multiplicadores desde la base de datos
    from src.core.bacteria_profile_generator import get_multipliers_from_db

    antibiotic_multipliers = get_multipliers_from_db()

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
    genes_mutados = set()
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

                genes_mutados.add(gen_mutado)

                # Registrar mutación aplicada
                mutaciones_aplicadas.append(
                    {
                        "gen": gen_mutado,
                        "trigger": antibiotico,
                        "tipo": mutacion_tipo or "loss",
                    }
                )

    # Calcular MICs finales usando multiplicadores
    for antibiotico, base_mic in base_mics.items():
        if antibiotico not in antibiotic_multipliers:
            continue

        # Obtener multiplicadores de genes mutados
        multiplicadores = []
        for gen_mutado in genes_mutados:
            if gen_mutado in antibiotic_multipliers[antibiotico]:
                multiplicadores.append(antibiotic_multipliers[antibiotico][gen_mutado])

        # Aplicar regla multiplicativa
        if multiplicadores:
            mics_calculated[antibiotico] = calculate_mic_with_multipliers(
                base_mic, multiplicadores
            )

    return BacteriaProfile(
        organismo=ORGANISM_NAME,
        genotipo=genotipo,
        mics_calculated=mics_calculated,
        escenario="hospitalizado",
        origen_muestra=None,
        antibioticos_previos=antibioticos_previos,
        mutaciones_aplicadas=mutaciones_aplicadas,
    )


def get_multipliers_from_db() -> Dict[str, Dict[str, float]]:
    """
    Consulta la base de datos para obtener multiplicadores MIC.

    Estructura:
        {
            'Meropenem': {
                'oprD_loss': 8.0,
                'blaVIM_or_blaIMP': 16.0,
                'ftsI_PBP3_insertion_YRIN': 2.0
            },
            'Ciprofloxacino': {
                'gyrA_T83I': 8.0,
                'parC_S87L': 4.0,
                ...
            },
            ...
        }

    Returns:
        Diccionario anidado: antibiotico → gen → multiplicador
    """
    from src.data.database import get_session
    from sqlalchemy import text

    session = get_session()

    query = text("""
        SELECT 
            ac.antibiotico,
            gcm.gen,
            gcm.multiplicador_mic
        FROM gene_class_multipliers gcm
        JOIN antibiotic_classes ac ON ac.clase = gcm.clase_antibiotico
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
    return result


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


if __name__ == "__main__":
    # Prueba básica del módulo
    print("Generando bacteria wild-type...")
    wt_profile = generate_wild_type()
    print(format_profile_summary(wt_profile))

    print("\n" + "=" * 60 + "\n")

    print("Generando bacteria con historial de Cipro + Meropenem...")
    resistant_profile = generate_from_history(["Ciprofloxacino", "Meropenem"])
    print(format_profile_summary(resistant_profile))
