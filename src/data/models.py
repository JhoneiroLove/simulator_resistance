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
    concentracion_minima = Column(Float)
    concentracion_maxima = Column(Float)
    tipo = Column(String(50))

class Simulacion(Base):
    __tablename__ = "simulaciones"
    id = Column(Integer, primary_key=True)
    antibiotico_id = Column(Integer, ForeignKey("antibioticos.id"))
    concentracion = Column(Float)
    resistencia_predicha = Column(Float)
    fecha = Column(DateTime, server_default=func.now())
    genes = relationship("Gen", secondary="simulacion_genes", lazy="joined")

class SimulacionGen(Base):
    __tablename__ = "simulacion_genes"
    simulacion_id = Column(Integer, ForeignKey("simulaciones.id"), primary_key=True)
    gen_id = Column(Integer, ForeignKey("genes.id"), primary_key=True)