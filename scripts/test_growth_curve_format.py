"""
Test Growth Curve Data Format

Verifica que el formato de datos generado por workflow_data_manager
sea compatible con GrowthCurveWidget.

Autor: Sistema AST Simulator
Fecha: Noviembre 2025
"""

import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.gui.workflows.workflow_data_manager import WorkflowDataManager


def test_growth_curve_format():
    """Prueba el formato de datos de curvas de crecimiento."""
    print("\n=== TEST: Formato de Datos de Curvas de Crecimiento ===\n")

    # Datos de ejemplo simulando lo que retorna ASTSimulator
    well_data_list = [
        {
            "well_id": "A1",
            "antibiotico": "Ciprofloxacino",
            "concentracion": 0.0,
            "tipo": "muestra",
            "od_final": 2.5,
            "growth_curve": [
                {"time": 0, "od": 0.1},
                {"time": 6, "od": 0.5},
                {"time": 12, "od": 1.5},
                {"time": 18, "od": 2.5},
            ],
        },
        {
            "well_id": "A2",
            "antibiotico": "Ciprofloxacino",
            "concentracion": 0.5,
            "tipo": "muestra",
            "od_final": 1.2,
            "growth_curve": [
                {"time": 0, "od": 0.1},
                {"time": 6, "od": 0.3},
                {"time": 12, "od": 0.8},
                {"time": 18, "od": 1.2},
            ],
        },
        {
            "well_id": "A3",
            "antibiotico": "Ciprofloxacino",
            "concentracion": 1.0,
            "tipo": "muestra",
            "od_final": 0.15,
            "growth_curve": [
                {"time": 0, "od": 0.1},
                {"time": 6, "od": 0.11},
                {"time": 12, "od": 0.13},
                {"time": 18, "od": 0.15},
            ],
        },
        {
            "well_id": "B1",
            "antibiotico": "Meropenem",
            "concentracion": 0.0,
            "tipo": "muestra",
            "od_final": 2.5,
            "growth_curve": [
                {"time": 0, "od": 0.1},
                {"time": 6, "od": 0.5},
                {"time": 12, "od": 1.5},
                {"time": 18, "od": 2.5},
            ],
        },
    ]

    mic_results = [
        {"antibiotico": "Ciprofloxacino", "mic_value": 1.0, "mic_operador": "="},
        {"antibiotico": "Meropenem", "mic_value": 0.5, "mic_operador": "<="},
    ]

    # Crear data manager y generar datos
    data_manager = WorkflowDataManager()
    growth_data = data_manager.generate_growth_curves_data(well_data_list, mic_results)

    # Verificar formato
    print(f"Tipo de retorno: {type(growth_data)}")
    print(f"Es diccionario: {isinstance(growth_data, dict)}")
    print(f"Antibióticos encontrados: {list(growth_data.keys())}")

    # Verificar estructura para cada antibiótico
    for antibiotico, curves in growth_data.items():
        print(f"\n--- {antibiotico} ---")
        print(f"  Número de curvas: {len(curves)}")

        for i, curve in enumerate(curves):
            print(f"  Curva {i + 1}:")
            print(f"    Concentración: {curve.get('concentracion')}")
            print(f"    Tiempos: {curve.get('tiempos')}")
            print(f"    ODs: {curve.get('ods')}")
            print(f"    Es MIC: {curve.get('mic')}")

    # Assertions
    assert isinstance(growth_data, dict), "Debe retornar un diccionario"
    assert "Ciprofloxacino" in growth_data, "Debe incluir Ciprofloxacino"
    assert "Meropenem" in growth_data, "Debe incluir Meropenem"

    # Verificar estructura de curvas
    cipro_curves = growth_data["Ciprofloxacino"]
    assert len(cipro_curves) == 3, "Ciprofloxacino debe tener 3 curvas"

    first_curve = cipro_curves[0]
    assert "concentracion" in first_curve, "Curva debe tener 'concentracion'"
    assert "tiempos" in first_curve, "Curva debe tener 'tiempos'"
    assert "ods" in first_curve, "Curva debe tener 'ods'"
    assert "mic" in first_curve, "Curva debe tener 'mic'"

    assert isinstance(first_curve["tiempos"], list), "tiempos debe ser lista"
    assert isinstance(first_curve["ods"], list), "ods debe ser lista"
    assert len(first_curve["tiempos"]) == len(first_curve["ods"]), (
        "tiempos y ods deben tener igual longitud"
    )

    # Verificar que el MIC está marcado correctamente
    mic_curve = next((c for c in cipro_curves if c["mic"]), None)
    assert mic_curve is not None, "Debe haber una curva marcada como MIC"
    assert mic_curve["concentracion"] == 1.0, "MIC debe ser 1.0 para Ciprofloxacino"

    print("\n✅ TEST PASADO - Formato correcto para GrowthCurveWidget\n")
    return True


if __name__ == "__main__":
    try:
        test_growth_curve_format()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
