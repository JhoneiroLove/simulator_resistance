import pytest
import numpy as np
from unittest.mock import MagicMock
from src.core.genetic_algorithm import GeneticAlgorithm, BacteriaIndividual, creator

@pytest.fixture
def ga_instance():
    """Fixture para generar una instancia de `GeneticAlgorithm` con configuración estándar."""
    genes = [
        {'id': 1, 'nombre': 'genA', 'peso_resistencia': 0.5, 'costo_adaptativo': 0.1, 'tipo': 'Bomba de eflujo'},
        {'id': 2, 'nombre': 'genB', 'peso_resistencia': 0.3, 'costo_adaptativo': 0.2, 'tipo': 'Modificación de objetivo'},
        {'id': 3, 'nombre': 'genC', 'peso_resistencia': 0.2, 'costo_adaptativo': 0.05, 'tipo': 'Inactivación enzimática'}
    ]

    antibiotic_schedule = [
        (10, {'id': 1, 'nombre': 'AntibioticoX', 'resistencia_gen': 'genA'}, 5.0),
        (30, {'id': 2, 'nombre': 'AntibioticoY', 'resistencia_gen': 'genB'}, 10.0)
    ]

    # Se mockea el `creator` de DEAP para evitar conflictos en ejecuciones repetidas de las pruebas.
    if not hasattr(creator, 'FitnessMax'):
        creator.create("FitnessMax", MagicMock, weights=(1.0,))
    if not hasattr(creator, 'Individual'):
        creator.create("Individual", BacteriaIndividual, fitness=creator.FitnessMax)

    ga = GeneticAlgorithm(
        genes=genes,
        antibiotic_schedule=antibiotic_schedule,
        pop_size=50,
        generations=50
    )
    return ga

def test_bacteria_individual_creation():
    """Verifica la correcta creación y asignación de atributos de un `BacteriaIndividual`."""
    genes_bits = [1, 0, 1]
    recubrimiento = 0.8
    reproduccion = 1.2
    letalidad = 0.1
    permeabilidad = 0.4
    enzimas = 0.9

    b_individual = BacteriaIndividual(
        genes_bits, recubrimiento, reproduccion, letalidad, permeabilidad, enzimas
    )

    assert list(b_individual) == genes_bits
    assert b_individual.recubrimiento == recubrimiento
    assert b_individual.reproduccion == reproduccion
    assert b_individual.letalidad == letalidad
    assert b_individual.permeabilidad == permeabilidad
    assert b_individual.enzimas == enzimas

def test_ga_initialization(ga_instance):
    """Asegura que la clase `GeneticAlgorithm` se inicializa con los parámetros correctos."""
    assert ga_instance.pop_size == 50
    assert ga_instance.generations == 50
    assert len(ga_instance.genes) == 3
    assert ga_instance.total_weight == 1.0

def test_init_individual(ga_instance):
    """Verifica que el método `init_individual` crea un individuo con la estructura esperada."""
    individual = ga_instance.init_individual()
    assert isinstance(individual, BacteriaIndividual)
    assert len(individual) == len(ga_instance.genes)
    assert hasattr(individual, 'recubrimiento')
    assert hasattr(individual, 'reproduccion')
    assert hasattr(individual, 'letalidad')
    assert hasattr(individual, 'permeabilidad')
    assert hasattr(individual, 'enzimas')

def test_update_antibiotic(ga_instance):
    """Valida que el antibiótico activo y su concentración se actualizan según el `antibiotic_schedule`."""
    # Escenario 1: El tiempo es anterior al primer evento del cronograma.
    ga_instance._update_antibiotic(5)
    assert ga_instance.current_ab is None
    assert ga_instance.current_conc == 0.0

    # Escenario 2: El tiempo coincide con el primer evento.
    ga_instance._update_antibiotic(10)
    assert ga_instance.current_ab['nombre'] == 'AntibioticoX'
    assert ga_instance.current_conc == 5.0

    # Escenario 3: El tiempo se encuentra entre dos eventos.
    ga_instance._update_antibiotic(20)
    assert ga_instance.current_ab['nombre'] == 'AntibioticoX'

    # Escenario 4: El tiempo coincide con el segundo evento.
    ga_instance._update_antibiotic(30)
    assert ga_instance.current_ab['nombre'] == 'AntibioticoY'
    assert ga_instance.current_conc == 10.0

    # Escenario 5: El tiempo es posterior a todos los eventos.
    ga_instance._update_antibiotic(100)
    assert ga_instance.current_ab['nombre'] == 'AntibioticoY'

