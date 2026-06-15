from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal, Paciente

# Cria o arquivo do banco de dados (nutrisocial.db) assim que o código rodar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NutriSocial API", description="API para gestão nutricional")

# Função que abre e fecha a conexão com o banco a cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def raiz():
    return {"mensagem": "O servidor do NutriSocial está online e conectado ao banco!"}

# Atualizamos a rota para receber os dados e salvar no banco de verdade
@app.post("/pacientes/")
async def criar_paciente(nome: str, objetivo: str, email: str = None, telefone: str = None, db: Session = Depends(get_db)):
    
    # Prepara o objeto do novo paciente
    novo_paciente = Paciente(
        nome=nome, 
        objetivo=objetivo,
        email=email,
        telefone=telefone
    )
    
    # Salva no banco de dados
    db.add(novo_paciente)
    db.commit()
    db.refresh(novo_paciente) # Puxa o ID gerado pelo banco
    
    return {
        "status": "sucesso",
        "mensagem": f"Paciente {novo_paciente.nome} cadastrado!",
        "dados": novo_paciente
    }