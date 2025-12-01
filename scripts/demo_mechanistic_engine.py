import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.mechanistic_prediction_engine import MechanisticPredictionEngine

# UMBRAL EUCAST/CLSI: El engine usa estándar EUCAST para umbrales de turbidez
engine = MechanisticPredictionEngine(
    base_mu=0.69,
    base_K=2e9,
    N0=1e5,
    hill_coefficient=4.0,
    od_threshold=0.3,
    incubation_hours=18.0,
    standard="EUCAST",  # Puede ser "EUCAST" o "CLSI"
)

print("=" * 70)
print("SIMULACIÓN MECANICISTA CON UMBRALES EUCAST/CLSI")
print("=" * 70)
print(f"Estándar utilizado: {engine.standard}\n")

print("Simulación 1: Wild-type vs Meropenem 4 µg/mL")
print("-" * 70)
result_wt = engine.simulate_well("Meropenem", 4.0, [])
print(f"OD final: {result_wt.final_od:.4f}")
print(f"Mutaciones: {result_wt.mutation_events}")
print(f"Genotipo final: {result_wt.final_genotype}")
print(f"MIC virtual: {result_wt.mic_virtual} µg/mL\n")

print("Simulación 2: oprD_loss vs Meropenem 4 µg/mL")
print("-" * 70)
result_mut = engine.simulate_well("Meropenem", 4.0, ["oprD_loss"])
print(f"OD final: {result_mut.final_od:.4f}")
print(f"Mutaciones: {result_mut.mutation_events}")
print(f"Genotipo final: {result_mut.final_genotype}")
print(f"MIC virtual: {result_mut.mic_virtual} µg/mL\n")

print("Simulación 3: Determinación MIC automática para Ciprofloxacino (Wild-type)")
print("-" * 70)
# UMBRAL EUCAST/CLSI: Se obtiene automáticamente del breakpoint de Ciprofloxacino
mic_result = engine.simulate_mic_determination("Ciprofloxacino", [])
print(f"MIC determinado: {mic_result['mic_virtual']} µg/mL")
print(f"Estándar aplicado: {mic_result['standard_used']}")
print(f"Umbral de turbidez usado: OD ≥ {mic_result['turbidity_threshold']:.3f}")
print(
    f"Concentraciones probadas: {[f'{c:.3f}' for c in mic_result['concentrations'][:5]]}..."
)
print(f"Total de concentraciones: {len(mic_result['concentrations'])}")

print("\n" + "=" * 70)
print("COMPARACIÓN DE ESTÁNDARES")
print("=" * 70)

# Comparar EUCAST vs CLSI
engine_clsi = MechanisticPredictionEngine(standard="CLSI")
mic_result_clsi = engine_clsi.simulate_mic_determination("Meropenem", [])

print(f"\nMeropenem (Wild-type):")
print(
    f"  EUCAST: MIC = {engine.simulate_mic_determination('Meropenem', [])['mic_virtual']} µg/mL "
    f"(umbral OD ≥ {engine.simulate_mic_determination('Meropenem', [])['turbidity_threshold']:.3f})"
)
print(
    f"  CLSI:   MIC = {mic_result_clsi['mic_virtual']} µg/mL "
    f"(umbral OD ≥ {mic_result_clsi['turbidity_threshold']:.3f})"
)
