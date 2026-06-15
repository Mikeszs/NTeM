from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Configuração do SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./nutrisocial.db"

# O 'check_same_thread' é necessário apenas para o SQLite funcionar bem com o FastAPI
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 2. Criando as nossas Tabelas (Modelos)
class Paciente(Base):
    __tablename__ = "pacientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String)
    telefone = Column(String)
    objetivo = Column(String)

class AlimentoTACO(Base):
    __tablename__ = "alimentos_taco"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    kcal = Column(Float)
    carb = Column(Float)
    prot = Column(Float)
    gord = Column(Float)