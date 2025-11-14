from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Gen(Base):
    __tablename__ = "genes"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True)
    peso_resistencia = Column(Float)
    descripcion = Column(String(200))


class Antibiotico(Base):
    __tablename__ = "antibioticos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True)

    # Concentraciones usadas en la simulación
    concentracion_minima = Column(Float, nullable=False)
    concentracion_maxima = Column(Float, nullable=False)
    tipo = Column(String(50))
    # relación 1–1 a Recomendacion
    recomendacion = relationship(
        "Recomendacion", back_populates="antibiotico", uselist=False
    )


class Simulacion(Base):
    __tablename__ = "simulaciones"
    id = Column(Integer, primary_key=True)
    antibiotico_id = Column(Integer, ForeignKey("antibioticos.id"), nullable=False)
    concentracion = Column(Float, nullable=False)
    resistencia_predicha = Column(Float, nullable=False)
    fecha = Column(DateTime, server_default=func.now())
    huesped_id = Column(Integer, ForeignKey("guests.id"))

    genes = relationship("Gen", secondary="simulacion_genes", lazy="joined")
    # Agregar foreign_keys
    huesped = relationship(
        "Guest", back_populates="simulaciones", foreign_keys=[huesped_id]
    )


class SimulacionGen(Base):
    __tablename__ = "simulacion_genes"
    simulacion_id = Column(Integer, ForeignKey("simulaciones.id"), primary_key=True)
    gen_id = Column(Integer, ForeignKey("genes.id"), primary_key=True)


class Recomendacion(Base):
    __tablename__ = "recomendaciones"
    id = Column(Integer, primary_key=True)
    antibiotico_id = Column(Integer, ForeignKey("antibioticos.id"), nullable=False)
    texto = Column(String, nullable=False)
    antibiotico = relationship("Antibiotico", back_populates="recomendacion")


class SimulacionAtributos(Base):
    __tablename__ = "simulacion_atributos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    simulacion_id = Column(Integer, ForeignKey("simulaciones.id"), nullable=False)
    generacion = Column(Integer, nullable=False)
    antibiotico_id = Column(Integer, ForeignKey("antibioticos.id"), nullable=True)
    atributo = Column(String, nullable=False)
    valor_promedio = Column(Float, nullable=False)
    desviacion_std = Column(Float)
    fecha = Column(DateTime, server_default=func.now())

    simulacion = relationship("Simulacion", backref="atributos")
    antibiotico = relationship("Antibiotico", backref="atributos")


class ReporteSimulacion(Base):
    __tablename__ = "reportes_simulacion"
    id = Column(Integer, primary_key=True)
    simulacion_id = Column(Integer, ForeignKey("simulaciones.id"), nullable=False)
    fecha_ejecucion = Column(DateTime, server_default=func.now())
    generaciones_totales = Column(Integer, nullable=False)
    parametros_input = Column(String, nullable=False)  # JSON almacenado como texto

    simulacion = relationship("Simulacion")


class Guest(Base):
    """
    Modelo de paciente/huésped para simulaciones de resistencia bacteriana.
    """

    __tablename__ = "guests"

    # Campos básicos
    id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    sex = Column(String(10), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Función renal
    creatinina_serica = Column(Float)
    clearance_creatinina = Column(Float)

    # Función hepática
    alt = Column(Float)
    ast = Column(Float)
    bilirrubina_total = Column(Float)

    # Estado inmunológico
    estado_inmune = Column(String(30), nullable=False, default="normal")

    simulaciones = relationship(
        "Simulacion", back_populates="huesped", foreign_keys="Simulacion.huesped_id"
    )


class InfectionSite(Base):
    """
    Modelo de sitios de infección con características ambientales.
    Encapsula las propiedades físicas y fisiológicas del sitio donde ocurre la infección.
    """

    __tablename__ = "sitios_infeccion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    ph = Column(Float, nullable=False)
    capacidad_carga = Column(Float, nullable=False)
    perfusion_sanguinea = Column(Float, nullable=False, default=0.5)

    def __repr__(self):
        return f"<InfectionSite(id={self.id}, nombre='{self.nombre}', pH={self.ph}, perfusion={self.perfusion_sanguinea})>"


class Breakpoint(Base):
    """
    Modelo de breakpoints (puntos de corte) para interpretación S/R.
    Basado en estándares EUCAST y CLSI para Pseudomonas aeruginosa.
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
            'S' (sensible) o 'R' (resistente)
        """
        if mic_value <= self.s_mic:
            return "S"
        elif mic_value > self.r_mic:
            return "R"
        else:
            return "R"

    def __repr__(self):
        return f"<Breakpoint {self.antibiotico} ({self.standard}) S≤{self.s_mic} R>{self.r_mic}>"


class GeneClassMultiplier(Base):
    """
    Modelo de multiplicadores gen×clase para cálculo de MICs.
    Representa el efecto de cada gen de resistencia sobre cada clase de antibióticos.
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
    Define qué clase de antibiótico pertenece cada antibiótico para aplicar multiplicadores.
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
