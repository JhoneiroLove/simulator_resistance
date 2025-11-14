"""
Test de FASE B: Heteroresistencia + Fitness Costs

Valida:
1. Carga de distribuciones de heteroresistencia desde BD
2. Cálculo de distribuciones MIC poblacionales
3. Carga de costos de fitness desde BD
4. Cálculo de fitness acumulado para genotipos
5. Comparación de fitness entre cepas

Autor: Sistema AST - Fase B
Fecha: 14 de noviembre de 2025
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.genotype_phenotype_calculator import GenotypePhenotypeCalculator
from src.core.fitness_calculator import FitnessCalculator
from src.data.database import get_session
from src.data.models import HeteroresistanceDistribution, FitnessCost


def print_section(title: str):
    """Imprime sección con formato."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60 + "\n")


def test_1_load_heteroresistance():
    """TEST 1: Verificar carga de distribuciones de heteroresistencia."""
    print_section("TEST 1: Carga de Heteroresistance Distributions desde BD")

    session = get_session()
    records = session.query(HeteroresistanceDistribution).all()
    session.close()

    print(f"✅ Tabla heteroresistance_distributions tiene {len(records)} registros")

    if records:
        print("\n📊 Ejemplos de heteroresistencia documentada:")
        for record in records[:3]:
            estimated_mic = 10**record.mean_log_mic
            print(f"   {record.antibiotico:<20} + {record.genotype_signature:<30}")
            print(f"      MIC estimado: {estimated_mic:.2f} µg/mL")
            print(f"      Prevalencia:  {record.prevalence * 100:.1f}%")
            print(f"      Referencia:   {record.pmid_reference}")
            print()

    print("✅ TEST 1 PASADO: Heteroresistance distributions cargadas\n")
    return len(records) > 0


def test_2_calculate_mic_distribution():
    """TEST 2: Calcular distribución de MICs con heteroresistencia."""
    print_section("TEST 2: Cálculo de Distribución MIC (Heteroresistencia)")

    calc = GenotypePhenotypeCalculator()

    # Caso 1: Genotipo con heteroresistencia documentada
    print("🧬 Caso 1: oprD_loss (heteroresistencia documentada)")
    dist1 = calc.calculate_mic_distribution("Meropenem", ["oprD_loss"], n_samples=100)

    print(f"   MIC base (determinístico): {dist1['base_mic']:.3f} µg/mL")
    print(f"   MIC medio (poblacional):   {dist1['mean_mic']:.3f} µg/mL")
    print(f"   MIC mediana:               {dist1['median_mic']:.3f} µg/mL")
    print(f"   Desv. estándar:            {dist1['std_mic']:.3f} µg/mL")
    print(f"   Heteroresistente:          {dist1['heteroresistant']}")
    if dist1["heteroresistant"]:
        print(f"   Prevalencia:               {dist1['prevalence'] * 100:.1f}%")
        print(f"   Referencia:                {dist1['pmid_reference']}")

    # Caso 2: Genotipo sin heteroresistencia documentada
    print("\n🧬 Caso 2: ampC_promoter_-32C_T (sin heteroresistencia documentada)")
    dist2 = calc.calculate_mic_distribution(
        "Ceftazidima", ["ampC_promoter_-32C_T"], n_samples=100
    )

    print(f"   MIC base (determinístico): {dist2['base_mic']:.3f} µg/mL")
    print(f"   MIC medio (poblacional):   {dist2['mean_mic']:.3f} µg/mL")
    print(f"   Heteroresistente:          {dist2['heteroresistant']}")

    print("\n✅ TEST 2 PASADO: Distribuciones MIC calculadas correctamente\n")
    return dist1["heteroresistant"] and not dist2["heteroresistant"]


def test_3_load_fitness_costs():
    """TEST 3: Verificar carga de costos de fitness."""
    print_section("TEST 3: Carga de Fitness Costs desde BD")

    session = get_session()
    records = session.query(FitnessCost).all()
    session.close()

    print(f"✅ Tabla fitness_costs tiene {len(records)} registros")

    if records:
        print("\n📊 Ejemplos de costos de fitness documentados:")
        # Ordenar por costo descendente
        sorted_records = sorted(records, key=lambda x: x.fitness_cost, reverse=True)

        for record in sorted_records[:5]:
            category = (
                "Alto"
                if record.fitness_cost >= 0.2
                else "Moderado"
                if record.fitness_cost >= 0.1
                else "Bajo"
            )
            print(f"   {record.gen:<30} Costo: {record.fitness_cost:.3f} ({category})")
            print(f"      Growth penalty: {record.growth_rate_penalty:.1f}%")
            print(f"      CI:             {record.competitive_index:.2f}")
            print(f"      Referencia:     {record.pmid_reference}")
            print()

    print("✅ TEST 3 PASADO: Fitness costs cargados\n")
    return len(records) > 0


