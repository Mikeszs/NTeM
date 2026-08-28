import os
import json
from datetime import datetime, timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

from database import engine, Base, SessionLocal, Paciente, AlimentoTACO, Refeicao, ItemRefeicao, Usuario

# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NutriSocial API",
    description="API para gestão nutricional e clínica",
)

# =============================================================================
# CORS
# Em produção, substitua "*" pela URL real do seu frontend no Vercel.
# Ex: allow_origins=["https://meu-projeto.vercel.app"]
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ntem.vercel.app",      # produção
        "http://127.0.0.1:5500",        # desenvolvimento local — VS Code Live Server
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA — lidas do ambiente, nunca hardcoded
# =============================================================================

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = "HS256"

# Lê o tempo de expiração do ambiente; fallback para 60 minutos
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

if not SECRET_KEY:
    raise RuntimeError(
        "Variável de ambiente SECRET_KEY não encontrada. "
        "Gere um valor com: python -c \"import secrets; print(secrets.token_hex(32))\" "
        "e adicione no painel do Render em Environment."
    )

pwd_context    = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme  = OAuth2PasswordBearer(tokenUrl="auth/login")


# =============================================================================
# DEPENDÊNCIA: conexão com o banco
# =============================================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# CONTRATOS PYDANTIC (schemas de entrada/saída)
# =============================================================================

class UsuarioCadastro(BaseModel):
    nome:  str
    email: str
    senha: str
    role:  str

class Token(BaseModel):
    access_token: str
    token_type:   str
    role:         str
    nome:         str

class PacienteCreate(BaseModel):
    nome:     str
    objetivo: str
    email:    str = None
    telefone: str = None

class PacienteUpdate(BaseModel):
    nome:     str
    objetivo: str
    email:    str   = None
    telefone: str   = None
    sexo:     str
    idade:    int
    peso:     float
    altura:   float
    cintura:  float = 0.0
    quadril:  float = 0.0
    abdomen:  float = 0.0

class ItemDietaCreate(BaseModel):
    id:        int
    quantidade: float

class RefeicaoCreate(BaseModel):
    nome:    str
    horario: str
    itens:   List[ItemDietaCreate]

class DietaPayload(BaseModel):
    paciente_id: int
    refeicoes:   List[RefeicaoCreate]


# =============================================================================
# FUNÇÕES AUXILIARES DE AUTENTICAÇÃO
# =============================================================================

def obter_senha_hash(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_pura, senha_hash)

def criar_token_acesso(dados: dict) -> str:
    dados_copia = dados.copy()
    expiracao   = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_copia.update({"exp": expiracao})
    return jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)

def obter_usuario_atual(
    token: str = Depends(oauth2_scheme),
    db:    Session = Depends(get_db),
) -> Usuario:
    """Decodifica o JWT e retorna o usuário autenticado. Levanta 401 se inválido."""
    excecao = HTTPException(status_code=401, detail="Token inválido ou expirado")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise excecao
    except JWTError:
        raise excecao

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise excecao
    return usuario


# =============================================================================
# ROTAS
# =============================================================================

@app.get("/")
async def raiz():
    return {"mensagem": "NutriSocial API online e segura."}


# --- AUTENTICAÇÃO ---

@app.post("/auth/cadastro", status_code=201)
async def cadastrar_usuario(usuario: UsuarioCadastro, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    novo = Usuario(
        nome       = usuario.nome,
        email      = usuario.email,
        senha_hash = obter_senha_hash(usuario.senha),
        role       = usuario.role.lower(),
    )
    db.add(novo)
    db.commit()
    return {"mensagem": f"Usuário {novo.nome} criado com a função '{novo.role}'."}


@app.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    # Mensagem genérica para não revelar se o e-mail existe ou não
    if not usuario or not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    token = criar_token_acesso({"sub": usuario.email, "role": usuario.role})
    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         usuario.role,
        "nome":         usuario.nome,
    }


# --- PACIENTES ---

@app.get("/pacientes/")
async def listar_pacientes(
    db: Session = Depends(get_db),
    _: Usuario = Depends(obter_usuario_atual),
):
    return db.query(Paciente).all()

@app.get("/pacientes/{paciente_id}")
async def obter_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(obter_usuario_atual),
):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente

@app.post("/pacientes/")
async def criar_paciente(
    paciente: PacienteCreate,
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(obter_usuario_atual),
):
    if usuario_logado.role != "profissional":
        raise HTTPException(status_code=403, detail="Acesso restrito a profissionais.")
    novo = Paciente(
        nome=paciente.nome,
        objetivo=paciente.objetivo,
        email=paciente.email,
        telefone=paciente.telefone,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"status": "sucesso", "mensagem": "Paciente cadastrado!", "dados": novo}

