"""
Tests para GenotypePhenotypeCalculator (FASE 4)

Valida el sistema de cálculo MIC desde genotipo:
- Carga de baseline MICs (wild-type)
- Query de multiplicadores desde DB
- Cálculo multiplicativo de MICs
- Especificidad por clase antibiótica
- Fold-change automático
"""

import pytest
from src.core.genotype_phenotype_calculator import (
    GenotypePhenotypeCalculator,
    MICCalculationResult,
    calculate_mics_from_genotype,
)
from src.data.database import get_session
from src.data.models import GeneClassMultiplier, AntibioticClass


class TestGenotypePhenotypeCalculator:
    """Tests para la calculadora de MICs desde genotipo."""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Setup: poblar DB con multiplicadores de prueba."""
        session = get_session()

        # Limpiar tablas
        session.query(GeneClassMultiplier).delete()
        session.query(AntibioticClass).delete()
        session.commit()

        # Crear clases antibióticas (antibiotico → clase mapping)
        classes = [
            AntibioticClass(antibiotico="Ciprofloxacino", clase="Fluoroquinolona"),
            AntibioticClass(antibiotico="Levofloxacino", clase="Fluoroquinolona"),
            AntibioticClass(antibiotico="Meropenem", clase="Carbapenem"),
            AntibioticClass(antibiotico="Imipenem", clase="Carbapenem"),
            AntibioticClass(antibiotico="Colistina", clase="Polimixina"),
            AntibioticClass(antibiotico="Gentamicina", clase="Aminoglucósido"),
            AntibioticClass(antibiotico="Tobramicina", clase="Aminoglucósido"),
            AntibioticClass(antibiotico="Ceftazidima", clase="Cefalosporina"),
            AntibioticClass(antibiotico="Cefepima", clase="Cefalosporina"),
            AntibioticClass(antibiotico="Aztreonam", clase="Monobactam"),
            AntibioticClass(
                antibiotico="Piperacilina-Tazobactam",
                clase="Beta-lactámico + Inhibidor",
            ),
            AntibioticClass(
                antibiotico="Ticarcilina-Clavulánico",
                clase="Beta-lactámico + Inhibidor",
            ),
            AntibioticClass(antibiotico="Amikacina", clase="Aminoglucósido"),
            AntibioticClass(
                antibiotico="Ceftolozano-Tazobactam", clase="Beta-lactámico + Inhibidor"
            ),
            AntibioticClass(
                antibiotico="Ceftazidima-Avibactam", clase="Beta-lactámico + Inhibidor"
            ),
        ]
        session.add_all(classes)
        session.commit()

        # Crear multiplicadores
        multipliers = [
            # Fluoroquinolonas: gyrA + parC
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
            # Carbapenems: oprD + blaVIM
            GeneClassMultiplier(
                gen="oprD_inactivation",
                clase_antibiotica="Carbapenem",
                multiplicador_mic=16.0,
            ),
            GeneClassMultiplier(
                gen="blaVIM", clase_antibiotica="Carbapenem", multiplicador_mic=8.0
            ),
            # Polimixinas: pmrB
            GeneClassMultiplier(
                gen="pmrB", clase_antibiotica="Polimixina", multiplicador_mic=8.0
            ),
            # Aminoglucósidos: aph
            GeneClassMultiplier(
                gen="aph_3_VI",
                clase_antibiotica="Aminoglucósido",
                multiplicador_mic=16.0,
            ),
        ]
        session.add_all(multipliers)
        session.commit()
        session.close()

        # Limpiar cache
        calculator = GenotypePhenotypeCalculator()
        calculator.clear_cache()

        yield

        # Cleanup
        session = get_session()
        session.query(GeneClassMultiplier).delete()
        session.query(AntibioticClass).delete()
        session.commit()
        session.close()

    def test_get_baseline_mics(self):
        """Test: obtener MICs baseline (wild-type) para 15 antibióticos."""
        calculator = GenotypePhenotypeCalculator()
        baseline = calculator.get_baseline_mics()

        # Verificar que tenemos 15 antibióticos
        assert len(baseline) == 15

        # Verificar algunos antibióticos clave
        assert "Ciprofloxacino" in baseline
        assert "Meropenem" in baseline
        assert "Colistina" in baseline
        assert "Amikacina" in baseline

        # Verificar valores conocidos
        assert baseline["Ciprofloxacino"] == 0.125
        assert baseline["Meropenem"] == 0.5
        assert baseline["Colistina"] == 1.0

        print("✅ Baseline MICs cargados correctamente (15 antibióticos)")

    def test_load_multipliers_from_db(self):
        """Test: cargar multiplicadores desde DB y cachear."""
        calculator = GenotypePhenotypeCalculator()

        # Primera carga (desde DB)
        multipliers = calculator.load_multipliers_from_db()

        # Verificar estructura: {antibiotico: {gen: mult}}
        assert isinstance(multipliers, dict)
        assert "Ciprofloxacino" in multipliers
        assert "Meropenem" in multipliers

        # Verificar genes en Ciprofloxacino
        assert "gyrA_T83I" in multipliers["Ciprofloxacino"]
        assert "parC_S87L" in multipliers["Ciprofloxacino"]

        # Verificar valores
        assert multipliers["Ciprofloxacino"]["gyrA_T83I"] == 8.0
        assert (
            multipliers["Ciprofloxacino"]["parC_S87L"] == 4.0
        )  # Segunda carga (desde cache)
        multipliers2 = calculator.load_multipliers_from_db()
        assert multipliers2 is multipliers  # Mismo objeto (cache)

        print("✅ Multiplicadores cargados y cacheados correctamente")

    def test_calculate_mic_single_gene(self):
        """Test: calcular MIC con un solo gen mutado."""
        calculator = GenotypePhenotypeCalculator()

        # gyrA solo afecta fluoroquinolonas
        results = calculator.calculate_all_mics(["gyrA_T83I"])

        # Buscar Ciprofloxacino (results es dict)
        assert isinstance(results, dict)
        cipro = results["Ciprofloxacino"]

        # MIC base = 0.125, multiplicador = 8.0
        # MIC calculado = 0.125 * 8.0 = 1.0
        assert cipro.mic_base == 0.125
        assert cipro.mic_calculado == pytest.approx(1.0, rel=1e-3)
        assert cipro.fold_change == pytest.approx(8.0, rel=1e-3)
        assert "gyrA_T83I" in cipro.genes_aplicados

        # Meropenem NO debe cambiar (no es fluoroquinolona)
        mero = results["Meropenem"]
        assert mero.mic_calculado == mero.mic_base  # Sin cambio
        assert mero.fold_change == 1.0

        print("✅ MIC con gen único calculado correctamente")
        print(
            f"   - Cipro: {cipro.mic_base} → {cipro.mic_calculado} (×{cipro.fold_change:.1f})"
        )
        print(f"   - Mero: {mero.mic_base} → {mero.mic_calculado} (sin cambio)")

    def test_calculate_mic_multiple_genes_same_class(self):
        """Test: calcular MIC con múltiples genes de la misma clase (multiplicación)."""
        calculator = GenotypePhenotypeCalculator()

        # gyrA + parC ambos afectan fluoroquinolonas
        results = calculator.calculate_all_mics(["gyrA_T83I", "parC_S87L"])

        cipro = results["Ciprofloxacino"]

        # MIC base = 0.125, multiplicadores = 8.0 * 4.0 = 32.0
        # MIC calculado = 0.125 * 32.0 = 4.0
        assert cipro.mic_base == 0.125
        assert cipro.mic_calculado == pytest.approx(4.0, rel=1e-3)
        assert cipro.fold_change == pytest.approx(32.0, rel=1e-3)
        assert "gyrA_T83I" in cipro.genes_aplicados
        assert "parC_S87L" in cipro.genes_aplicados
        assert len(cipro.multiplicadores) == 2
        assert 8.0 in cipro.multiplicadores
        assert 4.0 in cipro.multiplicadores

        print("✅ MIC con genes múltiples (misma clase) calculado correctamente")
        print(
            f"   - Cipro: {cipro.mic_base} → {cipro.mic_calculado} (×{cipro.fold_change:.1f})"
        )
        print(f"   - Genes aplicados: {cipro.genes_aplicados}")

    def test_calculate_mic_multiple_genes_different_classes(self):
        """Test: calcular MIC con genes de diferentes clases (especificidad)."""
        calculator = GenotypePhenotypeCalculator()

        # gyrA (FQ) + oprD (Carbapenem) + pmrB (Polimixina)
        genes = ["gyrA_T83I", "oprD_inactivation", "pmrB"]
        results = calculator.calculate_all_mics(genes)

        # Ciprofloxacino: solo afectado por gyrA
        cipro = results["Ciprofloxacino"]
        assert cipro.fold_change == pytest.approx(8.0, rel=1e-3)
        assert cipro.genes_aplicados == ["gyrA_T83I"]

        # Meropenem: solo afectado por oprD
        mero = results["Meropenem"]
        assert mero.fold_change == pytest.approx(16.0, rel=1e-3)
        assert mero.genes_aplicados == ["oprD_inactivation"]

        # Colistina: solo afectado por pmrB
        coli = results["Colistina"]
        assert coli.fold_change == pytest.approx(8.0, rel=1e-3)
        assert coli.genes_aplicados == ["pmrB"]

        # Gentamicina: NO afectado (no tiene genes relacionados)
        amika = results["Amikacina"]  # Gentamicina no existe, usamos Amikacina
        assert amika.fold_change == 1.0
        assert amika.genes_aplicados == []

        print("✅ Especificidad por clase verificada correctamente")
        print(f"   - Cipro afectado por: {cipro.genes_aplicados}")
        print(f"   - Mero afectado por: {mero.genes_aplicados}")
        print(f"   - Coli afectado por: {coli.genes_aplicados}")
        print(f"   - Genta afectado por: {amika.genes_aplicados}")

    def test_calculate_mic_carbapenem_double_resistance(self):
        """Test: doble resistencia a carbapenems (oprD + blaVIM)."""
        calculator = GenotypePhenotypeCalculator()

        # oprD + blaVIM ambos afectan carbapenems
        results = calculator.calculate_all_mics(["oprD_inactivation", "blaVIM"])

        # Meropenem e Imipenem deben aumentar ×128
        mero = results["Meropenem"]
        imi = results["Imipenem"]

        # MIC base Meropenem = 0.5, multiplicadores = 16.0 * 8.0 = 128.0
        # MIC calculado = 0.5 * 128.0 = 64.0
        assert mero.mic_calculado == pytest.approx(64.0, rel=1e-3)
        assert mero.fold_change == pytest.approx(128.0, rel=1e-3)
        assert len(mero.genes_aplicados) == 2

        # Imipenem similar
        assert imi.fold_change == pytest.approx(128.0, rel=1e-3)

        print("✅ Resistencia doble a carbapenems verificada")
        print(
            f"   - Mero: {mero.mic_base} → {mero.mic_calculado} (×{mero.fold_change:.0f})"
        )

    def test_get_mics_as_dict(self):
        """Test: método simplificado get_mics_as_dict()."""
        calculator = GenotypePhenotypeCalculator()

        mics = calculator.get_mics_as_dict(["gyrA_T83I", "oprD_inactivation"])

        # Verificar que es un dict simple
        assert isinstance(mics, dict)
        assert "Ciprofloxacino" in mics
        assert "Meropenem" in mics

        # Verificar valores
        assert mics["Ciprofloxacino"] == pytest.approx(1.0, rel=1e-3)  # 0.125 * 8.0
        assert mics["Meropenem"] == pytest.approx(8.0, rel=1e-3)  # 0.5 * 16.0

        print("✅ Método get_mics_as_dict() funcional")
        print(f"   - Dict simplificado: {list(mics.keys())[:3]}...")

    def test_standalone_function(self):
        """Test: función standalone calculate_mics_from_genotype()."""
        results = calculate_mics_from_genotype(["gyrA_T83I", "pmrB"])

        # Verificar que retorna dict antibiótico → MIC
        assert isinstance(results, dict)
        assert len(results) == 15

        # Verificar cálculos
        assert "Ciprofloxacino" in results
        assert "Colistina" in results

        # Cipro: 0.125 * 8.0 = 1.0
        assert results["Ciprofloxacino"] == pytest.approx(1.0, rel=1e-3)
        # Colistina: 1.0 * 8.0 = 8.0
        assert results["Colistina"] == pytest.approx(8.0, rel=1e-3)

        print("✅ Función standalone calculate_mics_from_genotype() funcional")

    def test_empty_genotype(self):
        """Test: genotipo vacío (wild-type) debe retornar MICs baseline."""
        calculator = GenotypePhenotypeCalculator()

        results = calculator.calculate_all_mics([])

        # Todos los MICs deben ser iguales al baseline (fold_change = 1.0)
        for r in results.values():
            assert r.mic_calculado == r.mic_base
            assert r.fold_change == 1.0
            assert r.genes_aplicados == []
            assert r.multiplicadores == []

        print("✅ Genotipo vacío retorna MICs baseline correctamente")

    def test_unknown_gene(self):
        """Test: gen desconocido (no en DB) no debe afectar MICs."""
        calculator = GenotypePhenotypeCalculator()

        # Gen ficticio que no existe en DB
        results = calculator.calculate_all_mics(["fake_gene_XYZ"])

        # Todos los MICs deben ser baseline (sin cambio)
        for r in results.values():
            assert r.mic_calculado == r.mic_base
            assert r.fold_change == 1.0

        print("✅ Genes desconocidos ignorados correctamente")

    def test_mic_calculation_result_dataclass(self):
        """Test: dataclass MICCalculationResult."""
        result = MICCalculationResult(
            antibiotico="Ciprofloxacino",
            mic_base=0.125,
            mic_calculado=4.0,
            genes_aplicados=["gyrA_T83I", "parC_S87L"],
            multiplicadores=[8.0, 4.0],
        )

        # Verificar fold_change auto-calculado
        assert result.fold_change == pytest.approx(32.0, rel=1e-3)

        # Verificar representación
        assert "Ciprofloxacino" in str(result)
        assert "4.0" in str(result)  # mic_calculado

        print("✅ Dataclass MICCalculationResult funcional")

    def test_cache_performance(self):
        """Test: verificar que el cache mejora performance."""
        calculator = GenotypePhenotypeCalculator()

        # Primera llamada (carga desde DB)
        import time

        start = time.time()
        calculator.load_multipliers_from_db()
        first_time = time.time() - start

        # Segunda llamada (desde cache)
        start = time.time()
        calculator.load_multipliers_from_db()
        cached_time = time.time() - start

        # Cache debe ser significativamente más rápido
        assert cached_time < first_time

        print(
            f"✅ Cache verificado (primera: {first_time * 1000:.2f}ms, cache: {cached_time * 1000:.2f}ms)"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