def test_evaluate_no_antibiotic(ga_instance):
    """Comprueba el cálculo de fitness de un individuo cuando no hay un antibiótico activo."""
    # Se define un individuo con un genotipo y atributos específicos.
    individual = BacteriaIndividual([1, 0, 0], 0.5, 1.0, 0.1, 0.5, 0.5)
    ga_instance.current_ab = None
    ga_instance.current_conc = 0.0

    fitness = ga_instance.evaluate(individual)

    # El fitness se calcula manualmente para la validación.
    # raw_resistance = 0.5 (del genA)
    # adaptive_cost = (recubrimiento + enzimas) / 2 = (0.5 + 0.5) / 2 = 0.5
    # N = (0.5 / 1.0) * (1 - 0.5) = 0.25
    # Supervivencia al antibiótico = 1 (no hay)
    # Tasa de muerte = 0.05
    # Fitness final = 0.25 * 1 * (1 - 0.05) = 0.2375
    assert np.isclose(fitness[0], 0.2375)

def test_evaluate_with_antibiotic(ga_instance):
    """Comprueba el cálculo de fitness de un individuo bajo la presión de un antibiótico."""
    individual = BacteriaIndividual([1, 0, 0], 0.5, 1.0, 0.1, 0.5, 0.5)
    ga_instance.current_ab = {
        'nombre': 'AntibioticoX',
        'resistencia_gen': 'genA',
        'concentracion_minima': 2.0,
        'concentracion_maxima': 8.0
    }
    # Se establece una concentración de antibiótico intermedia.
    ga_instance.current_conc = 5.0

    fitness = ga_instance.evaluate(individual)

    # El fitness se calcula manualmente para la validación.
    # raw_resistance = 0.5 (del genA)
    # adaptive_cost = (recubrimiento + enzimas) / 2 = (0.5 + 0.5) / 2 = 0.5
    # N = (0.5 / 1.0) * (1 - 0.5) = 0.25
    # Supervivencia al antibiótico = 1 - (5-2)/(8-2) = 0.5
    # N = 0.25 * 0.5 = 0.125
    # Tasa de muerte = 0.05
    # Fitness final = 0.125 * (1 - 0.05) = 0.11875
    assert np.isclose(fitness[0], 0.11875)

def test_environmental_modifiers(ga_instance):
    """Verifica que los modificadores de crecimiento y muerte responden a cambios en los factores ambientales."""
    # Por defecto, los modificadores deben ser 1.0 (sin efecto).
    assert ga_instance.growth_modifier() == 1.0
    assert ga_instance.death_modifier() == 1.0

    # Una temperatura fuera del rango óptimo debe reducir el crecimiento.
    ga_instance.set_environmental_factor('temperature', 34.0)
    assert np.isclose(ga_instance.growth_modifier(), 0.7)

    # Un pH fuera del rango óptimo debe aumentar la tasa de muerte.
    ga_instance.set_environmental_factor('pH', 6.0)
    assert ga_instance.death_modifier() == 1.2

    # Se restauran las condiciones para confirmar que los modificadores vuelven a 1.0.
    ga_instance.set_environmental_factor('temperature', 37.0)
    ga_instance.set_environmental_factor('pH', 7.4)
    assert ga_instance.growth_modifier() == 1.0
    assert ga_instance.death_modifier() == 1.0


