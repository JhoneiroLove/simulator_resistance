"""
Modulo Well Issues Model - Simulacion de Problemas en Pozos AST

Este modulo implementa la simulacion de pozos ambiguos y problematicos
que ocurren en paneles AST reales, incluyendo:
- Pozos con crecimiento debil o inconsistente
- Pozos contaminados
- Pozos con borde difuso
- Pozos con precipitado
- Pozos que no se pueden leer

Basado en feedback de especialista en microbiologia clinica.

Autor: Sistema AST Simulator
Fecha: 17 de noviembre de 2025
Version: 1.0 - Pozos Ambiguos
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class WellIssueType(Enum):
    """Tipos de problemas que pueden ocurrir en pozos AST."""

    NONE = "normal"
    WEAK_GROWTH = "crecimiento_debil"
    CONTAMINATED = "contaminado"
    DIFFUSE_EDGE = "borde_difuso"
    PRECIPITATE = "precipitado"
    UNREADABLE = "no_legible"
    INCONSISTENT_OD = "od_inconsistente"


@dataclass
class WellIssue:
    """Representa un problema especifico en un pozo."""

    well_position: str
    issue_type: WellIssueType
    severity: float  # 0.0 = minimo, 1.0 = maximo
    description: str
    affects_reading: bool  # Si afecta la lectura de OD
    affects_interpretation: bool  # Si afecta interpretacion S/R
    recommended_action: str


class WellIssuesSimulator:
    """
    Simulador de problemas aleatorios en pozos AST.

    Simula condiciones realistas donde 2-4 pozos por panel pueden tener
    problemas que dificultan o invalidan su lectura, similar a lo que
    ocurre con sistemas como MicroScan en laboratorios reales.
    """

    def __init__(
        self,
        issue_probability: float = 0.03,  # 3% de pozos con problemas
        min_issues_per_panel: int = 2,
        max_issues_per_panel: int = 4,
        seed: Optional[int] = None,
    ):
        """
        Inicializa el simulador de problemas de pozos.

        Args:
            issue_probability: Probabilidad base de que un pozo tenga problemas
            min_issues_per_panel: Minimo de pozos problematicos por panel
            max_issues_per_panel: Maximo de pozos problematicos por panel
            seed: Semilla para reproducibilidad
        """
        self.issue_probability = issue_probability
        self.min_issues = min_issues_per_panel
        self.max_issues = max_issues_per_panel

        if seed is not None:
            random.seed(seed)

        # Configuracion de tipos de problemas y sus caracteristicas
        self.issue_configs = {
            WellIssueType.WEAK_GROWTH: {
                "weight": 0.25,
                "severity_range": (0.3, 0.7),
                "affects_reading": True,
                "affects_interpretation": True,
                "description_templates": [
                    "Crecimiento detectado pero muy debil (OD marginal)",
                    "Turbidez apenas perceptible, dificil clasificar",
                    "Crecimiento lento, lectura en zona gris",
                ],
                "action": "Repetir prueba o usar metodo alternativo",
            },
            WellIssueType.CONTAMINATED: {
                "weight": 0.15,
                "severity_range": (0.6, 1.0),
                "affects_reading": True,
                "affects_interpretation": True,
                "description_templates": [
                    "Crecimiento atipico, posible contaminacion",
                    "Morfologia inusual, sospecha de organismo secundario",
                    "Patron de crecimiento no coincide con perfil esperado",
                ],
                "action": "Descartar resultado, repetir con cultivo puro",
            },
            WellIssueType.DIFFUSE_EDGE: {
                "weight": 0.20,
                "severity_range": (0.2, 0.6),
                "affects_reading": True,
                "affects_interpretation": False,
                "description_templates": [
                    "Borde de crecimiento difuso, dificil determinar umbral",
                    "Transicion gradual crece/no-crece",
                    "Lectura ambigua en zona limite",
                ],
                "action": "Revisar manualmente, considerar MIC adyacente",
            },
            WellIssueType.PRECIPITATE: {
                "weight": 0.20,
                "severity_range": (0.3, 0.8),
                "affects_reading": True,
                "affects_interpretation": False,
                "description_templates": [
                    "Precipitado en el fondo, interfiere con lectura optica",
                    "Cristales visibles, OD artificialmente elevada",
                    "Material particulado, lectura poco confiable",
                ],
                "action": "Revisar visualmente, no confiar en OD automatica",
            },
            WellIssueType.UNREADABLE: {
                "weight": 0.10,
                "severity_range": (0.9, 1.0),
                "affects_reading": True,
                "affects_interpretation": True,
                "description_templates": [
                    "Pozo no leible, fallo en sistema optico",
                    "Lectura rechazada por QC automatico",
                    "Error de lectura, datos no disponibles",
                ],
                "action": "Excluir del analisis, reportar como no-disponible",
            },
            WellIssueType.INCONSISTENT_OD: {
                "weight": 0.10,
                "severity_range": (0.4, 0.7),
                "affects_reading": True,
                "affects_interpretation": False,
                "description_templates": [
                    "OD fluctua entre lecturas, patron inconsistente",
                    "Variacion temporal atipica",
                    "Curva de crecimiento errática",
                ],
                "action": "Revisar curva completa, considerar repetir",
            },
        }

    def assign_issues_to_panel(
        self, well_positions: List[str], exclude_controls: bool = True
    ) -> Dict[str, WellIssue]:
        """
        Asigna problemas aleatorios a pozos de un panel.

        Args:
            well_positions: Lista de posiciones de pozos (ej: ["A1", "A2", ...])
            exclude_controls: Si True, no asigna problemas a controles

        Returns:
            Diccionario {posicion: WellIssue} con pozos problematicos
        """
        # Filtrar controles si es necesario
        if exclude_controls:
            # Tipicamente controles estan en ultimas posiciones
            # Asumimos H11, H12 como controles (ajustar segun layout real)
            control_positions = ["H11", "H12"]
            available_wells = [p for p in well_positions if p not in control_positions]
        else:
            available_wells = well_positions

        # Determinar cantidad de pozos con problemas
        num_issues = random.randint(self.min_issues, self.max_issues)
        num_issues = min(num_issues, len(available_wells))

        # Seleccionar pozos al azar
        affected_wells = random.sample(available_wells, num_issues)

        # Asignar tipo de problema a cada pozo
        issues = {}
        for well_pos in affected_wells:
            issue = self._generate_random_issue(well_pos)
            issues[well_pos] = issue

        return issues

    def _generate_random_issue(self, well_position: str) -> WellIssue:
        """
        Genera un problema aleatorio para un pozo especifico.

        Args:
            well_position: Posicion del pozo (ej: "A1")

        Returns:
            WellIssue con el problema generado
        """
        # Seleccionar tipo de problema segun pesos
        issue_types = list(self.issue_configs.keys())
        weights = [self.issue_configs[t]["weight"] for t in issue_types]
        issue_type = random.choices(issue_types, weights=weights, k=1)[0]

        # Obtener configuracion del tipo de problema
        config = self.issue_configs[issue_type]

        # Generar severidad aleatoria dentro del rango
        severity = random.uniform(*config["severity_range"])

        # Seleccionar descripcion aleatoria
        description = random.choice(config["description_templates"])

        return WellIssue(
            well_position=well_position,
            issue_type=issue_type,
            severity=severity,
            description=description,
            affects_reading=config["affects_reading"],
            affects_interpretation=config["affects_interpretation"],
            recommended_action=config["action"],
        )

    def apply_issue_to_od(
        self, original_od: float, issue: WellIssue, time_point: int
    ) -> Tuple[float, bool]:
        """
        Aplica el efecto de un problema sobre la lectura de OD.

        Args:
            original_od: OD original sin problema
            issue: Problema a aplicar
            time_point: Tiempo en minutos (para problemas temporales)

        Returns:
            Tupla (od_modificada, lectura_valida)
        """
        if not issue.affects_reading:
            return original_od, True

        # Aplicar modificacion segun tipo de problema
        if issue.issue_type == WellIssueType.WEAK_GROWTH:
            # Reducir OD segun severidad
            reduction_factor = 0.5 - (issue.severity * 0.3)
            modified_od = original_od * reduction_factor
            valid = True

        elif issue.issue_type == WellIssueType.CONTAMINATED:
            # Aumentar OD erraticamente
            contamination_boost = 1.0 + (issue.severity * 0.8)
            modified_od = original_od * contamination_boost
            # Agregar ruido alto
            noise = random.gauss(0, 0.15 * modified_od)
            modified_od += noise
            valid = False  # No confiable

        elif issue.issue_type == WellIssueType.DIFFUSE_EDGE:
            # Agregar ruido en zona de transicion
            if 0.2 < original_od < 0.5:
                noise = random.gauss(0, 0.1 * issue.severity)
                modified_od = original_od + noise
            else:
                modified_od = original_od
            valid = True

        elif issue.issue_type == WellIssueType.PRECIPITATE:
            # Incremento artificial de OD por material particulado
            precipitate_od = random.uniform(0.05, 0.15) * issue.severity
            modified_od = original_od + precipitate_od
            valid = False  # Lectura no representa crecimiento real

        elif issue.issue_type == WellIssueType.UNREADABLE:
            # Devolver NaN o valor invalido
            modified_od = float("nan")
            valid = False

        elif issue.issue_type == WellIssueType.INCONSISTENT_OD:
            # Fluctuacion aleatoria en cada lectura
            fluctuation = random.gauss(0, 0.2 * issue.severity)
            modified_od = original_od * (1.0 + fluctuation)
            valid = True  # Pero baja confianza

        else:
            modified_od = original_od
            valid = True

        # Clampear a rango fisicamente posible (0.0 - 4.0)
        if not math.isnan(modified_od):
            modified_od = max(0.0, min(4.0, modified_od))

        return modified_od, valid

    def generate_issue_report(self, issues: Dict[str, WellIssue]) -> str:
        """
        Genera reporte de texto con los problemas encontrados.

        Args:
            issues: Diccionario de pozos con problemas

        Returns:
            Texto formateado con el reporte
        """
        if not issues:
            return "Panel sin problemas detectados - Todas las lecturas validas"

        report_lines = [
            "ALERTA DE CONTROL DE CALIDAD",
            "=" * 70,
            f"Pozos problematicos detectados: {len(issues)}",
            "",
        ]

        for well_pos, issue in sorted(issues.items()):
            report_lines.append(f"Pozo {well_pos}:")
            report_lines.append(f"  Tipo: {issue.issue_type.value}")
            report_lines.append(f"  Severidad: {issue.severity:.1%}")
            report_lines.append(f"  Descripcion: {issue.description}")
            report_lines.append(f"  Accion recomendada: {issue.recommended_action}")
            report_lines.append("")

        return "\n".join(report_lines)


import math
