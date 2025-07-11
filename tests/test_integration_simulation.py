from src.data.database import get_session
from src.data.models import (
    Gen,
    Antibiotico,
    Simulacion,
    ReporteSimulacion,
    MetricaGeneracion,
)
from src.core.genetic_algorithm import GeneticAlgorithm
from src.core.reporting import save_simulation_report, save_generation_metrics
import math

def get_basic_genes():
    session = get_session()
    genes = session.query(Gen).all()
    out = [
        {"id": g.id, "nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
        for g in genes
    ]
    session.close()
    return out


def get_antibiotic_schedule():
    session = get_session()
    ab = session.query(Antibiotico).first()
    session.close()
    return [
        (
            0,
            {
                "id": ab.id,
                "nombre": ab.nombre,
                "tipo": ab.tipo,
                "concentracion_minima": ab.concentracion_minima,
                "concentracion_maxima": ab.concentracion_maxima,
            },
            0.5,
        )
    ]

def test_full_simulation_and_reporting():
    genes = get_basic_genes()
    schedule = get_antibiotic_schedule()
    # Crea simulación
    session = get_session()
    sim = Simulacion(
        antibiotico_id=schedule[0][1]["id"],
        concentracion=schedule[0][2],
        resistencia_predicha=0.0,
    )
    session.add(sim)
    session.commit()
    sim_id = sim.id
    session.close()
    # Ejecuta el algoritmo genético
    ga = GeneticAlgorithm(
        genes=genes,
        antibiotic_schedule=schedule,
        mutation_rate=0.1,
        generations=5,
        pop_size=10,
        death_rate=0.05,
        simulation_id=sim_id,
    )
    ga.initialize([genes[0]["id"], genes[1]["id"]])
    for _ in range(5):
        ga.step()
    ga.save_final_gene_attributes([genes[0]["id"], genes[1]["id"]])

    # Reporting actualizado
    params = {
        "genes": [g["id"] for g in genes],
        "mutation_rate": 0.1,
        "death_rate": 0.05,
        "generations": 5,
        "environmental_factors": {"temperature": 37.0, "pH": 7.4},
    }
    save_simulation_report(ga, params)
    save_generation_metrics(ga, sim_id)

    # Verifica reporte y métricas por generación
    session = get_session()
    reporte = session.query(ReporteSimulacion).filter_by(simulacion_id=sim_id).first()
    assert reporte is not None, "No se creó el reporte de simulación"
    metricas = session.query(MetricaGeneracion).filter_by(simulacion_id=sim_id).all()
    assert metricas, "No se guardaron métricas de la simulación"
    nombres_metricas = set(m.nombre_indicador for m in metricas)
    assert "avg_fitness" in nombres_metricas
    assert "diversidad_genetica" in nombres_metricas
    assert "tasa_convergencia" in nombres_metricas
    session.close()

def test_flujo_completo_simulacion_usuario():
    session = get_session()
    genes = session.query(Gen).all()
    ab = session.query(Antibiotico).first()
    session.close()
    genes_seleccionados = [g.id for g in genes]
    mutation_rate = 0.08
    death_rate = 0.04
    generations = 7
    environmental_factors = {"temperature": 37.0, "pH": 7.4}
    pop_size = 10
    schedule = [
        (
            0,
            {
                "id": ab.id,
                "nombre": ab.nombre,
                "tipo": ab.tipo,
                "concentracion_minima": ab.concentracion_minima,
                "concentracion_maxima": ab.concentracion_maxima,
            },
            0.2,
        ),
        (
            3,
            {
                "id": ab.id,
                "nombre": ab.nombre,
                "tipo": ab.tipo,
                "concentracion_minima": ab.concentracion_minima,
                "concentracion_maxima": ab.concentracion_maxima,
            },
            0.6,
        ),
    ]
    ga = GeneticAlgorithm(
        genes=[
            {"id": g.id, "nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes
        ],
        antibiotic_schedule=schedule,
        mutation_rate=mutation_rate,
        generations=generations,
        pop_size=pop_size,
        death_rate=death_rate,
        environmental_factors=environmental_factors,
    )
    ga.initialize(genes_seleccionados)
    for _ in range(generations):
        ga.step()
    assert len(ga.avg_hist) == generations
    assert len(ga.population_hist) == generations + 1
    assert all(0 <= val <= 1e7 for val in ga.population_hist)
    assert all(0 <= val <= 1.0 for val in ga.avg_hist)
    assert len(ga.expansion_index_hist) == generations + 1
    assert len(ga.degradation_hist) == generations + 1
    assert all(val is not None and not math.isnan(val) for val in ga.avg_hist)
    assert all(val is not None and not math.isnan(val) for val in ga.population_hist)

def test_simulacion_con_id_gen_inexistente():
    session = get_session()
    session.query(Gen).delete()
    session.commit()
    g1 = Gen(nombre="Fake1", peso_resistencia=0.5, descripcion="Fake1")
    g2 = Gen(nombre="Fake2", peso_resistencia=0.7, descripcion="Fake2")
    session.add(g1)
    session.add(g2)
    session.commit()
    ab = session.query(Antibiotico).first()
    g1_id = g1.id
    g2_id = g2.id
    g1_nombre = g1.nombre
    g1_peso = g1.peso_resistencia
    g2_nombre = g2.nombre
    g2_peso = g2.peso_resistencia
    ab_id = ab.id
    ab_nombre = ab.nombre
    ab_tipo = ab.tipo
    ab_conc_min = ab.concentracion_minima
    ab_conc_max = ab.concentracion_maxima
    session.close()
    genes_existentes = [
        {"id": g1_id, "nombre": g1_nombre, "peso_resistencia": g1_peso},
        {"id": g2_id, "nombre": g2_nombre, "peso_resistencia": g2_peso},
    ]
    ids_seleccionados = [9999]
    schedule = [
        (
            0,
            {
                "id": ab_id,
                "nombre": ab_nombre,
                "tipo": ab_tipo,
                "concentracion_minima": ab_conc_min,
                "concentracion_maxima": ab_conc_max,
            },
            0.5,
        )
    ]
    ga = GeneticAlgorithm(
        genes=genes_existentes,
        antibiotic_schedule=schedule,
        mutation_rate=0.1,
        generations=3,
        pop_size=5,
        death_rate=0.05,
    )
    try:
        ga.initialize(ids_seleccionados)
        for _ in range(3):
            ga.step()
    except Exception as e:
        assert "index" in str(e) or "list" in str(e)
    else:
        assert len(ga.avg_hist) == 3

def test_simulacion_con_id_antibiotico_inexistente():
    session = get_session()
    session.query(Antibiotico).delete()
    session.commit()
    session.close()
    genes = [
        {"id": 1, "nombre": "A", "peso_resistencia": 0.5},
        {"id": 2, "nombre": "B", "peso_resistencia": 0.5},
    ]
    schedule = [
        (
            0,
            {
                "id": 9999,
                "nombre": "FakeAb",
                "tipo": "FakeType",
                "concentracion_minima": 0.1,
                "concentracion_maxima": 1.0,
            },
            0.7,
        )
    ]
    ga = GeneticAlgorithm(
        genes=genes,
        antibiotic_schedule=schedule,
        mutation_rate=0.1,
        generations=3,
        pop_size=5,
        death_rate=0.05,
    )
    ga.initialize([1, 2])
    for _ in range(3):
        ga.step()
    assert len(ga.avg_hist) == 3