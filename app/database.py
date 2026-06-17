from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./nutrisocial.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Paciente(Base):
    __tablename__ = "pacientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String)
    telefone = Column(String)
    objetivo = Column(String)
    
    # Novos campos antropométricos integrados ao cadastro
    sexo = Column(String, default="F")
    idade = Column(Integer, default=0)
    peso = Column(Float, default=0.0)
    altura = Column(Float, default=0.0)
    cintura = Column(Float, default=0.0)
    quadril = Column(Float, default=0.0)
    abdomen = Column(Float, default=0.0)

class AlimentoTACO(Base):
    __tablename__ = "alimentos_taco"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    kcal = Column(Float)
    carb = Column(Float)
    prot = Column(Float)
    gord = Column(Float)
    fibra = Column(Float, default=0.0) # NOVA COLUNA
    sodio = Column(Float, default=0.0) # NOVA COLUNA

# --- NOVAS TABELAS PARA A DIETA ---

class Refeicao(Base):
    __tablename__ = "refeicoes"
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), index=True)
    nome = Column(String, nullable=False)
    horario = Column(String, nullable=False)

class ItemRefeicao(Base):
    __tablename__ = "itens_refeicao"
    
    id = Column(Integer, primary_key=True, index=True)
    refeicao_id = Column(Integer, ForeignKey("refeicoes.id"), index=True)
    alimento_id = Column(Integer, ForeignKey("alimentos_taco.id"))
    quantidade = Column(Float, nullable=False)

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    role = Column(String, default="paciente") # Pode ser: 'profissional' ou 'paciente'