"""
Test Demo - Growth Curve Widget

Prueba visual del widget de curvas de crecimiento con datos sintéticos.

Para ejecutar:
    python scripts/test_growth_curves_demo.py
"""

import sys
from pathlib import Path

# Añadir directorio raíz al path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from PyQt5.QtWidgets import QApplication
from src.gui.widgets.growth_curve_widget import (
    GrowthCurveWidget,
    generate_sample_growth_data,
)


def main():
    """Función principal."""
    app = QApplication(sys.argv)

    # Crear widget
    widget = GrowthCurveWidget()
    widget.setWindowTitle("Test - Growth Curves Widget")
    widget.resize(1000, 600)

    # Generar datos de ejemplo
    print("Generando datos de ejemplo...")
    growth_data = generate_sample_growth_data()

    print(f"Antibióticos generados: {list(growth_data.keys())}")
    for antibiotico, curves in growth_data.items():
        print(f"  - {antibiotico}: {len(curves)} curvas")

    # Cargar datos
    widget.load_growth_data(growth_data)

    # Mostrar widget
    widget.show()

    print("\n✅ Widget cargado correctamente")
    print("📊 Puedes cambiar de antibiótico usando el selector")
    print("🗑️ Puedes limpiar el gráfico con el botón rojo")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