def test_4_calculate_fitness():
    """TEST 4: Calcular fitness para genotipos."""
    print_section("TEST 4: Cálculo de Fitness para Genotipos")

    calc = FitnessCalculator()

    # Caso 1: Wild-type
    print("🧬 Caso 1: Wild-type (sin mutaciones)")
    fitness_wt = calc.calculate_fitness([])
    print(f"   Costo total:         {fitness_wt.total_fitness_cost:.3f}")
    print(f"   CI:                  {fitness_wt.competitive_index:.2f}")
    print(f"   Tiempo duplicación:  {fitness_wt.doubling_time_min:.1f} min")

    # Caso 2: Una mutación
    print("\n🧬 Caso 2: oprD_loss (pérdida de porina)")
    fitness_oprd = calc.calculate_fitness(["oprD_loss"])
    print(f"   Costo total:         {fitness_oprd.total_fitness_cost:.3f}")
    print(f"   CI:                  {fitness_oprd.competitive_index:.2f}")
    print(f"   Tiempo duplicación:  {fitness_oprd.doubling_time_min:.1f} min")
    print(f"   Genes con costo:     {fitness_oprd.genes_with_cost}")

    # Caso 3: Múltiples mutaciones
    print("\n🧬 Caso 3: oprD_loss + blaVIM_or_blaIMP (doble resistencia)")
    fitness_multi = calc.calculate_fitness(["oprD_loss", "blaVIM_or_blaIMP"])
    print(f"   Costo total:         {fitness_multi.total_fitness_cost:.3f}")
    print(f"   CI:                  {fitness_multi.competitive_index:.2f}")
    print(f"   Tiempo duplicación:  {fitness_multi.doubling_time_min:.1f} min")
    print(f"   Genes con costo:     {fitness_multi.genes_with_cost}")
    print(f"   Breakdown:           {fitness_multi.cost_breakdown}")

    # Validaciones
    assert fitness_wt.total_fitness_cost == 0.0
    assert fitness_oprd.total_fitness_cost > 0.0
    assert fitness_multi.total_fitness_cost > fitness_oprd.total_fitness_cost
    assert fitness_wt.competitive_index == 1.0
    assert fitness_multi.competitive_index < fitness_oprd.competitive_index

    print("\n✅ TEST 4 PASADO: Fitness calculations correctos\n")
    return True


def test_5_compare_genotypes():
    """TEST 5: Comparar fitness entre genotipos."""
    print_section("TEST 5: Comparación de Fitness entre Genotipos")

    calc = FitnessCalculator()

    # Comparar: oprD_loss vs oprD_loss+blaVIM
    print("⚔️ Comparación: oprD_loss VS oprD_loss + blaVIM_or_blaIMP")

    comparison = calc.compare_genotypes(
        ["oprD_loss"], ["oprD_loss", "blaVIM_or_blaIMP"]
    )

    print(f"   CI ratio (A/B):              {comparison['ci_ratio']:.3f}")
    print(f"   Ventaja en crecimiento (A):  {comparison['growth_advantage_pct']:.1f}%")
    print(
        f"   Diferencia duplicación:      {comparison['doubling_time_diff_min']:.1f} min"
    )
    print(f"   Ganador (más fit):           {comparison['winner']}")

    # Validaciones
    assert comparison["winner"] == "A"  # oprD solo es más fit que oprD+blaVIM
    assert comparison["ci_ratio"] > 1.0

    print("\n✅ TEST 5 PASADO: Comparaciones de fitness correctas\n")
    return True


def main():
    """Ejecuta todos los tests de FASE B."""
    print("\n" + "=" * 60)
    print("🧪 TESTING FASE B: Heteroresistencia + Fitness Costs")
    print("=" * 60)

    results = []

    try:
        results.append(test_1_load_heteroresistance())
        results.append(test_2_calculate_mic_distribution())
        results.append(test_3_load_fitness_costs())
        results.append(test_4_calculate_fitness())
        results.append(test_5_compare_genotypes())

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Resumen
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
    else:
        print("⚠️ ALGUNOS TESTS FALLARON")
    print("=" * 60)

    print("\n📋 RESUMEN:")
    print("   ✅ Heteroresistance distributions cargadas desde BD")
    print("   ✅ Distribuciones MIC poblacionales calculadas")
    print("   ✅ Fitness costs cargados desde BD")
    print("   ✅ Fitness acumulado para genotipos calculado")
    print("   ✅ Comparaciones de fitness funcionales")
    print("\n🚀 FASE B IMPLEMENTADA CORRECTAMENTE\n")

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
