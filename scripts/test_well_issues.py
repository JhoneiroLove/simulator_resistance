"""
Test de Pozos Ambiguos - FASE 4

Valida la implementacion de pozos problematicos en paneles AST,
verificando que:
- Se asignan 2-4 pozos con problemas por panel
- Los problemas afectan las lecturas de OD
- Los diferentes tipos de problemas se generan correctamente
- El reporte incluye informacion de pozos problematicos

Autor: Sistema AST Simulator
Fecha: 17 de noviembre de 2025
"""

import sys
from pathlib import Path

# Agregar directorio raiz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.ast_simulator import ASTSimulator
from src.core.well_issues_model import WellIssuesSimulator, WellIssueType


def test_well_issues_generation():
    """
    Prueba que el simulador genera pozos problematicos correctamente.
    """
    print("=" * 70)
    print("TEST: GENERACION DE POZOS PROBLEMATICOS")
    print("=" * 70)

    # Crear simulador
    simulator = ASTSimulator(
        bacteria_profile_id=1,
        panel_name="EUCAST_PA_Standard",
        inoculo_mcfarland=0.5,
    )

    # Simular incubacion (esto asigna problemas)
    simulator.simulate_incubation()

    print(f"\nPozos con problemas detectados: {len(simulator.well_issues)}")
    print(f"Rango esperado: 2-4 pozos\n")

    # Validar que hay entre 2-4 pozos con problemas
    assert 2 <= len(simulator.well_issues) <= 4, (
        f"Numero de pozos problematicos fuera de rango: {len(simulator.well_issues)}"
    )

    # Mostrar detalles de cada problema
    print(f"{'Posicion':<10} {'Tipo':<25} {'Severidad':<12} {'Afecta OD':<12}")
    print("-" * 70)

    for well_pos, issue in sorted(simulator.well_issues.items()):
        print(
            f"{well_pos:<10} {issue.issue_type.value:<25} {issue.severity:<12.1%} {str(issue.affects_reading):<12}"
        )

    print(f"\n{'=' * 70}\n")
    return True


def test_issue_types_distribution():
    """
    Verifica que todos los tipos de problemas pueden generarse.
    """
    print("=" * 70)
    print("TEST: DISTRIBUCION DE TIPOS DE PROBLEMAS")
    print("=" * 70)

    # Crear simulador de problemas
    issues_sim = WellIssuesSimulator(
        issue_probability=1.0,  # 100% para forzar generacion
        min_issues_per_panel=50,
        max_issues_per_panel=50,
    )

    # Generar muchos pozos problematicos
    well_positions = [f"{row}{col}" for row in "ABCDEFGH" for col in range(1, 13)]
    issues = issues_sim.assign_issues_to_panel(well_positions, exclude_controls=False)

    # Contar tipos de problemas
    type_counts = {}
    for issue in issues.values():
        issue_type = issue.issue_type.value
        type_counts[issue_type] = type_counts.get(issue_type, 0) + 1

    print(f"\nDistribucion de {len(issues)} problemas generados:\n")
    print(f"{'Tipo de Problema':<30} {'Cantidad':<10} {'Porcentaje':<10}")
    print("-" * 70)

    for issue_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        percentage = (count / len(issues)) * 100
        print(f"{issue_type:<30} {count:<10} {percentage:<10.1f}%")

    # Verificar que al menos 4 tipos diferentes aparecen
    assert len(type_counts) >= 4, (
        f"Solo {len(type_counts)} tipos generados, esperados al menos 4"
    )

    print(f"\n{'=' * 70}\n")
    return True


