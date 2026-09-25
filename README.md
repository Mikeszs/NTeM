# 🥗 NutriSocial (NTeM)
**Plataforma Web de Gestão Nutricional para Atendimento Social**

![Status](https://img.shields.io/badge/Status-Em_Homologação-success)
![Version](https://img.shields.io/badge/Version-0.2.0-blue)
![Python](https://img.shields.io/badge/Python-3%2B-yellow)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952b3)

O **NutriSocial** é uma plataforma de gestão clínica e prescrição dietética desenvolvida para centralizar e automatizar o atendimento nutricional filantrópico. O sistema foi concebido no âmbito do **Projeto de Integração Escola Comunidade (PIESC)**, voltado para as necessidades operacionais dos acadêmicos e formandos de Nutrição da **UNINGÁ**.

---

## 🎯 Objetivo e Contexto Social

Antes do NutriSocial, o atendimento filantrópico sofria com gargalos operacionais: o uso de Formulários do Google dispersos, cálculos manuais de metabolismo e consultas morosas a PDFs de centenas de páginas da Tabela TACO. Alternativas comerciais (como o WebDiet) mostraram-se economicamente inviáveis para um projeto universitário e social, limitando o plano gratuito a apenas 5 interações.

**A nossa solução:** Criar um ambiente digital de custo zero para a universidade, que possibilita aos acadêmicos de Nutrição:
1. **Triplicar a capacidade de atendimento** à população de baixa renda.
2. **Reduzir o tempo operacional (Time-on-Task)** através da automação de cálculos.
3. **Entregar prescrições profissionais** e padronizadas em PDF, aumentando a adesão dos pacientes ao tratamento.

---

## ✨ Funcionalidades Principais (MVP)

*   **Cadastro e Anamnese (CRUD):** Gestão centralizada de pacientes, histórico clínico, alergias e hábitos.
*   **Avaliação Antropométrica:** Cálculo instantâneo e automático de IMC e Taxa Metabólica Basal (TMB).
*   **Motor de Prescrição Dietética (TACO):** Banco de dados integrado com a Tabela Brasileira de Composição de Alimentos (TACO), calculando macronutrientes proporcionalmente à gramatura informada.
*   **Exportação em PDF:** Geração dinâmica de planos alimentares em documento padronizado pronto para impressão ou envio digital.
*   **Dashboard e Acessibilidade:** Painel interativo com métricas de pacientes e suporte nativo a **Dark Mode** (salvo no `localStorage`).
*   **Segurança (Auth JWT):** Proteção de rotas sensíveis e senhas criptografadas (bcrypt), com sistema de redefinição via e-mail.

---

## 🛠 Arquitetura e Stack Tecnológica

O projeto foi construído sob uma **arquitetura de 3 camadas (Three-tier)** focada em performance e custo zero (PaaS):

*   **Front-End (Apresentação):** HTML5, CSS3, JavaScript Vanilla, Bootstrap 5.3.
    *   *Hospedagem:* Vercel.
    *   *Roteamento:* Sistema inteligente via `config.js` que direciona a API para `localhost` no ambiente de desenvolvimento ou para a nuvem em produção.
*   **Back-End (Aplicação):** Python 3+, FastAPI, Pydantic, SQLAlchemy.
    *   *Hospedagem:* Render.
*   **Banco de Dados (Persistência):** PostgreSQL relacional (Normalizado em 3FN).
    *   *Hospedagem:* Neon.tech

---

## ⚙️ Metodologia e Versionamento

O fluxo de trabalho alia as melhores práticas da Engenharia de Software:
*   **Metodologia Ágil:** Desenvolvimento baseado no ciclo *Build-Measure-Learn* (Lean Startup) e priorização de escopo pelo método MoSCoW.
*   **Gestão de Projetos:** Utilização do framework **FlowED** (Nível 2) para planejamento e homologação.
*   **Versionamento:** Adoção do fluxo **Dec-B (Branches Desacopladas)**, isolando o desenvolvimento local e ferramentas de automação na branch `test`, para garantir que a branch `main` de produção receba apenas código limpo, semântico e funcional.
*   **DevOps (CI/CD):** Pipeline de entrega contínua vinculado ao GitHub, publicando atualizações na Vercel e no Render automaticamente a cada *merge* na branch principal.

---



# 🛠 NutriSocial — Ambiente Local

Guia único e direto para clonar, configurar e rodar o projeto localmente.

---

## Estrutura do projeto

```
NTeM/
├── app/                  ← Backend (FastAPI)
│   ├── main.py
│   ├── database.py
│   └── taco.json
├── frontend/              ← Frontend (HTML/JS puro)
│   ├── login.html
│   ├── index.html
│   ├── ...
│   ├── config.js         ← detecta local x produção automaticamente
│   └── auth.js
├── .env.example           ← modelo — copie para .env
├── .gitignore
├── requirements.txt
├── start.ps1               ← sobe o backend (Windows)
└── start.sh                 ← sobe o backend (Mac/Linux)
```

**Importante:** existe UMA pasta do projeto. Nunca clone dentro de outra pasta que já tenha o projeto — foi isso que causou o erro anterior (`.env` não encontrado porque o terminal estava numa subpasta duplicada).

---

## Setup — só na primeira vez

### 1. Clonar a branch `test`

```bash
git clone -b test https://github.com/Mikeszs/NTeM.git
cd NTeM
```

### 2. Criar o ambiente virtual Python

```bash
python -m venv .venv
```

Isso cria a pasta `.venv/` — ela fica **só na sua máquina**, nunca vai para o GitHub (já está no `.gitignore`).

### 3. Ativar o ambiente virtual e instalar as dependências

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Você só faz isso **uma vez**. Da próxima vez que abrir o VS Code, o `.venv` já vai estar lá com tudo instalado — não precisa rodar `pip install` de novo, a menos que o `requirements.txt` mude.

### 4. Criar o arquivo `.env`

```bash
# Copia o modelo
cp .env.example .env       # Mac/Linux
copy .env.example .env     # Windows
```

Abra o `.env` no VS Code e preencha com os valores reais (pegue no painel do Render, em **Environment**):

```
DATABASE_URL=postgresql://neondb_owner:SUA_SENHA_REAL@ep-small-math-acye4350.sa-east-1.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=qualquer_string_longa_aleatoria
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

> ⚠️ O `.env` nunca é commitado — ele já está no `.gitignore`. Isso é intencional: cada pessoa/máquina tem o seu.

---

## Uso do dia a dia — depois do setup inicial

### Rodar o backend

**Windows:**
```powershell
.\start.ps1
```

**Mac/Linux:**
```bash
./start.sh
```

Isso ativa o `.venv` e sobe o servidor automaticamente. **Não precisa mais digitar `$env:DATABASE_URL` nem nada parecido** — o arquivo `.env` é carregado sozinho pelo `database.py` através da biblioteca `python-dotenv`.

Verifique: abra `http://127.0.0.1:8000/docs` — o Swagger deve aparecer.

### Rodar o frontend

No VS Code, clique com o botão direito em `frontend/login.html` → **Open with Live Server**.

O browser abre em `http://127.0.0.1:5500/frontend/login.html`. O `config.js` detecta automaticamente que está em localhost e aponta as chamadas para `http://127.0.0.1:8000` (seu backend local).

---

## Fluxo de trabalho com Git

```
main   ← produção (Render + Vercel fazem deploy automático daqui)
test   ← você trabalha e testa aqui
```

### Rotina normal

```bash
# 1. Sempre comece atualizando a branch test
git checkout test
git pull origin test

# 2. Faça as alterações no código, teste localmente com start.ps1 / start.sh

# 3. Quando estiver funcionando, commit e push na test
git add .
git commit -m "descrição da alteração"
git push origin test

# 4. Quando aprovar, manda para produção
git checkout main
git merge test
git push origin main
git checkout test        # volta para test para continuar trabalhando
```

---

## O que NUNCA vai para o GitHub (proteção automática pelo `.gitignore`)

| Arquivo/pasta | Por quê |
|---|---|
| `.env` | Contém a senha real do banco e a chave secreta |
| `.venv/` | Ambiente virtual — específico de cada máquina, muito pesado |
| `__pycache__/` | Cache do Python, gerado automaticamente |
| `*.db` | Banco de dados local, se usado em testes isolados |
| `.vscode/` | Configurações pessoais do editor |

O que **vai** para o GitHub: `.env.example` (só o modelo, sem senha real), todo o código-fonte, `requirements.txt`, e os scripts `start.ps1` / `start.sh`.

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `DATABASE_URL não encontrada` | `.env` não existe ou está na pasta errada | Confirme que `.env` está na **raiz** do projeto (mesmo nível do `requirements.txt`) |
| "Erro de conexão com o servidor de autenticação" no login local | CORS bloqueando a porta do Live Server | Confirme que `main.py` tem `http://127.0.0.1:5500` na lista `allow_origins` |
| `ModuleNotFoundError` ao rodar o backend | Ambiente virtual não está ativo | Rode `start.ps1` / `start.sh` — eles ativam o `.venv` automaticamente |
| Alterações no `requirements.txt` não aparecem | Dependências não foram reinstaladas | Rode `pip install -r requirements.txt` novamente com o `.venv` ativo |
