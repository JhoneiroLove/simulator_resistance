"""
Test de integración para AST Workflow

Verifica que el workflow completo funciona correctamente con todos los widgets.
"""

from PyQt5.QtWidgets import QApplication
import sys

# Crear QApplication para tests de GUI
if not QApplication.instance():
    app = QApplication(sys.argv)


def test_ast_workflow_creation():
    """Verifica que el workflow se puede crear sin errores."""
    from src.gui.workflows.ast_workflow import ASTWorkflow

    workflow = ASTWorkflow()

    # Verificar que los widgets existen
    assert hasattr(workflow, "panel_widget")
    assert hasattr(workflow, "plate_viewer")
    assert hasattr(workflow, "results_table")
    assert hasattr(workflow, "growth_curve_widget")

    # Verificar que los widgets no son None
    assert workflow.panel_widget is not None
    assert workflow.plate_viewer is not None
    assert workflow.results_table is not None
    assert workflow.growth_curve_widget is not None

    print("✅ Workflow creado exitosamente con 4 widgets")


def test_ast_workflow_clear():
    """Verifica que el método clear_all funciona."""
    from src.gui.workflows.ast_workflow import ASTWorkflow

    workflow = ASTWorkflow()
    workflow.clear_all()

    print("✅ clear_all() ejecutado sin errores")


def test_growth_curve_generation():
    """Verifica que se pueden generar curvas de crecimiento."""
    from src.gui.workflows.ast_workflow import ASTWorkflow

    workflow = ASTWorkflow()

    # Datos de prueba simulados
    well_data_list = [
        {
            "antibiotico": "Meropenem",
            "concentracion": 0.0,
            "growth_curve": [0.1, 0.15, 0.2, 0.3, 0.5, 0.8, 1.2, 1.8, 2.5],
        },
        {
            "antibiotico": "Meropenem",
            "concentracion": 1.0,
            "growth_curve": [0.1, 0.12, 0.15, 0.18, 0.22, 0.25, 0.28, 0.3, 0.32],
        },
        {
            "antibiotico": "Meropenem",
            "concentracion": 2.0,
            "growth_curve": [0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18],
        },
    ]

    mic_results = [
        {"antibiotico": "Meropenem", "mic_value": 2.0, "interpretacion": "R"}
    ]

    growth_data = workflow._generate_growth_curves_from_wells(
        well_data_list, mic_results
    )

    # Verificar estructura
    assert "Meropenem" in growth_data
    assert len(growth_data["Meropenem"]) == 3

    # Verificar que la curva del MIC está marcada
    mic_curve = [c for c in growth_data["Meropenem"] if c["mic"]]
    assert len(mic_curve) == 1
    assert mic_curve[0]["concentracion"] == 2.0

    print("✅ Generación de curvas de crecimiento exitosa")
    print(f"   - Antibióticos: {list(growth_data.keys())}")
    print(f"   - Curvas por antibiótico: {len(growth_data['Meropenem'])}")
    print("   - MIC marcado correctamente en 2.0 µg/mL")


def test_growth_curve_widget_integration():
    """Verifica que el widget de curvas puede cargar datos."""
    from src.gui.widgets.growth_curve_widget import GrowthCurveWidget

    widget = GrowthCurveWidget()

    # Datos de prueba
    growth_data = {
        "Meropenem": [
            {
                "concentracion": 0.0,
                "tiempos": list(range(19)),
                "ods": [0.1 + i * 0.15 for i in range(19)],
                "mic": False,
            },
            {
                "concentracion": 2.0,
                "tiempos": list(range(19)),
                "ods": [0.1 + i * 0.01 for i in range(19)],
                "mic": True,
            },
        ]
    }

    widget.load_growth_data(growth_data)

    # Verificar que el combo tiene el antibiótico
    assert widget.antibiotic_combo.count() == 1
    assert widget.antibiotic_combo.currentText() == "Meropenem"

    print("✅ Widget de curvas carga datos correctamente")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTS DE INTEGRACIÓN AST WORKFLOW")
    print("=" * 60 + "\n")

    test_ast_workflow_creation()
    test_ast_workflow_clear()
    test_growth_curve_generation()
    test_growth_curve_widget_integration()

    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON")
    print("=" * 60 + "\n")
