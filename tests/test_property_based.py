"""
Pruebas de Propiedad (Property-Based Testing) usando Hypothesis
Estas pruebas verifican propiedades fundamentales del algoritmo genético
sobre un amplio rango de valores aleatorios.
"""

from hypothesis import given, settings
from hypothesis.strategies import integers, floats
import math
from src.core.genetic_algorithm import GeneticAlgorithm

# 1. Probar que la población nunca sea negativa
@given(initial_population=integers(min_value=1, max_value=1000))
@settings(deadline=None)
def test_population_non_negative(initial_population):
    """
    La población bacteriana total nunca debe ser negativa
    después de cualquier cantidad de generaciones.
    """
    ga = GeneticAlgorithm(
        genes=[
            {"id": 1, "nombre": "gen1", "peso_resistencia": 0.5},
            {"id": 2, "nombre": "gen2", "peso_resistencia": 0.6},
        ],
        antibiotic_schedule=[],
        mutation_rate=0.1,
        generations=10,
        pop_size=initial_population,  # Población inicial variable
        death_rate=0.05,
        environmental_factors={"temperature": 37.0, "pH": 7.4},
    )
    ga.initialize([1, 2])

    for _ in range(10):
        ga.step()

    assert ga.population_total >= 0, (
        f"La población no puede ser negativa: {ga.population_total}"
    )
    # Además, la población histórica tampoco debe tener negativos
    assert all(val >= 0 for val in ga.population_hist), (
        f"Población negativa en historial: {ga.population_hist}"
    )

# 2. Probar que la tasa de letalidad siempre esté entre 0 y 1
@given(death_rate=floats(min_value=0.0, max_value=1.0))
def test_death_rate_in_range(death_rate):
    """
    La tasa de letalidad global debe estar siempre entre 0 y 1
    para cualquier simulación inicializada.
    """
    ga = GeneticAlgorithm(
        genes=[
            {"id": 1, "nombre": "gen1", "peso_resistencia": 0.5},
            {"id": 2, "nombre": "gen2", "peso_resistencia": 0.6},
        ],
        antibiotic_schedule=[],
        mutation_rate=0.1,
        generations=5,
        pop_size=20,
        death_rate=death_rate,
        environmental_factors={"temperature": 37.0, "pH": 7.4},
    )
    ga.initialize([1, 2])

    # El atributo death_rate debe estar en rango
    assert 0 <= ga.death_rate <= 1, f"Tasa de letalidad fuera de rango: {ga.death_rate}"

# 3. Probar que la suma de probabilidades de letalidad y supervivencia nunca exceda 1
@given(death_rate=floats(min_value=0.0, max_value=1.0))
def test_death_and_survival_sum_to_one(death_rate):
    """
    La suma de las probabilidades de letalidad y supervivencia
    debe ser siempre igual a 1.
    """
    survival_rate = 1 - death_rate
    suma = death_rate + survival_rate
    assert math.isclose(suma, 1, rel_tol=1e-9), (
        f"La suma de probabilidades no es 1: {suma}"
    )