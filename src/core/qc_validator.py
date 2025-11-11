"""
Módulo QC Validator - Validación de Controles de Calidad AST

Este módulo implementa validaciones de calidad para paneles AST,
incluyendo controles positivos/negativos y coherencia de resultados.

Funcionalidades principales:
- Validación de control positivo (OD > 1.0)
- Validación de control negativo (OD < 0.1)
- Validación de coherencia entre antibióticos relacionados
- Generación de reportes QC detallados

Estándares: CLSI M07 y EUCAST guidelines

Autor: Sistema AST Simulator
Fecha: 11 de noviembre de 2025
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QCResult:
    """
    Resultado de validación de control de calidad.

    Atributos:
        check_type: Tipo de validación ('positive_control', 'negative_control', 'coherence')
        passed: Si la validación pasó o falló
        value: Valor medido (OD para controles, None para coherencia)
        expected_range: Rango esperado (tupla min, max)
        message: Mensaje descriptivo del resultado
        severity: 'PASS', 'WARNING', 'FAIL'
    """

    check_type: str
    passed: bool
    value: Optional[float]
    expected_range: Optional[Tuple[float, float]]
    message: str
    severity: str


@dataclass
class CoherenceIssue:
    """
    Problema de coherencia entre antibióticos relacionados.

    Atributos:
        family: Familia de antibióticos (ej: 'carbapenems')
        antibiotics: Lista de antibióticos involucrados
        issue: Descripción del problema
        expected: Resultado esperado
        actual: Resultado observado
        severity: 'WARNING' o 'FAIL'
    """

    family: str
    antibiotics: List[str]
    issue: str
    expected: str
    actual: str
    severity: str


# Reglas de coherencia entre familias de antibióticos
COHERENCE_RULES = {
    "carbapenems": {
        "antibiotics": ["Imipenem", "Meropenem", "Doripenem", "Ertapenem"],
        "rule": "cross_resistance",
        "description": "Carbapenems comparten mecanismos de resistencia (pérdida OprD, MBLs)",
        "tolerance": 2,  # Diferencia máxima en diluciones (factor 4)
    },
    "fluoroquinolonas": {
        "antibiotics": ["Ciprofloxacino", "Levofloxacino"],
        "rule": "cross_resistance",
        "description": "Fluoroquinolonas comparten alteraciones en girasa/topoisomerasa",
        "tolerance": 2,
    },
    "aminoglucosidos": {
        "antibiotics": ["Gentamicina", "Tobramicina", "Amikacina"],
        "rule": "hierarchical",
        "description": "Amikacina típicamente más activa que Gentamicina/Tobramicina",
        "tolerance": 1,
    },
    "cefalosporinas_antipseudomonas": {
        "antibiotics": ["Ceftazidima", "Cefepime"],
        "rule": "similar",
        "description": "Ceftazidima y Cefepime con actividad similar vs P. aeruginosa",
        "tolerance": 2,
    },
}

# Thresholds para controles QC (basados en CLSI M07)
QC_THRESHOLDS = {
    "positive_control": {
        "min_od": 1.0,  # OD600 > 1.0 indica crecimiento robusto
        "description": "Control positivo debe mostrar crecimiento abundante",
    },
    "negative_control": {
        "max_od": 0.1,  # OD600 < 0.1 indica ausencia de crecimiento
        "description": "Control negativo debe permanecer claro",
    },
    "test_well_max": {
        "max_od": 3.0,  # OD > 3.0 puede indicar contaminación
        "description": "Pocillos de prueba no deben exceder OD 3.0",
    },
}


class QCValidator:
    """
    Validador de controles de calidad para paneles AST.

    Realiza validaciones estándar según CLSI M07:
    - Controles positivos y negativos
    - Coherencia de resultados entre antibióticos relacionados
    - Detección de anomalías (contaminación, errores técnicos)
    """

    def __init__(self):
        """Inicializa el validador QC."""
        self.qc_results: List[QCResult] = []
        self.coherence_issues: List[CoherenceIssue] = []

    def validate_positive_control(
        self, od_value: float, well_position: str = "H11"
    ) -> QCResult:
        """
        Valida control positivo (crecimiento sin antibiótico).

        El control positivo debe mostrar crecimiento robusto (OD > 1.0)
        para confirmar viabilidad del inóculo.

        Args:
            od_value: Densidad óptica final del control positivo
            well_position: Posición del pocillo (típicamente H11)

        Returns:
            QCResult con resultado de validación

        Ejemplo:
            >>> validator = QCValidator()
            >>> result = validator.validate_positive_control(1.8)
            >>> print(f"{result.severity}: {result.message}")
            PASS: Control positivo válido (OD=1.8)
        """
        min_od = QC_THRESHOLDS["positive_control"]["min_od"]
        passed = od_value >= min_od

        if passed:
            severity = "PASS"
            message = (
                f"Control positivo válido (OD={od_value:.2f}, posición {well_position})"
            )
        elif od_value >= min_od * 0.8:  # Dentro del 80%, warning
            severity = "WARNING"
            message = (
                f"Control positivo borderline (OD={od_value:.2f}, esperado ≥{min_od})"
            )
            passed = True  # Aceptable con advertencia
        else:
            severity = "FAIL"
            message = f"Control positivo FALLÓ (OD={od_value:.2f}, esperado ≥{min_od})"

        result = QCResult(
            check_type="positive_control",
            passed=passed,
            value=od_value,
            expected_range=(min_od, None),
            message=message,
            severity=severity,
        )

        self.qc_results.append(result)
        return result

    def validate_negative_control(
        self, od_value: float, well_position: str = "H12"
    ) -> QCResult:
        """
        Valida control negativo (sin bacteria).

        El control negativo debe permanecer claro (OD < 0.1)
        para confirmar ausencia de contaminación del medio.

        Args:
            od_value: Densidad óptica final del control negativo
            well_position: Posición del pocillo (típicamente H12)

        Returns:
            QCResult con resultado de validación

        Ejemplo:
            >>> validator = QCValidator()
            >>> result = validator.validate_negative_control(0.05)
            >>> print(f"{result.severity}: {result.message}")
            PASS: Control negativo válido (OD=0.05)
        """
        max_od = QC_THRESHOLDS["negative_control"]["max_od"]
        passed = od_value <= max_od

        if passed:
            severity = "PASS"
            message = (
                f"Control negativo válido (OD={od_value:.3f}, posición {well_position})"
            )
        elif od_value <= max_od * 1.5:  # Hasta 50% por encima, warning
            severity = "WARNING"
            message = (
                f"Control negativo borderline (OD={od_value:.3f}, esperado ≤{max_od})"
            )
            passed = True  # Aceptable con advertencia
        else:
            severity = "FAIL"
            message = f"Control negativo FALLÓ (OD={od_value:.3f}, esperado ≤{max_od}) - Posible contaminación"

        result = QCResult(
            check_type="negative_control",
            passed=passed,
            value=od_value,
            expected_range=(None, max_od),
            message=message,
            severity=severity,
        )

        self.qc_results.append(result)
        return result

    def validate_coherence(
        self, mic_results: Dict[str, Dict[str, any]]
    ) -> List[CoherenceIssue]:
        """
        Valida coherencia entre antibióticos relacionados.

        Detecta patrones incoherentes como:
        - Resistencia a un carbapenem pero sensibilidad a otro (inesperado)
        - Resistencia a fluoroquinolonas sin resistencia cruzada
        - Amikacina menos activa que Gentamicina (jerárquicamente incorrecto)

        Args:
            mic_results: Dict con resultados MIC
                {
                    'Meropenem': {'mic': 16, 'interpretation': 'R'},
                    'Imipenem': {'mic': 2, 'interpretation': 'S'},
                    ...
                }

        Returns:
            Lista de CoherenceIssue encontrados

        Ejemplo:
            >>> validator = QCValidator()
            >>> results = {
            ...     'Meropenem': {'mic': 16, 'interpretation': 'R'},
            ...     'Imipenem': {'mic': 2, 'interpretation': 'S'}
            ... }
            >>> issues = validator.validate_coherence(results)
            >>> print(f"Problemas: {len(issues)}")
            Problemas: 1
        """
        issues = []

        for family_name, family_data in COHERENCE_RULES.items():
            antibiotics_in_family = family_data["antibiotics"]
            rule_type = family_data["rule"]
            tolerance = family_data["tolerance"]

            # Filtrar antibióticos de esta familia presentes en resultados
            family_results = {
                ab: data
                for ab, data in mic_results.items()
                if ab in antibiotics_in_family
            }

            if len(family_results) < 2:
                continue  # Necesitamos al menos 2 antibióticos para comparar

            # Aplicar regla según tipo
            if rule_type == "cross_resistance":
                issues.extend(
                    self._check_cross_resistance(
                        family_name,
                        family_results,
                        tolerance,
                        family_data["description"],
                    )
                )
            elif rule_type == "hierarchical":
                issues.extend(
                    self._check_hierarchical(
                        family_name, family_results, family_data["description"]
                    )
                )
            elif rule_type == "similar":
                issues.extend(
                    self._check_similar_activity(
                        family_name,
                        family_results,
                        tolerance,
                        family_data["description"],
                    )
                )

        self.coherence_issues.extend(issues)
        return issues

    def _check_cross_resistance(
        self, family: str, results: Dict[str, Dict], tolerance: int, description: str
    ) -> List[CoherenceIssue]:
        """
        Verifica resistencia cruzada en familia de antibióticos.

        Si uno es R, esperamos que los demás también sean R o I (no S).
        """
        issues = []
        interpretations = {ab: data["interpretation"] for ab, data in results.items()}

        # Si hay al menos un R
        resistant_abs = [ab for ab, interp in interpretations.items() if interp == "R"]
        sensitive_abs = [ab for ab, interp in interpretations.items() if interp == "S"]

        if resistant_abs and sensitive_abs:
            issue = CoherenceIssue(
                family=family,
                antibiotics=resistant_abs + sensitive_abs,
                issue=f"Resistencia cruzada inconsistente en {family}",
                expected=f"Si {resistant_abs[0]} es R, esperar I/R en {', '.join(sensitive_abs)}",
                actual=f"{', '.join(resistant_abs)} son R pero {', '.join(sensitive_abs)} son S",
                severity="WARNING",
            )
            issues.append(issue)

        return issues

    def _check_hierarchical(
        self, family: str, results: Dict[str, Dict], description: str
    ) -> List[CoherenceIssue]:
        """
        Verifica jerarquía de actividad (ej: Amikacina > Gentamicina).
        """
        issues = []

        # Para aminoglucósidos: Amikacina debe ser más potente
        if "Amikacina" in results and "Gentamicina" in results:
            amk_mic = results["Amikacina"]["mic"]
            gent_mic = results["Gentamicina"]["mic"]

            # Amikacina debería tener MIC menor o igual
            if amk_mic > gent_mic * 2:  # Si Amikacina es >2x peor
                issue = CoherenceIssue(
                    family=family,
                    antibiotics=["Amikacina", "Gentamicina"],
                    issue="Jerarquía de actividad invertida",
                    expected="Amikacina MIC ≤ Gentamicina MIC",
                    actual=f"Amikacina MIC={amk_mic} > Gentamicina MIC={gent_mic}",
                    severity="WARNING",
                )
                issues.append(issue)

        return issues

    def _check_similar_activity(
        self, family: str, results: Dict[str, Dict], tolerance: int, description: str
    ) -> List[CoherenceIssue]:
        """
        Verifica que antibióticos con actividad similar tengan MICs comparables.
        """
        issues = []

        # Comparar todos los pares
        antibiotics = list(results.keys())
        for i, ab1 in enumerate(antibiotics):
            for ab2 in antibiotics[i + 1 :]:
                mic1 = results[ab1]["mic"]
                mic2 = results[ab2]["mic"]

                # Calcular diferencia en diluciones (log2)
                import math

                if mic1 > 0 and mic2 > 0:
                    dilution_diff = abs(math.log2(mic1 / mic2))

                    if dilution_diff > tolerance:
                        issue = CoherenceIssue(
                            family=family,
                            antibiotics=[ab1, ab2],
                            issue=f"Diferencia de actividad excesiva ({dilution_diff:.1f} diluciones)",
                            expected=f"Diferencia ≤{tolerance} diluciones",
                            actual=f"{ab1} MIC={mic1}, {ab2} MIC={mic2}",
                            severity="WARNING",
                        )
                        issues.append(issue)

        return issues

    def generate_qc_report(
        self,
        positive_control_od: float,
        negative_control_od: float,
        mic_results: Optional[Dict[str, Dict]] = None,
    ) -> Dict[str, any]:
        """
        Genera reporte completo de QC.

        Args:
            positive_control_od: OD del control positivo
            negative_control_od: OD del control negativo
            mic_results: Resultados MIC para validación de coherencia (opcional)

        Returns:
            Dict con reporte estructurado:
            {
                'timestamp': datetime,
                'controls': {
                    'positive': QCResult,
                    'negative': QCResult
                },
                'coherence': List[CoherenceIssue],
                'overall_status': 'PASS' | 'WARNING' | 'FAIL',
                'summary': str
            }

        Ejemplo:
            >>> validator = QCValidator()
            >>> report = validator.generate_qc_report(1.5, 0.05)
            >>> print(report['overall_status'])
            PASS
        """
        # Validar controles
        pos_result = self.validate_positive_control(positive_control_od)
        neg_result = self.validate_negative_control(negative_control_od)

        # Validar coherencia si se proporcionan resultados MIC
        coherence_issues = []
        if mic_results:
            coherence_issues = self.validate_coherence(mic_results)

        # Determinar estado general
        controls_passed = pos_result.passed and neg_result.passed
        has_failures = pos_result.severity == "FAIL" or neg_result.severity == "FAIL"
        has_warnings = (
            pos_result.severity == "WARNING"
            or neg_result.severity == "WARNING"
            or len(coherence_issues) > 0
        )

        if has_failures:
            overall_status = "FAIL"
            summary = "Validación QC FALLÓ - Revisar controles"
        elif has_warnings:
            overall_status = "WARNING"
            summary = f"Validación QC con advertencias ({len(coherence_issues)} problemas de coherencia)"
        else:
            overall_status = "PASS"
            summary = "Validación QC exitosa - Todos los controles dentro del rango"

        report = {
            "timestamp": datetime.now(),
            "controls": {"positive": pos_result, "negative": neg_result},
            "coherence": coherence_issues,
            "overall_status": overall_status,
            "summary": summary,
            "details": {
                "positive_od": positive_control_od,
                "negative_od": negative_control_od,
                "coherence_issues_count": len(coherence_issues),
                "controls_passed": controls_passed,
            },
        }

        return report

    def reset(self):
        """Limpia resultados previos para nueva validación."""
        self.qc_results.clear()
        self.coherence_issues.clear()
