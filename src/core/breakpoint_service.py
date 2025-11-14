"""
Módulo Breakpoint Service - Gestión de Puntos de Corte AST

Este módulo proporciona servicios para consultar y aplicar breakpoints
de susceptibilidad antimicrobiana según guías CLSI y EUCAST.

Funcionalidades principales:
- Consulta de breakpoints por antibiótico y guía (CLSI/EUCAST)
- Interpretación de MICs como S/I/R
- Verificación de cobertura de panel
- Cacheo de breakpoints frecuentes

Organismo fijo: Pseudomonas aeruginosa (no requiere organism_id)

Autor: Sistema AST Simulator
Fecha: 11 de noviembre de 2025
"""

from typing import Optional, Dict, List, Tuple
from src.data.database import get_session
from src.data.models import Breakpoint, PanelLayout


# Constante global del organismo
ORGANISM_NAME = "Pseudomonas aeruginosa"

# Cache de breakpoints para optimización
_breakpoint_cache: Dict[Tuple[str, str], Breakpoint] = {}


class BreakpointService:
    """
    Servicio para gestionar breakpoints de susceptibilidad antimicrobiana.

    Simplificado para trabajar exclusivamente con Pseudomonas aeruginosa.
    No requiere organism_id en ningún método.
    """

    def __init__(self, use_cache: bool = True):
        """
        Inicializa el servicio de breakpoints.

        Args:
            use_cache: Si True, cachea breakpoints en memoria para consultas rápidas
        """
        self.use_cache = use_cache
        self.session = get_session()

    def get_breakpoint(
        self,
        antibiotico_nombre: str,
        guideline: str = "EUCAST",
    ) -> Optional[Breakpoint]:
        """
        Obtiene el breakpoint para un antibiótico específico.

        Prioriza EUCAST sobre CLSI. Si no encuentra con la guía solicitada,
        intenta con la alternativa (fallback automático).

        Args:
            antibiotico_nombre: Nombre del antibiótico (ej: 'Meropenem')
            guideline: 'EUCAST' (por defecto) o 'CLSI'

        Returns:
            Objeto Breakpoint o None si no se encuentra

        Ejemplo:
            >>> service = BreakpointService()
            >>> bp = service.get_breakpoint('Meropenem', 'EUCAST')
            >>> print(f"MIC S≤{bp.s_mic}, R>{bp.r_mic}")
            MIC S≤2.0, R>8.0
        """
        # Verificar cache primero
        cache_key = (antibiotico_nombre, guideline)
        if self.use_cache and cache_key in _breakpoint_cache:
            return _breakpoint_cache[cache_key]

        # Query base
        breakpoint = (
            self.session.query(Breakpoint)
            .filter(
                Breakpoint.antibiotico == antibiotico_nombre,
                Breakpoint.standard == guideline,
            )
            .first()
        )

        # Fallback: Si no encontró con guideline solicitado, intentar con el otro
        if breakpoint is None:
            alternative_guideline = "CLSI" if guideline == "EUCAST" else "EUCAST"
            breakpoint = (
                self.session.query(Breakpoint)
                .filter(
                    Breakpoint.antibiotico == antibiotico_nombre,
                    Breakpoint.standard == alternative_guideline,
                )
                .first()
            )

        # Guardar en cache
        if breakpoint and self.use_cache:
            _breakpoint_cache[cache_key] = breakpoint

        return breakpoint

    def interpret_mic(
        self,
        mic_value: float,
        mic_operator: str,
        breakpoint_s: float,
        breakpoint_r: float,
    ) -> str:
        """
        Interpreta un valor MIC como Sensible/Intermedio/Resistente.

        Reglas estándar:
        - MIC ≤ breakpoint_s → S (Sensible)
        - breakpoint_s < MIC < breakpoint_r → I (Intermedio)
        - MIC ≥ breakpoint_r → R (Resistente)

        Casos especiales con operadores:
        - MIC_operator '≤' o '<=' → Valor es límite superior, probablemente S
        - MIC_operator '≥' o '>=' → Valor es límite inferior, probablemente R
        - MIC_operator '=' → Valor exacto, aplicar reglas estándar

        Args:
            mic_value: Valor numérico del MIC (µg/mL)
            mic_operator: Operador: '=', '<=', '>='
            breakpoint_s: Breakpoint de sensibilidad
            breakpoint_r: Breakpoint de resistencia

        Returns:
            'S', 'I', o 'R'

        Ejemplo:
            >>> service = BreakpointService()
            >>> result = service.interpret_mic(4.0, '=', 2.0, 8.0)
            >>> print(result)
            I
        """
        # Normalizar operadores
        if mic_operator in ["≤", "<="]:
            mic_operator = "<="
        elif mic_operator in ["≥", ">="]:
            mic_operator = ">="
        else:
            mic_operator = "="

        # Casos especiales con operadores
        if mic_operator == "<=":
            # MIC ≤ valor → Crecimiento inhibido a concentración baja
            if mic_value <= breakpoint_s:
                return "S"
            elif mic_value < breakpoint_r:
                return "I"
            else:
                return "I"  # Conservador: no asumimos R sin confirmación

        elif mic_operator == ">=":
            # MIC ≥ valor → Crecimiento NO inhibido a concentración alta
            if mic_value >= breakpoint_r:
                return "R"
            elif mic_value > breakpoint_s:
                return "I"
            else:
                return "I"  # Conservador: no asumimos S sin confirmación

        else:  # mic_operator == '='
            # Valor exacto: aplicar reglas estándar
            if mic_value <= breakpoint_s:
                return "S"
            elif mic_value >= breakpoint_r:
                return "R"
            else:
                return "I"

    def interpret_with_breakpoint(
        self,
        mic_value: float,
        mic_operator: str,
        antibiotico_nombre: str,
        guideline: str = "EUCAST",
    ) -> Tuple[str, Optional[Breakpoint]]:
        """
        Interpreta MIC consultando automáticamente el breakpoint.

        Función de conveniencia que combina get_breakpoint() + interpret_mic().

        Args:
            mic_value: Valor del MIC
            mic_operator: Operador ('=', '<=', '>=')
            antibiotico_nombre: Nombre del antibiótico (ej: 'Meropenem')
            guideline: 'EUCAST' o 'CLSI'

        Returns:
            Tupla (interpretación, breakpoint_usado)
            - interpretación: 'S', 'I', 'R', o 'UNKNOWN'
            - breakpoint_usado: Objeto Breakpoint o None

        Ejemplo:
            >>> service = BreakpointService()
            >>> interp, bp = service.interpret_with_breakpoint(16.0, '=', 'Meropenem', 'CLSI')
            >>> print(f"{interp} usando {bp.standard}")
            R usando CLSI
        """
        breakpoint = self.get_breakpoint(antibiotico_nombre, guideline)

        if breakpoint is None:
            return "UNKNOWN", None

        interpretation = self.interpret_mic(
            mic_value, mic_operator, breakpoint.breakpoint_s, breakpoint.breakpoint_r
        )

        return interpretation, breakpoint

    def check_breakpoint_coverage(
        self, panel_name: str, antibiotico_nombre: str, guideline: str = "EUCAST"
    ) -> Dict[str, any]:
        """
        Verifica si el panel cubre adecuadamente los breakpoints.

        Analiza si las concentraciones del panel incluyen valores alrededor
        de los breakpoints S y R (típicamente ±1 dilución).

        Args:
            panel_name: Nombre del panel (ej: 'EUCAST_PA_v2025')
            antibiotico_nombre: Nombre del antibiótico (ej: 'Meropenem')
            guideline: Guía de breakpoints a usar

        Returns:
            Dict con:
            - 'covers_s': bool, si cubre breakpoint S
            - 'covers_r': bool, si cubre breakpoint R
            - 'missing_concentrations': list de concentraciones recomendadas
            - 'panel_concentrations': list de concentraciones en el panel
        """
        # Obtener breakpoint
        breakpoint = self.get_breakpoint(antibiotico_nombre, guideline)

        if breakpoint is None:
            return {
                "covers_s": False,
                "covers_r": False,
                "missing_concentrations": [],
                "panel_concentrations": [],
                "error": "Breakpoint no encontrado",
            }

        # Obtener concentraciones del panel para este antibiótico
        panel_wells = (
            self.session.query(PanelLayout)
            .filter(
                PanelLayout.panel_name == panel_name,
                PanelLayout.antibiotico == antibiotico_nombre,
                PanelLayout.tipo == "test",
            )
            .all()
        )

        panel_concentrations = sorted([well.concentracion for well in panel_wells])

        if not panel_concentrations:
            return {
                "covers_s": False,
                "covers_r": False,
                "missing_concentrations": [breakpoint.s_mic, breakpoint.r_mic],
                "panel_concentrations": [],
                "error": "Antibiótico no encontrado en el panel",
            }

        # Verificar cobertura (necesitamos ±1 dilución alrededor de cada breakpoint)
        # Dilución típica = factor 2 (serie log2)
        covers_s = any(
            breakpoint.s_mic / 2 <= conc <= breakpoint.s_mic * 2
            for conc in panel_concentrations
        )

        covers_r = any(
            breakpoint.r_mic / 2 <= conc <= breakpoint.r_mic * 2
            for conc in panel_concentrations
        )

        # Identificar concentraciones faltantes
        missing = []
        if not covers_s:
            missing.append(breakpoint.s_mic)
        if not covers_r:
            missing.append(breakpoint.r_mic)

        return {
            "covers_s": covers_s,
            "covers_r": covers_r,
            "missing_concentrations": missing,
            "panel_concentrations": panel_concentrations,
            "breakpoint_s": breakpoint.s_mic,
            "breakpoint_r": breakpoint.r_mic,
            "guideline": breakpoint.standard,
        }

    def get_all_breakpoints_for_panel(
        self, antibiotico_nombres: List[str], guideline: str = "EUCAST"
    ) -> Dict[str, Optional[Breakpoint]]:
        """
        Obtiene breakpoints para múltiples antibióticos de un panel.

        Útil para cargar todos los breakpoints al inicio de una simulación.

        Args:
            antibiotico_nombres: Lista de nombres de antibióticos
            guideline: Guía a usar

        Returns:
            Diccionario {antibiotico_nombre: Breakpoint}

        Ejemplo:
            >>> service = BreakpointService()
            >>> breakpoints = service.get_all_breakpoints_for_panel(
            ...     ['Meropenem', 'Ciprofloxacino'], 'EUCAST'
            ... )
            >>> print(f"Breakpoints cargados: {len(breakpoints)}")
            Breakpoints cargados: 2
        """
        breakpoints = {}
        for antibiotico_nombre in antibiotico_nombres:
            bp = self.get_breakpoint(antibiotico_nombre, guideline)
            breakpoints[antibiotico_nombre] = bp

        return breakpoints

    def clear_cache(self):
        """
        Limpia el cache de breakpoints.

        Útil si se actualizan breakpoints en la base de datos durante
        la ejecución de la aplicación.
        """
        global _breakpoint_cache
        _breakpoint_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas del cache.

        Returns:
            Dict con 'cached_entries' y 'cache_enabled'
        """
        return {
            "cached_entries": len(_breakpoint_cache),
            "cache_enabled": self.use_cache,
        }
