import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# =============================================================================
# CARREGAMENTO AUTOMÁTICO DO .env
# Funciona independentemente de onde o uvicorn é iniciado (raiz ou app/).
# Em produção (Render), o .env não existe — as variáveis vêm do painel
# do Render diretamente, então load_dotenv() simplesmente não encontra
# nada e não faz diferença.
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent   # raiz do projeto (um nível acima de app/)
load_dotenv(BASE_DIR / ".env")

# =============================================================================
# CONEXÃO COM O BANCO
# A URL é lida da variável de ambiente DATABASE_URL — vinda do .env local
# ou das variáveis configuradas no painel do Render em produção.
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "Variável de ambiente DATABASE_URL não encontrada.\n"
        "→ Local: verifique se existe um arquivo .env na raiz do projeto.\n"
        "→ Produção: configure no painel do Render (Environment > Add Environment Variable)."
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# =============================================================================
# MODELOS
# =============================================================================

class Paciente(Base):
    __tablename__ = "pacientes"

    id       = Column(Integer, primary_key=True, index=True)
    nome     = Column(String, nullable=False)
    email    = Column(String)
    telefone = Column(String)
    objetivo = Column(String)

    # Campos antropométricos integrados ao cadastro
    sexo     = Column(String,  default="F")
    idade    = Column(Integer, default=0)
    peso     = Column(Float,   default=0.0)
    altura   = Column(Float,   default=0.0)
    cintura  = Column(Float,   default=0.0)
    quadril  = Column(Float,   default=0.0)
    abdomen  = Column(Float,   default=0.0)


class AlimentoTACO(Base):
    __tablename__ = "alimentos_taco"

    id    = Column(Integer, primary_key=True, index=True)
    nome  = Column(String, nullable=False)
    kcal  = Column(Float)
    carb  = Column(Float)
    prot  = Column(Float)
    gord  = Column(Float)
    fibra = Column(Float, default=0.0)
    sodio = Column(Float, default=0.0)


class Refeicao(Base):
    __tablename__ = "refeicoes"

    id          = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), index=True)
    nome        = Column(String, nullable=False)
    horario     = Column(String, nullable=False)


class ItemRefeicao(Base):
    __tablename__ = "itens_refeicao"

    id          = Column(Integer, primary_key=True, index=True)
    refeicao_id = Column(Integer, ForeignKey("refeicoes.id"), index=True)
    alimento_id = Column(Integer, ForeignKey("alimentos_taco.id"))
    quantidade  = Column(Float, nullable=False)


class Usuario(Base):
    __tablename__ = "usuarios"

    id          = Column(Integer, primary_key=True, index=True)
    nome        = Column(String, nullable=False)
    email       = Column(String, unique=True, index=True, nullable=False)
    senha_hash  = Column(String, nullable=False)
    role        = Column(String, default="paciente")  # 'profissional' ou 'paciente'