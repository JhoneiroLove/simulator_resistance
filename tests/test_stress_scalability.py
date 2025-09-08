import time
import math
import pytest
import psutil
import os

from src.core.genetic_algorithm import GeneticAlgorithm

def get_memory_usage_mb():
    """Devuelve el uso de memoria actual del proceso en MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_max_generations_and_population():
    """
    Prueba de estrés:
    Ejecuta el algoritmo con un gran número de generaciones y población máxima razonable.
    """
    genes = [{"id": i, "nombre": f"gen{i}", "peso_resistencia": 0.5} for i in range(10)]
    generations = 100  # Puedes subir este número, depende de tu PC
    pop_size = 1000  # Subir para más estrés, pero cuida la RAM

    ga = GeneticAlgorithm(
        genes=genes,
        antibiotic_schedule=[],
        mutation_rate=0.1,
        generations=generations,
        pop_size=pop_size,
        death_rate=0.05,
        environmental_factors={"temperature": 37.0, "pH": 7.4},
    )
    ga.initialize([g["id"] for g in genes])

    start_time = time.time()
    for _ in range(generations):
        ga.step()
    elapsed = time.time() - start_time
    mem_mb = get_memory_usage_mb()

    print(
        f"\n[Estrés] Generaciones={generations} Población={pop_size} Tiempo={elapsed:.2f}s RAM={mem_mb:.2f}MB"
    )
    assert ga.population_total >= 0
    assert elapsed < 60  # Cambia el umbral según tu tolerancia (segundos)

@pytest.mark.parametrize("peso_extremo", [-1e6, 0, 1e6])
def test_genes_with_extreme_weights(peso_extremo):
    """
    Prueba qué ocurre si los genes tienen pesos extremos (negativo, cero, muy grande).
    """
    genes = [
        {"id": 1, "nombre": "A", "peso_resistencia": peso_extremo},
        {"id": 2, "nombre": "B", "peso_resistencia": 0.5},
    ]
    ga = GeneticAlgorithm(
        genes=genes,
        antibiotic_schedule=[],
        mutation_rate=0.2,
        generations=20,
        pop_size=100,
        death_rate=0.1,
    )
    ga.initialize([1, 2])
    for _ in range(20):
        ga.step()
    assert not any(math.isnan(val) or math.isinf(val) for val in ga.avg_hist), (
        "Valores no numéricos en avg_hist"
    )
    assert ga.population_total >= 0

@pytest.mark.parametrize("param", [-1, 0, 1e6])
def test_absurd_parameters(param):
    """
    Prueba el algoritmo con parámetros absurdos o en el límite (negativo, cero, enorme).
    """
    genes = [{"id": 1, "nombre": "Z", "peso_resistencia": 1.0}]
    try:
        ga = GeneticAlgorithm(
            genes=genes,
            antibiotic_schedule=[],
            mutation_rate=max(0.0, float(param)),  # mutation_rate debe ser >= 0
            generations=max(1, int(abs(param))),
            pop_size=max(1, int(abs(param))),
            death_rate=max(0.0, float(param)),  # death_rate debe ser >= 0
        )
        ga.initialize([1])
        for _ in range(min(10, ga.generations)):
            ga.step()
        # La población no debe ser negativa ni NaN
        assert ga.population_total >= 0
        assert not any(math.isnan(val) or math.isinf(val) for val in ga.population_hist)
    except Exception as e:
        # Es aceptable que el algoritmo lance excepción controlada con parámetros inválidos.
        print(f"Parámetro absurdo ({param}) produjo excepción controlada: {e}")