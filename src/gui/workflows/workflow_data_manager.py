"""
Workflow Data Manager - Gestión de datos entre widgets del workflow

Responsabilidad única: Transformar y distribuir datos entre componentes.
Principio Interface Segregation: Interfaces específicas para cada tipo de dato.

Autor: Sistema AST Simulator
Fecha: 17 de noviembre de 2025
"""

from typing import Dict, List, Any


class WorkflowDataManager:
    """
    Gestiona la transformación y distribución de datos en el workflow.

    Responsabilidades:
    - Transformar datos entre formatos de widgets
    - Validar integridad de datos
    - Generar datos derivados (ej: curvas de crecimiento)

    Principio: Single Responsibility (gestión de datos solamente)
    """

    def __init__(self):
        """Inicializa el gestor de datos."""
        self.current_profile_id: int = None
        self.current_results: Dict[str, Any] = {}

    def set_bacteria_profile(self, profile_id: int):
        """
        Almacena el ID del perfil bacteriano actual.

        Args:
            profile_id: ID del perfil en la base de datos
        """
        self.current_profile_id = profile_id

    def get_bacteria_profile(self) -> int:
        """
        Obtiene el ID del perfil bacteriano actual.

        Returns:
            ID del perfil o None si no hay perfil cargado
        """
        return self.current_profile_id

    def set_ast_results(self, results: dict):
        """
        Almacena los resultados de la simulación AST.

        Args:
            results: Diccionario con well_data_list, mic_results, qc_report
        """
        self.current_results = results

    def get_well_data(self) -> List[dict]:
        """
        Obtiene los datos de pocillos de la simulación actual.

        Returns:
            Lista de diccionarios con datos de pocillos
        """
        return self.current_results.get("well_data_list", [])

    def get_mic_results(self) -> List[dict]:
        """
        Obtiene los resultados MIC de la simulación actual.

        Returns:
            Lista de diccionarios con resultados MIC
        """
        return self.current_results.get("mic_results", [])

    def generate_growth_curves_data(
        self, well_data_list: List[dict], mic_results: List[dict]
    ) -> Dict[str, List[Dict]]:
        """
        Genera datos de curvas de crecimiento desde datos de pocillos.

        Args:
            well_data_list: Lista de datos de pocillos
            mic_results: Lista de resultados MIC

        Returns:
            Diccionario formateado para GrowthCurveWidget:
            {
                'antibiotico1': [
                    {
                        'concentracion': 0.0,
                        'tiempos': [0, 1, 2, ..., 18],
                        'ods': [0.1, 0.15, ..., 2.5],
                        'mic': False
                    },
                    ...
                ],
                ...
            }
        """
        growth_data = {}

        # Agrupar pocillos por antibiótico
        wells_by_antibiotic = {}
        for well in well_data_list:
            if well.get("tipo") == "muestra":
                antibiotico = well.get("antibiotico")
                if antibiotico:
                    if antibiotico not in wells_by_antibiotic:
                        wells_by_antibiotic[antibiotico] = []
                    wells_by_antibiotic[antibiotico].append(well)

        # Crear entrada por antibiótico
        for antibiotico, wells in wells_by_antibiotic.items():
            # Buscar MIC correspondiente
            mic_data = next(
                (m for m in mic_results if m.get("antibiotico") == antibiotico), None
            )
            mic_value = mic_data.get("mic_value") if mic_data else None

            # Ordenar pocillos por concentración
            wells_sorted = sorted(
                wells,
                key=lambda w: float(w.get("concentracion", 0)),
                reverse=False,
            )

            # Extraer curvas de crecimiento
            curves_list = []
            for well in wells_sorted:
                conc = well.get("concentracion")
                growth_curve = well.get("growth_curve", [])

                if conc is not None and growth_curve:
                    # Extraer tiempos y ODs de la curva
                    tiempos = [point.get("time", 0) for point in growth_curve]
                    ods = [point.get("od", 0) for point in growth_curve]

                    # Determinar si esta concentración es el MIC
                    is_mic = mic_value is not None and abs(conc - mic_value) < 0.001

                    curves_list.append(
                        {
                            "concentracion": conc,
                            "tiempos": tiempos,
                            "ods": ods,
                            "mic": is_mic,
                        }
                    )

            # Agregar al diccionario solo si hay curvas
            if curves_list:
                growth_data[antibiotico] = curves_list

        return growth_data

    def clear_all(self):
        """Limpia todos los datos almacenados."""
        self.current_profile_id = None
        self.current_results = {}
