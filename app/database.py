import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Date, JSON
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

# pool_pre_ping testa a conexão antes de usá-la e pool_recycle a renova a cada 5 min:
# o Neon (plano gratuito) encerra conexões ociosas, o que causava
# "SSL connection has been closed unexpectedly" e erro 500 na primeira requisição.
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
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


class AvaliacaoAntropometrica(Base):
    """
    Histórico de avaliações antropométricas de um paciente.

    Cada salvamento gera UM registro novo e imutável (não há edição/remoção):
    guardamos as medidas informadas e o SNAPSHOT do resultado calculado na
    época. Assim, se uma fórmula for corrigida no futuro, as avaliações antigas
    continuam mostrando exatamente o que foi entregue ao paciente, e a evolução
    (peso, % de gordura) pode ser comparada entre datas.

    Dobras e circunferências ficam em JSON porque o conjunto de medidas varia
    por fórmula; a validação dos campos e limites é feita na API (Pydantic).
    """
    __tablename__ = "avaliacoes_antropometricas"

    id              = Column(Integer, primary_key=True, index=True)
    paciente_id     = Column(Integer, ForeignKey("pacientes.id"), nullable=False, index=True)
    profissional_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_avaliacao  = Column(Date, nullable=False)
    criado_em       = Column(DateTime, nullable=False, default=datetime.utcnow)

    sexo     = Column(String(1), nullable=False)
    idade    = Column(Integer)
    peso     = Column(Float)
    altura   = Column(Float)
    formula  = Column(String, nullable=False)

    dobras          = Column(JSON, nullable=False, default=dict)
    circunferencias = Column(JSON, nullable=False, default=dict)
    resultado       = Column(JSON, nullable=False)


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

    # --- Recuperação de senha ---
    # Armazenamos apenas o HASH do token, nunca o valor original.
    # Isso segue a mesma lógica de nunca guardar senha em texto puro:
    # se o banco vazar, os tokens de reset não são reutilizáveis.
    reset_token_hash    = Column(String,   nullable=True)
    reset_token_expira  = Column(DateTime, nullable=True)