def test_initialize(ga_instance):
    """Asegura que el método `initialize` prepara correctamente la población y los contadores para una simulación."""
    # Se fuerza la activación del gen con ID 2.
    selected_ids = [2]
    ga_instance.initialize(selected_gene_ids=selected_ids)

    assert len(ga_instance.pop) == ga_instance.pop_size
    assert ga_instance.current_step == 0
    assert len(ga_instance.best_hist) == 0
    assert len(ga_instance.population_hist) == 1
    assert ga_instance.population_total == 1e4

    # Se comprueba que el gen forzado está presente en toda la población inicial.
    for ind in ga_instance.pop:
        assert ind[1] == 1

def test_step(ga_instance, mocker):
    """Valida que un único paso (`step`) del algoritmo actualiza el estado de la simulación correctamente."""
    # Se mockea `random.random` para controlar el comportamiento estocástico.
    mocker.patch('src.core.genetic_algorithm.random.random', return_value=1.0)

    ga_instance.initialize(selected_gene_ids=[])
    initial_pop_hist_len = len(ga_instance.population_hist)
    initial_best_hist_len = len(ga_instance.best_hist)

    # Se ejecuta un único paso de la simulación.
    result = ga_instance.step()

    assert result is True
    assert ga_instance.current_step == 1
    assert len(ga_instance.pop) == ga_instance.pop_size
    assert len(ga_instance.population_hist) == initial_pop_hist_len + 1
    assert len(ga_instance.best_hist) == initial_best_hist_len + 1


def test_step_operators_are_called(ga_instance, mocker):
    """Asegura que los operadores genéticos (`select`, `mate`, `mutate`) son invocados durante la ejecución de `step`."""
    ga_instance.initialize(selected_gene_ids=[])

    # Se usan mocks para espiar las llamadas a los operadores de DEAP.
    mock_select = mocker.patch.object(ga_instance.toolbox, 'select', wraps=ga_instance.toolbox.select)
    mock_mate = mocker.patch.object(ga_instance.toolbox, 'mate')
    mock_mutate = mocker.patch.object(ga_instance.toolbox, 'mutate')
    mocker.patch('src.core.genetic_algorithm.random.random', return_value=1.0)

    # Se ejecuta un único paso de la simulación.
    ga_instance.step()

    # Se valida que cada operador fue llamado el número esperado de veces.
    mock_select.assert_called_once()
    assert mock_mate.call_count == ga_instance.pop_size / 2
    assert mock_mutate.call_count == ga_instance.pop_size

def test_step_evolutionary_rescue(ga_instance, mocker):
    """Valida el mecanismo de rescate evolutivo, que debe activarse cuando la diversidad genética es críticamente baja."""
    ga_instance.initialize(selected_gene_ids=[])

    # Se genera una población homogénea para simular una diversidad nula (H=0).
    uniform_pop = [
        creator.Individual([0, 0, 0], 0.5, 0.5, 0.5, 0.5, 0.5)
        for _ in range(ga_instance.pop_size)
    ]
    ga_instance.pop = uniform_pop

    # Se deshabilita la mutación estándar para aislar el efecto del rescate.
    mocker.patch.object(ga_instance.toolbox, 'mutate')

    # Se configura el mock de `random` para que la mutación de rescate se active solo una vez.
    num_bio_mutations = ga_instance.pop_size * 5
    rescue_randoms = [0.01] + [1.0] * (ga_instance.pop_size - 1)
    all_randoms = [1.0] * num_bio_mutations + rescue_randoms
    mocker.patch('src.core.genetic_algorithm.random.random', side_effect=all_randoms)
    # Se configura `randint` para que la mutación afecte a un gen predecible.
    mocker.patch('src.core.genetic_algorithm.random.randint', return_value=0)

    # Se ejecuta un único paso de la simulación.
    ga_instance.step()

    # Se comprueba que el bit del gen esperado fue invertido por el rescate.
    assert ga_instance.pop[0][0] == 1
    # Se asegura que el resto de la población no fue afectado por la mutación de rescate.
    for i in range(1, ga_instance.pop_size):
        assert ga_instance.pop[i][0] == 0
