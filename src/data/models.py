from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# ============================================================================
# MODELOS CIENTÍFICOS AST (Post-refactorización)
# ============================================================================
# Solo se mantienen modelos necesarios para el workflow AST científico.
# Modelos legacy eliminados: Gen, Antibiotico, Simulacion, Recomendacion,
# SimulacionGen, SimulacionAtributos, ReporteSimulacion, Guest, InfectionSite
# ============================================================================


class Breakpoint(Base):
    """
    Modelo de breakpoints (puntos de corte) para interpretación S/R.
    Basado en estándares EUCAST y CLSI para Pseudomonas aeruginosa.

    Fuente: Migración 014 (EUCAST v15.0, CLSI M07)
    """

    __tablename__ = "breakpoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    antibiotico = Column(String(100), nullable=False)
    organismo = Column(String(100), nullable=False, default="Pseudomonas aeruginosa")
    s_mic = Column(Float, nullable=False)
    r_mic = Column(Float, nullable=False)
    standard = Column(String(20), nullable=False)
    fuente = Column(String(200), nullable=False)
    familia = Column(String(100))
    mecanismo = Column(String(200))

    def interpret_mic(self, mic_value: float) -> str:
        """
        Interpreta un valor MIC según los breakpoints.

        Args:
            mic_value: Concentración MIC en µg/mL

        Returns:
            'S' (sensible), 'I' (intermedio) o 'R' (resistente)
        """
        if mic_value <= self.s_mic:
            return "S"
        elif mic_value > self.r_mic:
            return "R"
        else:
            return "I"

    def __repr__(self):
        return f"<Breakpoint {self.antibiotico} ({self.standard}) S≤{self.s_mic} R>{self.r_mic}>"


class GeneClassMultiplier(Base):
    """
    Modelo de multiplicadores gen×clase para cálculo de MICs.
    Representa el efecto de cada gen de resistencia sobre cada clase de antibióticos.

    Fuente: Migración 015 (Matriz científica con referencias PMID)
    """

    __tablename__ = "gene_class_multipliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    gen = Column(String(100), nullable=False)
    clase_antibiotica = Column(String(100), nullable=False)
    multiplicador_mic = Column(Float, nullable=False, default=1.0)

    def __repr__(self):
        return f"<GeneClassMultiplier {self.gen} × {self.clase_antibiotica} = ×{self.multiplicador_mic}>"


class AntibioticClass(Base):
    """
    Modelo de mapeo antibiótico → clase.
    Define qué clase pertenece cada antibiótico para aplicar multiplicadores.

    Fuente: Migración 017 (Familias y mecanismos científicos)
    """

    __tablename__ = "antibiotic_classes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    antibiotico = Column(String(100), nullable=False, unique=True)
    clase = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<AntibioticClass {self.antibiotico} → {self.clase}>"


class BacteriaProfile(Base):
    """
    Modelo de perfiles bacterianos generados in-silico.
    Almacena el estado inicial de la bacteria antes de ejecutar AST.

    Fuente: Migración 018 (Generación científica de perfiles)
    """

    __tablename__ = "bacteria_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organismo = Column(String(100), nullable=False, default="Pseudomonas aeruginosa")
    escenario = Column(String(50), nullable=False)
    origen_muestra = Column(String(50))
    antibioticos_previos = Column(String(500))
    genotipo = Column(String(1000), nullable=False)
    mics_calculated = Column(String(1000), nullable=False)
    mutaciones_aplicadas = Column(String(1000))
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<BacteriaProfile {self.organismo} ({self.escenario})>"


class PanelLayout(Base):
    """
    Modelo de layouts de panel AST (96 wells).
    Define la distribución de antibióticos y concentraciones en el panel.

    Fuente: Migración 016 (Paneles EUCAST/CLSI oficiales)
    """

    __tablename__ = "panel_layouts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    panel_name = Column(String(100), nullable=False)
    well_position = Column(String(10), nullable=False)
    antibiotico = Column(String(100), nullable=False)
    concentracion = Column(Float, nullable=False)
    tipo = Column(String(20), nullable=False)

    def __repr__(self):
        return f"<PanelLayout {self.panel_name} {self.well_position}: {self.antibiotico} {self.concentracion}µg/mL>"


class BaselineMIC(Base):
    """
    Modelo de MICs basales (wild-type) para Pseudomonas aeruginosa.
    Representa los valores MIC de bacterias sin mutaciones de resistencia.

    Fuente: Migración 019 (EUCAST ECOFFs, CLSI wild-type distributions)
    """

    __tablename__ = "baseline_mics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    antibiotico = Column(String(100), nullable=False, unique=True)
    mic_wt = Column(Float, nullable=False)
    organismo = Column(String(100), nullable=False, default="Pseudomonas aeruginosa")
    metodo = Column(String(50), nullable=False, default="Broth microdilution")
    fuente = Column(String(200), nullable=False)
    notas = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<BaselineMIC {self.antibiotico}: {self.mic_wt} µg/mL (WT)>"


class HeteroresistanceDistribution(Base):
    """
    Modelo de distribuciones de heteroresistencia.

    Representa subpoblaciones bacterianas con MICs diferentes dentro de la misma cepa.
    Fundamental para modelar resistencia heterogénea común en P. aeruginosa.

    Fuente: Migración 020 (PMID:25691624 - Heteroresistance to carbapenems)
    """

    __tablename__ = "heteroresistance_distributions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    antibiotico = Column(String(100), nullable=False)
    genotype_signature = Column(String(200), nullable=False)
    mean_log_mic = Column(Float, nullable=False)
    std_log_mic = Column(Float, nullable=False, default=0.3)
    prevalence = Column(Float, nullable=False, default=0.01)
    detection_frequency = Column(Float)
    pmid_reference = Column(String(50))
    study_conditions = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return (
            f"<HeteroresistanceDistribution {self.antibiotico} "
            f"({self.genotype_signature}): μ={self.mean_log_mic:.2f}, "
            f"σ={self.std_log_mic:.2f}, prev={self.prevalence * 100:.1f}%>"
        )


class FitnessCost(Base):
    """
    Modelo de costos de fitness asociados a mecanismos de resistencia.

    Representa el costo biológico (reducción en tasa de crecimiento, virulencia, etc.)
    de cada gen de resistencia. Crítico para modelar evolución y transmisión.

    Fuente: Migración 021 (PMID:19258524 - Fitness costs in P. aeruginosa)
    """

    __tablename__ = "fitness_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    gen = Column(String(100), nullable=False, unique=True)
    fitness_cost = Column(Float, nullable=False, default=0.0)
    growth_rate_penalty = Column(Float, default=0.0)
    doubling_time_increase = Column(Float, default=0.0)
    competitive_index = Column(Float, default=1.0)
    context_dependent = Column(Integer, default=0)  # SQLite no tiene BOOLEAN nativo
    compensatory_mutations = Column(String)
    pmid_reference = Column(String(50))
    measurement_method = Column(String(100))
    study_conditions = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return (
            f"<FitnessCost {self.gen}: cost={self.fitness_cost:.3f}, "
            f"CI={self.competitive_index:.2f}>"
        )
