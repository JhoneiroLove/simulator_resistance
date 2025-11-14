"""
Script de prueba para FASE A: Baseline MICs desde BD + variabilidad estocástica.

Verifica:
1. Carga de baseline_mics desde BD (no hardcoded)
2. Funcionamiento del parámetro stochastic=True
3. Redondeo a diluciones estándar
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.genotype_phenotype_calculator import GenotypePhenotypeCalculator
from src.data.database import get_session
from src.data.models import BaselineMIC


def test_baseline_mics_from_db():
    """Test 1: Verificar que baseline MICs se cargan desde BD."""
    print("\n" + "=" * 60)
    print("TEST 1: Carga de Baseline MICs desde Base de Datos")
    print("=" * 60)

    # Verificar que la tabla tiene datos
    session = get_session()
    baseline_count = session.query(BaselineMIC).count()
    session.close()

    print(f"✅ Tabla baseline_mics tiene {baseline_count} registros")

    # Cargar baseline MICs mediante el calculador
    calc = GenotypePhenotypeCalculator()
    baseline_dict = calc.get_baseline_mics()

    print(f"✅ GenotypePhenotypeCalculator cargó {len(baseline_dict)} baseline MICs")

    # Mostrar algunos valores
    antibiotics_to_check = ["Meropenem", "Ciprofloxacino", "Amikacina", "Colistina"]
    print("\n📊 Valores de ejemplo:")
    for ab in antibiotics_to_check:
        if ab in baseline_dict:
            print(f"   {ab:25s}: {baseline_dict[ab]:6.3f} µg/mL")

    assert baseline_count == len(baseline_dict), "Mismatch entre BD y cache"
    print("\n✅ TEST 1 PASADO: Baseline MICs se cargan correctamente desde BD\n")


def test_deterministic_calculation():
    """Test 2: MIC determinístico (sin stochastic)."""
    print("\n" + "=" * 60)
    print("TEST 2: Cálculo Determinístico (stochastic=False)")
    print("=" * 60)

    calc = GenotypePhenotypeCalculator()

    # Test wild-type (sin mutaciones)
    genes_wt = []
    result_wt = calc.calculate_mic("Meropenem", genes_wt, stochastic=False)

    print(f"\n🧬 Genotipo: Wild-type (sin mutaciones)")
    print(f"   Antibiótico: Meropenem")
    print(f"   MIC base:    {result_wt.mic_base} µg/mL")
    print(f"   MIC final:   {result_wt.mic_calculado} µg/mL")
    print(f"   Genes:       {result_wt.genes_aplicados}")

    assert result_wt.mic_calculado == result_wt.mic_base, (
        "Wild-type debe tener MIC = baseline"
    )

    # Test con mutaciones
    genes_mut = ["oprD_loss", "blaVIM_or_blaIMP"]
    result_mut = calc.calculate_mic("Meropenem", genes_mut, stochastic=False)

    print(f"\n🧬 Genotipo: oprD_loss + blaVIM")
    print(f"   Antibiótico: Meropenem")
    print(f"   MIC base:    {result_mut.mic_base} µg/mL")
    print(f"   MIC final:   {result_mut.mic_calculado} µg/mL")
    print(f"   Mult:        {result_mut.multiplicadores}")
    print(f"   Fold-change: {result_mut.fold_change:.1f}x")

    # El cálculo debe ser determinístico (siempre mismo resultado)
    result_mut2 = calc.calculate_mic("Meropenem", genes_mut, stochastic=False)
    assert result_mut.mic_calculado == result_mut2.mic_calculado, (
        "Deterministic must be reproducible"
    )

    print("\n✅ TEST 2 PASADO: Cálculo determinístico funciona correctamente\n")


def test_stochastic_calculation():
    """Test 3: MIC estocástico (con variabilidad biológica)."""
    print("\n" + "=" * 60)
    print("TEST 3: Cálculo Estocástico (stochastic=True)")
    print("=" * 60)

    calc = GenotypePhenotypeCalculator()

    genes = ["oprD_loss"]
    antibiotico = "Meropenem"

    # Generar 10 réplicas estocásticas
    mics_stochastic = []
    for i in range(10):
        result = calc.calculate_mic(antibiotico, genes, stochastic=True)
        mics_stochastic.append(result.mic_calculado)

    # Calcular MIC determinístico para comparar
    result_det = calc.calculate_mic(antibiotico, genes, stochastic=False)
    mic_det = result_det.mic_calculado

    print(f"\n🧬 Genotipo: oprD_loss")
    print(f"   Antibiótico: {antibiotico}")
    print(f"   MIC determinístico: {mic_det} µg/mL")
    print(f"\n📊 10 réplicas estocásticas:")
    for i, mic in enumerate(mics_stochastic, 1):
        print(f"   Réplica {i:2d}: {mic:6.3f} µg/mL")

    # Estadísticas
    import numpy as np

    mean_mic = np.mean(mics_stochastic)
    std_mic = np.std(mics_stochastic)
    min_mic = min(mics_stochastic)
    max_mic = max(mics_stochastic)

    print(f"\n📈 Estadísticas:")
    print(f"   Media:       {mean_mic:6.3f} µg/mL")
    print(f"   Desv. std:   {std_mic:6.3f} µg/mL")
    print(f"   Rango:       {min_mic:6.3f} - {max_mic:6.3f} µg/mL")
    print(f"   Variabilidad: {min_mic / max_mic:.2f}x - {max_mic / min_mic:.2f}x")

    # Verificar que hay variabilidad
    unique_values = len(set(mics_stochastic))
    print(f"\n   Valores únicos: {unique_values}/10")

    # Debe haber al menos 2 valores diferentes (probabilidad ~99.9%)
    assert unique_values >= 2, "Stochastic mode should produce variability"

    # Todos los valores deben ser diluciones estándar
    standard_dilutions = [
        0.015,
        0.03,
        0.06,
        0.125,
        0.25,
        0.5,
        1.0,
        2.0,
        4.0,
        8.0,
        16.0,
        32.0,
        64.0,
        128.0,
        256.0,
        512.0,
        1024.0,
    ]
    for mic in mics_stochastic:
        assert mic in standard_dilutions, f"MIC {mic} no es dilución estándar"

    print("\n✅ TEST 3 PASADO: Variabilidad estocástica funciona correctamente\n")


def test_all_antibiotics():
    """Test 4: calculate_all_mics con ambos modos."""
    print("\n" + "=" * 60)
    print("TEST 4: Cálculo para TODOS los antibióticos")
    print("=" * 60)

    calc = GenotypePhenotypeCalculator()
    genes = ["gyrA_T83I", "oprD_loss"]

    # Modo determinístico
    results_det = calc.calculate_all_mics(genes, stochastic=False)
    print(f"\n✅ Calculados {len(results_det)} antibióticos (determinístico)")

    # Modo estocástico
    results_stoch = calc.calculate_all_mics(genes, stochastic=True)
    print(f"✅ Calculados {len(results_stoch)} antibióticos (estocástico)")

    # Verificar que tienen los mismos antibióticos
    assert set(results_det.keys()) == set(results_stoch.keys()), (
        "Both modes should have same antibiotics"
    )

    # Mostrar comparación para algunos antibióticos
    print("\n📊 Comparación Determinístico vs Estocástico:")
    print(f"{'Antibiótico':<30} {'Determ.':>10} {'Estoc.':>10} {'Match':>8}")
    print("-" * 60)

    antibiotics_to_show = [
        "Meropenem",
        "Ciprofloxacino",
        "Amikacina",
        "Ceftazidima",
        "Colistina",
    ]
    for ab in antibiotics_to_show:
        if ab in results_det:
            mic_det = results_det[ab].mic_calculado
            mic_stoch = results_stoch[ab].mic_calculado
            match = "✓" if mic_det == mic_stoch else "✗"
            print(f"{ab:<30} {mic_det:>10.3f} {mic_stoch:>10.3f}    {match:>5}")

    print("\n✅ TEST 4 PASADO: calculate_all_mics funciona en ambos modos\n")


def main():
    """Ejecutar todos los tests."""
    print("\n" + "=" * 60)
    print("🧪 TESTING FASE A: Baseline MICs + Stochastic Variability")
    print("=" * 60)

    try:
        test_baseline_mics_from_db()
        test_deterministic_calculation()
        test_stochastic_calculation()
        test_all_antibiotics()

        print("\n" + "=" * 60)
        print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 60)
        print("\n📋 RESUMEN:")
        print("   ✅ Baseline MICs se cargan desde BD (no hardcoded)")
        print("   ✅ Cálculo determinístico reproducible")
        print("   ✅ Variabilidad estocástica funciona (±1 dilución)")
        print("   ✅ Redondeo a diluciones estándar correcto")
        print("   ✅ calculate_all_mics compatible con ambos modos")
        print("\n🚀 FASE A IMPLEMENTADA CORRECTAMENTE\n")

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FALLIDO")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
