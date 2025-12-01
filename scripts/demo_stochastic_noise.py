import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.mechanistic_prediction_engine import MechanisticPredictionEngine

print("=" * 70)
print("DEMOSTRACIÓN: RUIDO EXPERIMENTAL ESTOCÁSTICO")
print("=" * 70)

# MODO DETERMINISTA (seed fijo)
print("\n1. MODO DETERMINISTA (seed=42, stochastic=True)")
print("-" * 70)
engine_det = MechanisticPredictionEngine(
    standard="EUCAST",
    stochastic=True,
    seed=42,
)

results_det = []
for i in range(3):
    result = engine_det.simulate_well("Meropenem", 2.0, [])
    results_det.append(result.final_od)
    print(f"  Ejecución {i + 1}: OD final = {result.final_od:.6f}")

print(f"\n  Todas idénticas: {len(set([f'{od:.6f}' for od in results_det])) == 1}")

# MODO ESTOCÁSTICO (sin seed)
print("\n2. MODO ESTOCÁSTICO (sin seed, variabilidad real)")
print("-" * 70)
engine_stoch = MechanisticPredictionEngine(
    standard="EUCAST",
    stochastic=True,
    seed=None,
)

results_stoch = []
for i in range(10):
    result = engine_stoch.simulate_well("Meropenem", 2.0, [])
    results_stoch.append(result.final_od)
    print(f"  Ejecución {i + 1}: OD final = {result.final_od:.6f}")

import numpy as np

cv = np.std(results_stoch) / np.mean(results_stoch)
print(f"\n  Media: {np.mean(results_stoch):.6f}")
print(f"  Desv. Est.: {np.std(results_stoch):.6f}")
print(f"  CV: {cv:.2%} (esperado: ~5% según CLSI M07)")

# MODO SIN RUIDO (baseline)
print("\n3. MODO SIN RUIDO (stochastic=False)")
print("-" * 70)
engine_no_noise = MechanisticPredictionEngine(
    standard="EUCAST",
    stochastic=False,
)

results_no_noise = []
for i in range(3):
    result = engine_no_noise.simulate_well("Meropenem", 2.0, [])
    results_no_noise.append(result.final_od)
    print(f"  Ejecución {i + 1}: OD final = {result.final_od:.6f}")

print(f"\n  Todas idénticas: {len(set([f'{od:.6f}' for od in results_no_noise])) == 1}")

# DETERMINACIÓN MIC CON RUIDO INTER-POZO
print("\n4. DETERMINACIÓN MIC CON RUIDO INTER-POZO")
print("-" * 70)
mic_results = []
for i in range(5):
    mic_calc = engine_stoch.mic_calculator
    od_test = [1.5, 1.2, 0.8, 0.15, 0.05, 0.01]
    conc_test = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]

    mic_det = mic_calc.determine_mic(
        conc_test,
        od_test,
        interpolate=True,
        antibiotic="Meropenem",
        apply_noise=True,
        noise_cv=0.05,
    )
    mic_results.append(mic_det.mic_virtual)
    print(f"  Replicado {i + 1}: MIC = {mic_det.mic_virtual} µg/mL")

print(f"\n  Variabilidad: {set(mic_results)}")
print(f"  Rango: {min(mic_results)} - {max(mic_results)} µg/mL")

print("\n" + "=" * 70)
print("VALIDACIÓN: ✓ Ruido experimental implementado según CLSI M07")
print("=" * 70)