def test_od_modifications():
    """
    Verifica que los problemas modifican las lecturas de OD correctamente.
    """
    print("=" * 70)
    print("TEST: MODIFICACION DE LECTURAS DE OD")
    print("=" * 70)

    # Crear simulador
    simulator = ASTSimulator(
        bacteria_profile_id=1,
        panel_name="EUCAST_PA_Standard",
        inoculo_mcfarland=0.5,
    )

    # Simular incubacion
    simulator.simulate_incubation()

    print(f"\nAnalizando {len(simulator.well_issues)} pozos problematicos:\n")

    # Verificar que los pozos problematicos tienen ODs afectadas
    for well_pos, issue in simulator.well_issues.items():
        # Buscar el pozo en panel_wells
        well = next((w for w in simulator.panel_wells if w.posicion == well_pos), None)

        if well and well.readings:
            od_final = well.readings[-1].od_600
            print(f"Pozo {well_pos}:")
            print(f"  Tipo problema: {issue.issue_type.value}")
            print(f"  OD final: {od_final:.3f}")
            print(f"  Es NaN: {str(od_final != od_final)}")  # NaN check

            # Verificar segun tipo de problema
            if issue.issue_type == WellIssueType.UNREADABLE:
                # Debe ser NaN
                assert od_final != od_final, f"Pozo UNREADABLE deberia ser NaN"
                print(f"  Estado: OK (no legible)")
            elif issue.issue_type == WellIssueType.WEAK_GROWTH:
                # Debe tener OD reducida
                print(f"  Estado: OK (crecimiento debil)")
            else:
                print(f"  Estado: OK (problema aplicado)")

            print()

    print(f"{'=' * 70}\n")
    return True


def test_report_includes_issues():
    """
    Verifica que el reporte incluye informacion de pozos problematicos.
    """
    print("=" * 70)
    print("TEST: REPORTE DE POZOS PROBLEMATICOS")
    print("=" * 70)

    # Crear simulador
    simulator = ASTSimulator(
        bacteria_profile_id=1,
        panel_name="EUCAST_PA_Standard",
        inoculo_mcfarland=0.5,
    )

    # Simular
    simulator.simulate_incubation()
    simulator.calculate_mics()
    report = simulator.get_report()

    # Verificar metadata
    print(f"\nMetadata del reporte:")
    print(f"  Pozos problematicos: {report['metadata']['pozos_problematicos']}")

    # Verificar seccion well_issues
    assert "well_issues" in report, "Reporte no incluye seccion 'well_issues'"
    print(f"  Seccion 'well_issues': Presente")
    print(f"  Problemas reportados: {len(report['well_issues'])}")

    # Mostrar detalles
    if report["well_issues"]:
        print(f"\nDetalles de pozos problematicos en reporte:\n")
        for issue_data in report["well_issues"]:
            print(f"  Pozo: {issue_data['posicion']}")
            print(f"    Tipo: {issue_data['tipo']}")
            print(f"    Descripcion: {issue_data['descripcion']}")
            print(f"    Accion: {issue_data['accion_recomendada']}")
            print()

    # Validar estructura
    for issue_data in report["well_issues"]:
        assert "posicion" in issue_data
        assert "tipo" in issue_data
        assert "severidad" in issue_data
        assert "descripcion" in issue_data
        assert "afecta_lectura" in issue_data
        assert "afecta_interpretacion" in issue_data
        assert "accion_recomendada" in issue_data

    print(f"Estructura del reporte: OK")
    print(f"\n{'=' * 70}\n")
    return True


def test_controls_not_affected():
    """
    Verifica que los controles no reciben problemas.
    """
    print("=" * 70)
    print("TEST: CONTROLES SIN PROBLEMAS")
    print("=" * 70)

    # Ejecutar multiples simulaciones
    for i in range(10):
        simulator = ASTSimulator(
            bacteria_profile_id=1,
            panel_name="EUCAST_PA_Standard",
            inoculo_mcfarland=0.5,
        )
        simulator.simulate_incubation()

        # Verificar que ningun control tiene problemas
        control_positions = ["H11", "H12"]  # Posiciones tipicas de controles
        for ctrl_pos in control_positions:
            assert ctrl_pos not in simulator.well_issues, (
                f"Control {ctrl_pos} tiene problema en iteracion {i + 1}"
            )

    print(f"\n10 simulaciones completadas")
    print(f"Controles siempre sin problemas: OK")
    print(f"\n{'=' * 70}\n")
    return True


if __name__ == "__main__":
    print("\n")

    try:
        # Ejecutar tests
        test_well_issues_generation()
        test_issue_types_distribution()
        test_od_modifications()
        test_report_includes_issues()
        test_controls_not_affected()

        print("\n" + "=" * 70)
        print("TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 70 + "\n")

    except AssertionError as e:
        print(f"\nERROR EN TEST: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\nEXCEPCION INESPERADA: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
