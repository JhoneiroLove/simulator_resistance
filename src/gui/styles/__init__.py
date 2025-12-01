"""
Módulo de estilos adaptables para Portabilidad

Proporciona gestión centralizada de temas y estilos que se adaptan
al sistema operativo y tema del usuario.
"""

from .theme_manager import ThemeManager, get_theme_manager

__all__ = ["ThemeManager", "get_theme_manager"]
