"""
Módulo AST Simulator - Simulador de Pruebas de Sensibilidad Antimicrobiana

Este módulo simula el proceso completo de un panel AST (Antimicrobial Susceptibility Testing)
para Pseudomonas aeruginosa, incluyendo:
- Incubación de 18 horas con lecturas ópticas
- Curvas de crecimiento logísticas
- Cálculo de MIC por umbral e interpolación
- Interpretación S/R según breakpoints EUCAST/CLSI
- Control de calidad de pocillos
- Variabilidad del inóculo y efecto en MIC aparente (v2.0)

Autor: Sistema AST Simulator
Fecha: 17 de noviembre de 2025
Versión: 2.0 - Variabilidad de Inóculo
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import math
import random

from src.data.database import get_session
from src.data.models import PanelLayout, Breakpoint, BacteriaProfile


ORGANISM_NAME = "Pseudomonas aeruginosa"
ORGANISM_GRAM = "negativo"
DEFAULT_TEMPERATURE = 37.0
DEFAULT_INOCULUM = 0.5
DEFAULT_DURATION = 18


@dataclass
class WellReading:
    """Lectura óptica de un pocillo en un tiempo específico."""

    tiempo_minutos: int
    od_600: float
    turbidez: float
    crecimiento_detectado: bool


@dataclass
class WellData:
    """Datos completos de un pocillo AST."""

    posicion: str
    antibiotico: str
    concentracion: float
    tipo: str
    readings: List[WellReading]

    @property
    def od_final(self) -> float:
        """OD al final de la incubación (18h)."""
        if not self.readings:
            return 0.0
        return self.readings[-1].od_600


@dataclass
class MICResult:
    """Resultado MIC para un antibiótico."""

    antibiotico: str
    mic_value: float
    mic_operador: str
    metodo: str
    interpretacion: str
    breakpoint_usado: str
    confianza: float


class ASTSimulator:
    """
    Simulador de panel AST para Pseudomonas aeruginosa.

    Simula el proceso completo de incubación, lectura óptica y cálculo de MICs
    para un panel de 96 wells con múltiples antibióticos y concentraciones.
    """

    def __init__(
        self,
        bacteria_profile_id: int,
        panel_name: str = "Pseudomonas_Standard_Panel",
        inoculo_mcfarland: float = DEFAULT_INOCULUM,
        temperatura: float = DEFAULT_TEMPERATURE,
        duracion_horas: int = DEFAULT_DURATION,
    ):
        """
        Inicializa el simulador AST.

        Args:
            bacteria_profile_id: ID del perfil bacteriano generado
            panel_name: Nombre del panel a usar
            inoculo_mcfarland: Densidad del inóculo (típico 0.5)
            temperatura: Temperatura de incubación en °C
            duracion_horas: Duración de incubación en horas
        """
        self.session = get_session()
        self.bacteria_profile_id = bacteria_profile_id
        self.panel_name = panel_name
        self.inoculo_mcfarland = inoculo_mcfarland
        self.temperatura = temperatura
        self.duracion_horas = duracion_horas
        self.duracion_minutos = duracion_horas * 60

        self.bacteria_profile = None
        self.panel_wells: List[WellData] = []
        self.mic_results: List[MICResult] = []
        self.qc_passed = False

        # NUEVO: Variabilidad del inóculo (±0.05 McFarland)
        # Simula error en preparación de suspensión bacteriana
        self.inoculo_deviation = random.uniform(-0.05, 0.05)
        self.inoculo_real = self.inoculo_mcfarland + self.inoculo_deviation

        self._load_bacteria_profile()
        self._load_panel_layout()

    def _load_bacteria_profile(self):
        """Carga el perfil bacteriano desde la BD."""
        self.bacteria_profile = (
            self.session.query(BacteriaProfile)
            .filter_by(id=self.bacteria_profile_id)
            .first()
        )

        if not self.bacteria_profile:
            raise ValueError(
                f"BacteriaProfile {self.bacteria_profile_id} no encontrado"
            )

    def _load_panel_layout(self):
        """Carga el layout del panel desde la BD."""
        wells = (
            self.session.query(PanelLayout).filter_by(panel_name=self.panel_name).all()
        )

        if not wells:
            raise ValueError(f"Panel {self.panel_name} no encontrado en BD")

        for well in wells:
            self.panel_wells.append(
                WellData(
                    posicion=well.well_position,
                    antibiotico=well.antibiotico,
                    concentracion=well.concentracion,
                    tipo=well.tipo,
                    readings=[],
                )
            )

    def simulate_incubation(self) -> Dict:
        """
        Simula el proceso completo de incubación de 18 horas.

        Genera lecturas ópticas cada 60 minutos para cada pocillo,
        aplicando curvas de crecimiento logísticas según la concentración
        de antibiótico y la resistencia de la bacteria.

        Returns:
            Diccionario con resumen de la simulación
        """
        time_points = range(0, self.duracion_minutos + 1, 60)

        for well in self.panel_wells:
            for tiempo in time_points:
                if well.tipo in ["control_positivo", "control_negativo"]:
                    reading = self._simulate_control_well(well, tiempo)
                else:
                    reading = self._simulate_test_well(well, tiempo)

                well.readings.append(reading)

        return {
            "duracion_minutos": self.duracion_minutos,
            "total_wells": len(self.panel_wells),
            "lecturas_por_well": len(time_points),
            "temperatura": self.temperatura,
            "inoculo": self.inoculo_mcfarland,
        }

    def _simulate_test_well(self, well: WellData, tiempo_minutos: int) -> WellReading:
        """
        Simula lectura de un pocillo de prueba usando modelo logístico.

        La curva de crecimiento depende de:
        - MIC calculado del antibiótico (desde bacteria_profile)
        - Concentración en el pocillo
        - Si concentración < MIC: crece normalmente
        - Si concentración >= MIC: crecimiento inhibido

        NUEVO v2.0: Inóculo real afecta OD inicial y capacidad de crecimiento

        Args:
            well: Datos del pocillo
            tiempo_minutos: Tiempo desde inicio de incubación

        Returns:
            Lectura óptica en ese tiempo
        """
        import json

        mics_calculated = json.loads(self.bacteria_profile.mics_calculated)
        mic_bacteria = mics_calculated.get(well.antibiotico, 1.0)

        # NUEVO v2.0: Inóculo real afecta OD inicial y parámetros de crecimiento
        # Inóculo más alto → más células → mayor OD inicial y final
        od_initial = 0.05 * self.inoculo_real  # Usar inóculo real (con desviación)

        # Ajustar OD máxima con alta sensibilidad al inóculo para efecto visible en MIC
        # Factor amplificado: 1 + 5 * (desviación / nominal)
        # Ejemplo: inóculo +10% → od_max +50% → cambia MIC 1-2 diluciones
        inoculum_deviation_pct = (
            self.inoculo_real - self.inoculo_mcfarland
        ) / self.inoculo_mcfarland
        inoculum_factor = 1.0 + (5.0 * inoculum_deviation_pct)
        od_max = 2.0 * inoculum_factor

        k = 0.02
        t_mid = 480

        if well.concentracion < mic_bacteria:
            od = od_initial + (od_max - od_initial) / (
                1 + math.exp(-k * (tiempo_minutos - t_mid))
            )
        elif well.concentracion == mic_bacteria:
            od = od_initial + (od_max * 0.3 - od_initial) / (
                1 + math.exp(-k * (tiempo_minutos - t_mid))
            )
        else:
            ratio = mic_bacteria / well.concentracion
            od_max_inhibido = od_max * ratio * 0.2
            od = od_initial + (od_max_inhibido - od_initial) / (
                1 + math.exp(-k * (tiempo_minutos - t_mid))
            )

        od = max(od_initial, min(od, 4.0))

        return WellReading(
            tiempo_minutos=tiempo_minutos,
            od_600=round(od, 3),
            turbidez=round(od * 100, 1),
            crecimiento_detectado=(od > 0.3),
        )

    def _simulate_control_well(
        self, well: WellData, tiempo_minutos: int
    ) -> WellReading:
        """
        Simula lectura de pocillos de control QC.

        - Control positivo: Crecimiento normal (sin antibiótico)
        - Control negativo: Sin crecimiento (sin bacteria)

        NUEVO v2.0: Control positivo usa inóculo real (afecta OD inicial y final)

        Args:
            well: Datos del pocillo de control
            tiempo_minutos: Tiempo desde inicio

        Returns:
            Lectura óptica esperada
        """
        od_initial = 0.05 * self.inoculo_real  # Usar inóculo real

        if well.tipo == "control_positivo":
            # Ajustar OD máxima con alta sensibilidad al inóculo
            inoculum_deviation_pct = (
                self.inoculo_real - self.inoculo_mcfarland
            ) / self.inoculo_mcfarland
            inoculum_factor = 1.0 + (5.0 * inoculum_deviation_pct)
            od_max = 2.0 * inoculum_factor

            k = 0.02
            t_mid = 480
            od = od_initial + (od_max - od_initial) / (
                1 + math.exp(-k * (tiempo_minutos - t_mid))
            )
        else:
            od = od_initial

        return WellReading(
            tiempo_minutos=tiempo_minutos,
            od_600=round(od, 3),
            turbidez=round(od * 100, 1),
            crecimiento_detectado=(od > 0.3),
        )

    def calculate_mics(self, metodo: str = "umbral") -> List[MICResult]:
        """
        Calcula MICs para todos los antibióticos del panel.

        Args:
            metodo: "umbral" o "interpolacion"

        Returns:
            Lista de resultados MIC
        """
        antibioticos_unicos = set(
            well.antibiotico for well in self.panel_wells if well.tipo == "test"
        )

        self.mic_results = []

        for antibiotico in antibioticos_unicos:
            if metodo == "umbral":
                mic_result = self._calculate_mic_by_threshold(antibiotico)
            else:
                mic_result = self._calculate_mic_by_interpolation(antibiotico)

            self.mic_results.append(mic_result)

        return self.mic_results

    def _calculate_mic_by_threshold(self, antibiotico: str) -> MICResult:
        """
        Calcula MIC usando método de umbral de OD.

        Algoritmo:
        1. Ordenar wells por concentración creciente
        2. Encontrar primera concentración con OD < 0.3
        3. Esa concentración es el MIC

        Args:
            antibiotico: Nombre del antibiótico

        Returns:
            Resultado MIC
        """
        umbral_od = 0.3

        wells_antibiotico = [
            w
            for w in self.panel_wells
            if w.antibiotico == antibiotico and w.tipo == "test"
        ]
        wells_ordenados = sorted(wells_antibiotico, key=lambda w: w.concentracion)

        mic_value = None
        mic_operador = "="

        for well in wells_ordenados:
            if well.od_final < umbral_od:
                mic_value = well.concentracion
                break

        if mic_value is None:
            mic_value = wells_ordenados[-1].concentracion
            mic_operador = ">="

        interpretacion = self._interpret_mic(antibiotico, mic_value)

        return MICResult(
            antibiotico=antibiotico,
            mic_value=mic_value,
            mic_operador=mic_operador,
            metodo="umbral",
            interpretacion=interpretacion,
            breakpoint_usado="EUCAST",
            confianza=0.95,
        )

    def _calculate_mic_by_interpolation(self, antibiotico: str) -> MICResult:
        """
        Calcula MIC usando interpolación lineal entre wells.

        Encuentra dos wells consecutivos donde cruza el umbral
        y calcula valor exacto por interpolación.

        Args:
            antibiotico: Nombre del antibiótico

        Returns:
            Resultado MIC interpolado
        """
        umbral_od = 0.3

        wells_antibiotico = [
            w
            for w in self.panel_wells
            if w.antibiotico == antibiotico and w.tipo == "test"
        ]
        wells_ordenados = sorted(wells_antibiotico, key=lambda w: w.concentracion)

        for i in range(len(wells_ordenados) - 1):
            well_low = wells_ordenados[i]
            well_high = wells_ordenados[i + 1]

            if well_low.od_final >= umbral_od and well_high.od_final < umbral_od:
                mic_value = well_low.concentracion + (
                    (well_high.concentracion - well_low.concentracion)
                    * (
                        (well_low.od_final - umbral_od)
                        / (well_low.od_final - well_high.od_final)
                    )
                )

                interpretacion = self._interpret_mic(antibiotico, mic_value)

                return MICResult(
                    antibiotico=antibiotico,
                    mic_value=round(mic_value, 2),
                    mic_operador="≈",
                    metodo="interpolacion",
                    interpretacion=interpretacion,
                    breakpoint_usado="EUCAST",
                    confianza=0.90,
                )

        return self._calculate_mic_by_threshold(antibiotico)

    def _interpret_mic(self, antibiotico: str, mic_value: float) -> str:
        """
        Interpreta MIC como S o R usando breakpoints EUCAST.

        Args:
            antibiotico: Nombre del antibiótico
            mic_value: Valor MIC en µg/mL

        Returns:
            "S" (sensible) o "R" (resistente)
        """
        breakpoint = (
            self.session.query(Breakpoint)
            .filter_by(antibiotico=antibiotico, standard="EUCAST")
            .first()
        )

        if not breakpoint:
            breakpoint = (
                self.session.query(Breakpoint)
                .filter_by(antibiotico=antibiotico, standard="CLSI")
                .first()
            )

        if breakpoint:
            return breakpoint.interpret_mic(mic_value)

        return "R"

    def apply_qc_checks(self) -> Dict:
        """
        Aplica validación de controles de calidad.

        Verifica:
        - Control positivo: OD final > 1.0 (crecimiento esperado)
        - Control negativo: OD final < 0.1 (sin crecimiento)

        Returns:
            Diccionario con resultados QC
        """
        control_positivo = next(
            (w for w in self.panel_wells if w.tipo == "control_positivo"), None
        )
        control_negativo = next(
            (w for w in self.panel_wells if w.tipo == "control_negativo"), None
        )

        qc_results = {
            "control_positivo": {
                "passed": False,
                "od_final": 0.0,
                "mensaje": "Control positivo no encontrado",
            },
            "control_negativo": {
                "passed": False,
                "od_final": 0.0,
                "mensaje": "Control negativo no encontrado",
            },
            "qc_global": False,
        }

        if control_positivo:
            od_pos = control_positivo.od_final
            passed_pos = od_pos > 1.0
            qc_results["control_positivo"] = {
                "passed": passed_pos,
                "od_final": od_pos,
                "mensaje": "OK"
                if passed_pos
                else f"Crecimiento insuficiente (OD={od_pos})",
            }

        if control_negativo:
            od_neg = control_negativo.od_final
            passed_neg = od_neg < 0.1
            qc_results["control_negativo"] = {
                "passed": passed_neg,
                "od_final": od_neg,
                "mensaje": "OK"
                if passed_neg
                else f"Contaminación detectada (OD={od_neg})",
            }

        self.qc_passed = (
            qc_results["control_positivo"]["passed"]
            and qc_results["control_negativo"]["passed"]
        )
        qc_results["qc_global"] = self.qc_passed

        return qc_results

    def get_report(self) -> Dict:
        """
        Genera reporte completo de la ejecución AST.

        Returns:
            Diccionario con todos los resultados
        """
        qc_results = self.apply_qc_checks()

        # Convertir well data a formato serializable
        well_data_list = []
        for well in self.panel_wells:
            growth_curve = [
                {
                    "time": reading.tiempo_minutos / 60.0,  # Convertir a horas
                    "od": reading.od_600,
                }
                for reading in well.readings
            ]

            well_data_list.append(
                {
                    "well_id": well.posicion,
                    "antibiotico": well.antibiotico,
                    "concentracion": well.concentracion,
                    "tipo": well.tipo,
                    "od_final": well.od_final,
                    "growth_curve": growth_curve,
                }
            )

        # Formatear resultados MIC con estructura esperada por la tabla
        mic_results_formatted = []
        for r in self.mic_results:
            # Obtener breakpoints de la base de datos
            breakpoint = (
                self.session.query(Breakpoint)
                .filter_by(antibiotico=r.antibiotico, standard="EUCAST")
                .first()
            )

            mic_results_formatted.append(
                {
                    "antibiotico": r.antibiotico,
                    "mic_value": r.mic_value,  # Valor numérico
                    "mic_operador": r.mic_operador,
                    "interpretacion": r.interpretacion,
                    "guideline": r.breakpoint_usado,
                    "version": "v15.0" if r.breakpoint_usado == "EUCAST" else "M07-A11",
                    "breakpoint_s": breakpoint.s_mic if breakpoint else 0,
                    "breakpoint_r": breakpoint.r_mic if breakpoint else 0,
                    "metodo": r.metodo,
                    "confianza": r.confianza,
                }
            )

        return {
            "metadata": {
                "organismo": ORGANISM_NAME,
                "organismo_gram": ORGANISM_GRAM,
                "bacteria_profile_id": self.bacteria_profile_id,
                "escenario": self.bacteria_profile.escenario,
                "panel": self.panel_name,
                "fecha": datetime.now().isoformat(),
                "temperatura": self.temperatura,
                "inoculo_mcfarland": self.inoculo_mcfarland,
                "inoculo_real": round(
                    self.inoculo_real, 3
                ),  # NUEVO: Inóculo con desviación
                "inoculo_deviation": round(
                    self.inoculo_deviation, 3
                ),  # NUEVO: Desviación
                "duracion_horas": self.duracion_horas,
            },
            "qc": qc_results,
            "well_data_list": well_data_list,
            "mic_results": mic_results_formatted,
            "resumen": {
                "total_antibioticos": len(self.mic_results),
                "sensibles": sum(
                    1 for r in self.mic_results if r.interpretacion == "S"
                ),
                "resistentes": sum(
                    1 for r in self.mic_results if r.interpretacion == "R"
                ),
                "qc_passed": self.qc_passed,
            },
        }
