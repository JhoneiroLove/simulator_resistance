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
    recomendacion = relationship("Recomendacion", back_populates="antibiotico", uselist=False)

class Simulacion(Base):
    __tablename__ = "simulaciones"
    id = Column(Integer, primary_key=True)
    antibiotico_id = Column(Integer, ForeignKey("antibioticos.id"), nullable=False)
    concentracion = Column(Float, nullable=False)
    resistencia_predicha = Column(Float, nullable=False)
    fecha = Column(DateTime, server_default=func.now())
    genes = relationship("Gen", secondary="simulacion_genes", lazy="joined")

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

class MetricaGeneracion(Base):
    __tablename__ = "metricas_generacion"
    id = Column(Integer, primary_key=True)
    simulacion_id = Column(Integer, ForeignKey("simulaciones.id"), nullable=False)
    generacion = Column(Integer, nullable=False)
    nombre_indicador = Column(String, nullable=False)
    valor = Column(Float, nullable=False)

    simulacion = relationship("Simulacion", backref="metricas_generacion")