@app.put("/pacientes/{paciente_id}")
async def atualizar_paciente(
    paciente_id: int,
    dados: PacienteUpdate,
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(obter_usuario_atual),
):
    if usuario_logado.role != "profissional":
        raise HTTPException(status_code=403, detail="Acesso restrito a profissionais.")
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    paciente.nome     = dados.nome
    paciente.objetivo = dados.objetivo
    paciente.email    = dados.email
    paciente.telefone = dados.telefone
    paciente.sexo     = dados.sexo
    paciente.idade    = dados.idade
    paciente.peso     = dados.peso
    paciente.altura   = dados.altura
    paciente.cintura  = dados.cintura
    paciente.quadril  = dados.quadril
    paciente.abdomen  = dados.abdomen

    db.commit()
    db.refresh(paciente)
    return {"status": "sucesso", "mensagem": "Prontuário atualizado.", "dados": paciente}


# --- ALIMENTOS (TACO) ---

@app.get("/alimentos/")
async def listar_alimentos(
    db: Session = Depends(get_db),
    _: Usuario = Depends(obter_usuario_atual),
):
    return db.query(AlimentoTACO).all()

@app.post("/importar-taco-completa/")
async def importar_taco_completa(
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(obter_usuario_atual),
):
    """Importa o taco.json. Restrito a profissionais. Bloqueada se banco já populado."""
    if usuario_logado.role != "profissional":
        raise HTTPException(status_code=403, detail="Acesso restrito a profissionais.")
    """Importa o taco.json para o banco. Abortada se já houver alimentos."""
    quantidade = db.query(AlimentoTACO).count()
    if quantidade > 0:
        return {"mensagem": f"Banco já possui {quantidade} alimentos. Abortado."}

    caminho = "taco.json"
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Arquivo taco.json não encontrado.")

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    alimentos = [
        AlimentoTACO(
            nome  = item.get("nome", "Sem Nome"),
            kcal  = float(item.get("kcal",  0)),
            carb  = float(item.get("carb",  0)),
            prot  = float(item.get("prot",  0)),
            gord  = float(item.get("gord",  0)),
            fibra = float(item.get("fibra", 0)),
            sodio = float(item.get("sodio", 0)),
        )
        for item in dados
    ]
    db.add_all(alimentos)
    db.commit()
    return {"status": "sucesso", "mensagem": f"{len(alimentos)} alimentos importados."}


# --- DIETA ---

@app.post("/dietas/")
async def salvar_dieta(
    payload: DietaPayload,
    db: Session = Depends(get_db),
    usuario_logado: Usuario = Depends(obter_usuario_atual),
):
    """Salva o plano alimentar. Restrito a profissionais autenticados."""
    if usuario_logado.role != "profissional":
        raise HTTPException(status_code=403, detail="Acesso restrito a profissionais.")

    # Remove refeições antigas do paciente antes de salvar as novas
    antigas = db.query(Refeicao).filter(Refeicao.paciente_id == payload.paciente_id).all()
    for ref in antigas:
        db.query(ItemRefeicao).filter(ItemRefeicao.refeicao_id == ref.id).delete()
        db.delete(ref)
    db.commit()

    for ref_data in payload.refeicoes:
        nova_ref = Refeicao(
            paciente_id = payload.paciente_id,
            nome        = ref_data.nome,
            horario     = ref_data.horario,
        )
        db.add(nova_ref)
        db.commit()
        db.refresh(nova_ref)

        db.add_all([
            ItemRefeicao(
                refeicao_id = nova_ref.id,
                alimento_id = item.id,
                quantidade  = item.quantidade,
            )
            for item in ref_data.itens
        ])

    db.commit()
    return {"status": "sucesso", "mensagem": "Plano alimentar salvo com sucesso!"}


@app.get("/dietas/{paciente_id}")
async def obter_dieta_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(obter_usuario_atual),
):
    refeicoes = db.query(Refeicao).filter(Refeicao.paciente_id == paciente_id).all()
    resultado = []

    for ref in refeicoes:
        itens_db = db.query(ItemRefeicao).filter(ItemRefeicao.refeicao_id == ref.id).all()
        lista_itens = []

        for item in itens_db:
            alimento = db.query(AlimentoTACO).filter(AlimentoTACO.id == item.alimento_id).first()
            if alimento:
                lista_itens.append({
                    "id":         alimento.id,
                    "nome":       alimento.nome,
                    "quantidade": item.quantidade,
                    "kcal_base":  alimento.kcal,
                    "carb_base":  alimento.carb,
                    "prot_base":  alimento.prot,
                    "gord_base":  alimento.gord,
                    "fibra_base": alimento.fibra,
                    "sodio_base": alimento.sodio,
                })

        resultado.append({
            "nome":    ref.nome,
            "horario": ref.horario,
            "itens":   lista_itens,
        })

    return resultado
