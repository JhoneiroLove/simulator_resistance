"""
Tests para integración AST→GA (FASE 4)

Valida el feedback loop entre AST y GA:
- Factory method GeneticAlgorithm.from_ast_results()
- Inferencia de mutaciones desde MICs
- Sistema dual de fitness (legacy vs MIC-based)
- Conversión individual→genes
"""

import pytest
from src.core.genetic_algorithm import GeneticAlgorithm
from src.data.database import get_session
from src.data.models import Gen, Antibiotico, GeneClassMultiplier, AntibioticClass


class TestGAASTIntegration:
    """Tests para integración AST→GA."""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Setup: poblar DB con datos necesarios."""
        session = get_session()

        # Limpiar tablas
        session.query(GeneClassMultiplier).delete()
        session.query(AntibioticClass).delete()
        session.query(Gen).delete()
        session.query(Antibiotico).delete()
        session.commit()

        # Crear genes
        genes = [
            Gen(
                nombre="gyrA_T83I",
                peso_resistencia=0.8,
                descripcion="DNA Gyrase mutation",
            ),
            Gen(
                nombre="parC_S87L",
                peso_resistencia=0.7,
                descripcion="Topoisomerase IV mutation",
            ),
            Gen(
                nombre="oprD_inactivation",
                peso_resistencia=0.9,
                descripcion="Porin loss",
            ),
            Gen(nombre="blaVIM", peso_resistencia=0.95, descripcion="Carbapenemase"),
            Gen(
                nombre="pmrB", peso_resistencia=0.85, descripcion="Polymyxin resistance"
            ),
            Gen(
                nombre="ampC", peso_resistencia=0.75, descripcion="AmpC beta-lactamase"
            ),
        ]
        session.add_all(genes)

        # Crear antibióticos
        antibioticos = [
            Antibiotico(
                nombre="Ciprofloxacino",
                concentracion_minima=0.01,
                concentracion_maxima=32.0,
                tipo="Fluoroquinolona",
            ),
            Antibiotico(
                nombre="Meropenem",
                concentracion_minima=0.25,
                concentracion_maxima=64.0,
                tipo="Carbapenem",
            ),
            Antibiotico(
                nombre="Colistina",
                concentracion_minima=0.5,
                concentracion_maxima=16.0,
                tipo="Polimixina",
            ),
        ]
        session.add_all(antibioticos)
        session.commit()

        # Crear clases antibióticas (antibiotico → clase mapping)
        classes = [
            AntibioticClass(antibiotico="Ciprofloxacino", clase="Fluoroquinolona"),
            AntibioticClass(antibiotico="Meropenem", clase="Carbapenem"),
            AntibioticClass(antibiotico="Colistina", clase="Polimixina"),
        ]
        session.add_all(classes)
        session.commit()

        # Crear multiplicadores
        multipliers = [
            GeneClassMultiplier(
                gen="gyrA_T83I",
                clase_antibiotica="Fluoroquinolona",
                multiplicador_mic=8.0,
            ),
            GeneClassMultiplier(
                gen="parC_S87L",
                clase_antibiotica="Fluoroquinolona",
                multiplicador_mic=4.0,
            ),
            GeneClassMultiplier(
                gen="oprD_inactivation",
                clase_antibiotica="Carbapenem",
                multiplicador_mic=16.0,
            ),
            GeneClassMultiplier(
                gen="blaVIM", clase_antibiotica="Carbapenem", multiplicador_mic=8.0
            ),
            GeneClassMultiplier(
                gen="pmrB", clase_antibiotica="Polimixina", multiplicador_mic=8.0
            ),
        ]
        session.add_all(multipliers)
        session.commit()
        session.close()

        yield

        # Cleanup
        session = get_session()
        session.query(GeneClassMultiplier).delete()
        session.query(AntibioticClass).delete()
        session.query(Gen).delete()
        session.query(Antibiotico).delete()
        session.commit()
        session.close()

    def test_infer_mutations_from_mics_fluoroquinolone(self):
        """Test: inferir mutaciones desde MICs altos en fluoroquinolonas."""
        # MICs simulando bacteria con resistencia a Cipro
        ast_mics = {
            "Ciprofloxacino": 32.0,  # Alto (baseline 0.125, fold = 256x)
            "Meropenem": 4.0,  # Normal (baseline 0.5, fold = 8x, no se infiere)
            "Colistina": 1.0,  # Normal (baseline 1.0, fold = 1x)
        }

        # Genes disponibles
        session = get_session()
        genes_db = session.query(Gen).all()
        genes = [
            {"nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_db
        ]
        session.close()

        # Inferir mutaciones
        inferred = GeneticAlgorithm._infer_mutations_from_mics(ast_mics, genes)

        # Debe inferir gyrA y/o parC (relacionados con FQ)
        assert len(inferred) > 0
        assert any(g in ["gyrA_T83I", "parC_S87L"] for g in inferred)

        # NO debe inferir oprD, blaVIM (no hay resistencia a carbapenems)
        assert "oprD_inactivation" not in inferred
        assert "blaVIM" not in inferred

        print("✅ Inferencia de mutaciones (Fluoroquinolona) correcta")
        print(f"   - Genes inferidos: {inferred}")

    def test_infer_mutations_from_mics_carbapenem(self):
        """Test: inferir mutaciones desde MICs altos en carbapenems."""
        ast_mics = {
            "Ciprofloxacino": 0.125,  # Normal (baseline 0.125)
            "Meropenem": 128.0,  # Alto (baseline 0.5, fold = 256x)
            "Colistina": 1.0,  # Normal
        }

        session = get_session()
        genes_db = session.query(Gen).all()
        genes = [
            {"nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_db
        ]
        session.close()

        inferred = GeneticAlgorithm._infer_mutations_from_mics(ast_mics, genes)

        # Debe inferir oprD y/o blaVIM (relacionados con carbapenems)
        assert len(inferred) > 0
        assert any(g in ["oprD_inactivation", "blaVIM"] for g in inferred)

        # NO debe inferir gyrA, parC (no hay resistencia a FQ)
        assert "gyrA_T83I" not in inferred
        assert "parC_S87L" not in inferred

        print("✅ Inferencia de mutaciones (Carbapenem) correcta")
        print(f"   - Genes inferidos: {inferred}")

    def test_infer_mutations_from_mics_multidrug(self):
        """Test: inferir mutaciones con resistencia múltiple."""
        ast_mics = {
            "Ciprofloxacino": 16.0,  # Alto (baseline 0.125, fold = 128x)
            "Meropenem": 64.0,  # Alto (baseline 0.5, fold = 128x)
            "Colistina": 16.0,  # Alto (baseline 1.0, fold = 16x)
        }

        session = get_session()
        genes_db = session.query(Gen).all()
        genes = [
            {"nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_db
        ]
        session.close()

        inferred = GeneticAlgorithm._infer_mutations_from_mics(ast_mics, genes)

        # Debe inferir múltiples genes (multidrug resistance)
        assert len(inferred) >= 3

        # Verificar que incluye genes de cada clase
        has_fq = any(g in ["gyrA_T83I", "parC_S87L"] for g in inferred)
        has_carb = any(g in ["oprD_inactivation", "blaVIM"] for g in inferred)
        has_poly = "pmrB" in inferred

        assert has_fq, "Debe inferir genes de fluoroquinolonas"
        assert has_carb, "Debe inferir genes de carbapenems"
        assert has_poly, "Debe inferir genes de polimixinas"

        print("✅ Inferencia MDR (multidrug resistance) correcta")
        print(f"   - Genes inferidos: {inferred}")

    def test_from_ast_results_factory_method(self):
        """Test: factory method GeneticAlgorithm.from_ast_results()."""
        ast_mics = {
            "Ciprofloxacino": 32.0,
            "Meropenem": 4.0,
            "Colistina": 1.0,
        }

        session = get_session()
        genes_db = session.query(Gen).all()
        genes = [
            {"nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_db
        ]
        session.close()

        # Crear GA desde resultados AST
        ga = GeneticAlgorithm.from_ast_results(
            ast_mic_results=ast_mics,
            genes=genes,
            target_antibiotic="Ciprofloxacino",
            target_concentration=4.0,
            pop_size=50,
            generations=10,
        )

        # Verificar que se creó correctamente
        assert ga is not None
        assert ga.pop_size == 50
        assert ga.generations == 10

        # Verificar que tiene mutaciones inferidas
        assert hasattr(ga, "_inferred_mutations")
        assert len(ga._inferred_mutations) > 0

        # Verificar que tiene MICs AST almacenados
        assert hasattr(ga, "_initial_ast_mics")
        assert ga._initial_ast_mics == ast_mics

        # Verificar que MIC-based fitness está activado
        assert hasattr(ga, "_use_mic_based_fitness")
        assert ga._use_mic_based_fitness is True

        # Verificar que tiene schedule de antibiótico
        assert len(ga.schedule) == 1
        gen_time, ab_dict, conc = ga.schedule[0]
        assert gen_time == 0
        assert ab_dict["nombre"] == "Ciprofloxacino"
        assert conc == 4.0

        print("✅ Factory method from_ast_results() funcional")
        print(f"   - Mutaciones inferidas: {len(ga._inferred_mutations)}")
        print(f"   - MIC-based fitness: {ga._use_mic_based_fitness}")

    def test_individual_to_mutated_genes(self):
        """Test: conversión de individual (bits) a lista de genes mutados."""
        session = get_session()
        genes_db = session.query(Gen).all()
        genes = [
            {"nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_db
        ]
        session.close()

        ga = GeneticAlgorithm(
            genes=genes,
            antibiotic_schedule=[(0, {"nombre": "Cipro"}, 1.0)],
            pop_size=10,
            generations=5,
        )

        # Individual con 6 genes, primeros 3 activados
        individual = [1, 1, 1, 0, 0, 0]

        mutated = ga.individual_to_mutated_genes(individual)

        # Debe retornar los primeros 3 genes
        assert len(mutated) == 3
        assert mutated[0] == genes[0]["nombre"]
        assert mutated[1] == genes[1]["nombre"]
        assert mutated[2] == genes[2]["nombre"]

        print("✅ Conversión individual→genes correcta")
        print(f"   - Individual: {individual}")
        print(f"   - Genes: {mutated}")

    def test_dual_fitness_system_legacy_mode(self):
        """Test: sistema dual de fitness - modo legacy."""
        session = get_session()
        genes_db = session.query(Gen).all()
        genes = [
            {"nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_db
        ]
        session.close()

        ga = GeneticAlgorithm(
            genes=genes,
            antibiotic_schedule=[(0, {"nombre": "Cipro"}, 1.0)],
            pop_size=10,
            generations=5,
        )

        # Por defecto debe usar modo legacy
        assert ga._use_mic_based_fitness is False

        # Evaluar individual
        individual = [1, 1, 0, 0, 0, 0]
        fitness = ga.evaluate(individual)

        # Debe retornar una tupla (DEAP convention)
        assert isinstance(fitness, tuple)
        assert len(fitness) == 1
        assert 0.0 <= fitness[0] <= 2.0

        print("✅ Modo legacy funcional")
        print(f"   - Fitness: {fitness[0]:.4f}")

    def test_dual_fitness_system_mic_mode(self):
        """Test: sistema dual de fitness - modo MIC-based."""
        ast_mics = {"Ciprofloxacino": 32.0}

        session = get_session()
        genes_db = session.query(Gen).all()
        genes = [
            {"nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_db
        ]
        session.close()

        ga = GeneticAlgorithm.from_ast_results(
            ast_mic_results=ast_mics,
            genes=genes,
            target_antibiotic="Ciprofloxacino",
            target_concentration=1.0,
            pop_size=10,
            generations=5,
        )

        # Debe usar modo MIC-based
        assert ga._use_mic_based_fitness is True

        # Evaluar individual con gyrA activado
        individual = [1, 0, 0, 0, 0, 0]  # Solo gyrA
        fitness = ga.evaluate(individual)

        # Debe retornar fitness calculado desde MICs reales (tupla)
        assert isinstance(fitness, tuple)
        assert len(fitness) == 1
        assert 0.0 <= fitness[0] <= 2.0

        print("✅ Modo MIC-based funcional")
        print(f"   - Fitness: {fitness[0]:.4f}")

    def test_enable_disable_mic_fitness(self):
        """Test: toggle entre legacy y MIC-based fitness."""
        session = get_session()
        genes_db = session.query(Gen).all()
        genes = [
            {"nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_db
        ]
        session.close()

        ga = GeneticAlgorithm(
            genes=genes,
            antibiotic_schedule=[(0, {"nombre": "Cipro"}, 1.0)],
            pop_size=10,
            generations=5,
        )

        # Inicialmente legacy
        assert ga._use_mic_based_fitness is False

        # Activar MIC-based
        ga.enable_mic_based_fitness()
        assert ga._use_mic_based_fitness is True

        # Desactivar
        ga.disable_mic_based_fitness()
        assert ga._use_mic_based_fitness is False

        print("✅ Toggle legacy↔MIC-based funcional")

    def test_evaluate_with_mics_requires_calculator(self):
        """Test: evaluate_with_mics requiere GenotypePhenotypeCalculator."""
        session = get_session()
        genes_db = session.query(Gen).all()
        genes = [
            {"nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_db
        ]
        session.close()

        ga = GeneticAlgorithm(
            genes=genes,
            antibiotic_schedule=[(0, {"nombre": "Cipro"}, 1.0)],
            pop_size=10,
            generations=5,
        )

        # Activar MIC-based sin tener calculator
        ga.enable_mic_based_fitness()

        individual = [1, 0, 0, 0, 0, 0]

        # Debe cargar calculator automáticamente (lazy loading)
        fitness = ga.evaluate(individual)
        assert isinstance(fitness, tuple)
        assert len(fitness) == 1

        # Verificar que calculator fue cargado
        assert ga._mic_calculator is not None

        print("✅ Lazy loading de GenotypePhenotypeCalculator funcional")

    def test_backward_compatibility(self):
        """Test: compatibilidad hacia atrás (simulaciones antiguas)."""
        session = get_session()
        genes_db = session.query(Gen).all()
        genes = [
            {"nombre": g.nombre, "peso_resistencia": g.peso_resistencia}
            for g in genes_db
        ]
        session.close()

        # GA creado de forma tradicional (sin from_ast_results)
        ga_old = GeneticAlgorithm(
            genes=genes,
            antibiotic_schedule=[(0, {"nombre": "Cipro"}, 1.0)],
            pop_size=10,
            generations=5,
        )

        # Debe funcionar normalmente con modo legacy
        individual = [1, 1, 0, 0, 0, 0]
        fitness_old = ga_old.evaluate(individual)

        assert isinstance(fitness_old, tuple)
        assert len(fitness_old) == 1
        assert ga_old._use_mic_based_fitness is False

        print("✅ Compatibilidad hacia atrás preservada")
        print(f"   - GA antiguo usa modo legacy: {not ga_old._use_mic_based_fitness}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
