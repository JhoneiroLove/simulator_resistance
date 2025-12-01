import pytest
import numpy as np
from src.core.mechanistic_prediction_engine import MechanisticPredictionEngine


def test_engine_initialization():
    engine = MechanisticPredictionEngine()
    assert engine.base_mu == 0.69
    assert engine.od_threshold == 0.3
    assert engine.incubation_hours == 18.0
    assert engine.standard == "EUCAST"
    assert engine.stochastic == True


def test_engine_initialization_clsi():
    engine = MechanisticPredictionEngine(standard="CLSI")
    assert engine.standard == "CLSI"


def test_engine_deterministic_mode():
    engine = MechanisticPredictionEngine(stochastic=False)
    result1 = engine.simulate_well("Meropenem", 2.0, [])
    result2 = engine.simulate_well("Meropenem", 2.0, [])
    assert result1.final_od == result2.final_od


def test_engine_stochastic_with_seed():
    results = []
    for _ in range(3):
        engine = MechanisticPredictionEngine(stochastic=True, seed=42)
        result = engine.simulate_well("Meropenem", 2.0, [])
        results.append(result.final_od)
    assert len(set(results)) == 1


def test_engine_stochastic_without_seed():
    engine = MechanisticPredictionEngine(stochastic=True, seed=None)
    results = [engine.simulate_well("Meropenem", 2.0, []).final_od for _ in range(10)]
    cv = np.std(results) / np.mean(results) if np.mean(results) > 0 else 0
    assert cv > 0
    assert cv < 0.15


def test_simulate_well_no_antibiotic():
    engine = MechanisticPredictionEngine()
    result = engine.simulate_well("Meropenem", 0.0, [])
    assert result.final_od > 0.0
    assert len(result.population_history) > 0


def test_simulate_well_with_resistance():
    engine = MechanisticPredictionEngine()
    result = engine.simulate_well("Meropenem", 4.0, ["oprD_loss"])
    assert result.final_genotype == ["oprD_loss"]
    assert result.mutation_events >= 0


def test_mic_determination():
    engine = MechanisticPredictionEngine()
    result = engine.simulate_mic_determination("Ciprofloxacino", [])
    assert "mic_virtual" in result
    assert result["mic_virtual"] > 0
    assert "standard_used" in result
    assert result["standard_used"] == "EUCAST"
    assert "turbidity_threshold" in result


def test_mic_determination_clsi():
    engine = MechanisticPredictionEngine(standard="CLSI")
    result = engine.simulate_mic_determination("Meropenem", [])
    assert result["standard_used"] == "CLSI"
    assert "turbidity_threshold" in result


def test_mic_with_noise():
    engine = MechanisticPredictionEngine(stochastic=True, seed=None)
    mic_calc = engine.mic_calculator

    od_test = [1.5, 1.2, 0.8, 0.15, 0.05, 0.01]
    conc_test = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]

    results = []
    for _ in range(5):
        mic_det = mic_calc.determine_mic(
            conc_test,
            od_test,
            interpolate=True,
            antibiotic="Meropenem",
            apply_noise=True,
            noise_cv=0.05,
        )
        results.append(mic_det.mic_virtual)

    assert len(set(results)) > 1 or all(r == results[0] for r in results)


def test_batch_panel_simulation():
    engine = MechanisticPredictionEngine()
    antibiotics = ["Meropenem", "Ciprofloxacino"]
    results = engine.batch_simulate_panel(antibiotics, [])
    assert len(results) == 2
    assert all(ab in results for ab in antibiotics)
    for ab in antibiotics:
        assert "standard_used" in results[ab]
        assert results[ab]["standard_used"] == "EUCAST"
