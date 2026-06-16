from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import engine, Base, SessionLocal, Paciente, AlimentoTACO, Refeicao, ItemRefeicao
import json
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NutriSocial API", description="API para gestão nutricional")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CONTRATOS PYDANTIC
class PacienteCreate(BaseModel):
    nome: str
    objetivo: str
    email: str = None
    telefone: str = None

class PacienteUpdate(BaseModel):
    nome: str
    objetivo: str
    email: str = None
    telefone: str = None
    sexo: str
    idade: int
    peso: float
    altura: float
    cintura: float = 0.0
    quadril: float = 0.0
    abdomen: float = 0.0

class ItemDietaCreate(BaseModel):
    id: int
    quantidade: float

class RefeicaoCreate(BaseModel):
    nome: str
    horario: str
    itens: List[ItemDietaCreate]

class DietaPayload(BaseModel):
    paciente_id: int
    refeicoes: List[RefeicaoCreate]

@app.get("/")
async def raiz():
    return {"mensagem": "O servidor do NutriSocial está online e conectado ao banco!"}

# --- ROTAS DE PACIENTES ---
@app.get("/pacientes/")
async def listar_pacientes(db: Session = Depends(get_db)):
    return db.query(Paciente).all()

@app.get("/pacientes/{paciente_id}")
async def obter_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente

@app.post("/pacientes/")
async def criar_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    novo_paciente = Paciente(nome=paciente.nome, objetivo=paciente.objetivo, email=paciente.email, telefone=paciente.telefone)
    db.add(novo_paciente)
    db.commit()
    db.refresh(novo_paciente)
    return {"status": "sucesso", "mensagem": "Paciente cadastrado!", "dados": novo_paciente}

@app.put("/pacientes/{paciente_id}")
async def atualizar_paciente(paciente_id: int, dados: PacienteUpdate, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    paciente.nome = dados.nome
    paciente.objetivo = dados.objetivo
    paciente.email = dados.email
    paciente.telefone = dados.telefone
    paciente.sexo = dados.sexo
    paciente.idade = dados.idade
    paciente.peso = dados.peso
    paciente.altura = dados.altura
    paciente.cintura = dados.cintura
    paciente.quadril = dados.quadril
    paciente.abdomen = dados.abdomen
    
    db.commit()
    db.refresh(paciente)
    return {"status": "sucesso", "mensagem": "Prontuário e medidas atualizados com sucesso!", "dados": paciente}

# --- ROTAS DA DIETA E TACO ---
@app.get("/alimentos/")
async def listar_alimentos(db: Session = Depends(get_db)):
    return db.query(AlimentoTACO).all()

@app.post("/importar-taco-completa/")
async def importar_taco_completa(db: Session = Depends(get_db)):
    quantidade = db.query(AlimentoTACO).count()
    if quantidade > 0:
        return {"mensagem": f"O banco já possui {quantidade} alimentos cadastrados. Operação abortada para evitar duplicidade."}

    caminho_arquivo = "taco.json"
    if not os.path.exists(caminho_arquivo):
        raise HTTPException(status_code=404, detail="Arquivo taco.json não encontrado na pasta do servidor.")

    with open(caminho_arquivo, "r", encoding="utf-8") as file:
        dados_taco = json.load(file)

    alimentos_para_inserir = []
    for item in dados_taco:
        novo_alimento = AlimentoTACO(
            nome=item.get("nome", "Sem Nome"),
            kcal=float(item.get("kcal", 0)),
            carb=float(item.get("carb", 0)),
            prot=float(item.get("prot", 0)),
            gord=float(item.get("gord", 0)),
            fibra=float(item.get("fibra", 0)), 
            sodio=float(item.get("sodio", 0))  
        )
        alimentos_para_inserir.append(novo_alimento)
    
    db.add_all(alimentos_para_inserir)
    db.commit()
    return {"status": "sucesso", "mensagem": f"Carga concluída! {len(alimentos_para_inserir)} alimentos importados."}

@app.post("/dietas/")
async def salvar_dieta(payload: DietaPayload, db: Session = Depends(get_db)):
    refeicoes_antigas = db.query(Refeicao).filter(Refeicao.paciente_id == payload.paciente_id).all()
    for ref in refeicoes_antigas:
        db.query(ItemRefeicao).filter(ItemRefeicao.refeicao_id == ref.id).delete()
        db.delete(ref)
    db.commit()

    for ref_data in payload.refeicoes:
        nova_refeicao = Refeicao(paciente_id=payload.paciente_id, nome=ref_data.nome, horario=ref_data.horario)
        db.add(nova_refeicao)
        db.commit()
        db.refresh(nova_refeicao)

        for item_data in ref_data.itens:
            novo_item = ItemRefeicao(refeicao_id=nova_refeicao.id, alimento_id=item_data.id, quantidade=item_data.quantidade)
            db.add(novo_item)
            
    db.commit()
    return {"status": "sucesso", "mensagem": "Plano alimentar guardado com sucesso!"}

@app.get("/dietas/{paciente_id}")
async def obter_dieta_paciente(paciente_id: int, db: Session = Depends(get_db)):
    refeicoes = db.query(Refeicao).filter(Refeicao.paciente_id == paciente_id).all()
    resultado = []
    for ref in refeicoes:
        itens_db = db.query(ItemRefeicao).filter(ItemRefeicao.refeicao_id == ref.id).all()
        lista_itens = []
        for item in itens_db:
            alimento = db.query(AlimentoTACO).filter(AlimentoTACO.id == item.alimento_id).first()
            if alimento:
                lista_itens.append({
                    "id": alimento.id, 
                    "nome": alimento.nome, 
                    "quantidade": item.quantidade,
                    "kcal_base": alimento.kcal, 
                    "carb_base": alimento.carb, 
                    "prot_base": alimento.prot, 
                    "gord_base": alimento.gord,
                    "fibra_base": alimento.fibra, # AGORA RETORNA A FIBRA
                    "sodio_base": alimento.sodio  # AGORA RETORNA O SÓDIO
                })
        resultado.append({"nome": ref.nome, "horario": ref.horario, "itens": lista_itens})
    return resultado