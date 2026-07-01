# 🍏 NutriSocial

> **Plataforma web de gestão clínica nutricional**, oferecendo aos profissionais da saúde a capacidade de centralizar o cadastro de pacientes, avaliações antropométricas, anamnese e a geração automatizada de planos alimentares e prontuários em PDF.

---

## 📖 Sobre o Projeto

O **NutriSocial** é um projeto acadêmico e prático desenvolvido para a disciplina de **Projeto Trainee** (PIESC) da UNINGÁ. A plataforma foi idealizada para digitalizar e otimizar a rotina de atendimentos nutricionais, substituindo o uso de planilhas dispersas por um sistema integrado, seguro e acessível na nuvem.

### 🎯 Objetivo

Garantir alta disponibilidade e precisão matemática no acompanhamento clínico individualizado, automatizando cálculos metabólicos (IMC e TMB baseados em Harris-Benedict) e entregando ao paciente um documento profissional e tangível de sua rotina alimentar.

---

## 🛠️ Tecnologias Utilizadas

O projeto foi construído utilizando uma arquitetura moderna de **Serviços Gerenciados (Cloud Computing)**, com a separação total entre a interface e as regras de negócio.

| Camada | Tecnologia | Detalhes Técnicos |
|--------|-----------|-------------------|
| **Back-End (API)** | Python 3 / FastAPI | Validação de dados assíncrona com Pydantic |
| **Banco de Dados** | PostgreSQL | Hospedado na nuvem via Neon.tech |
| **Front-End** | HTML5, CSS3, Vanilla JS | Componentização visual via Bootstrap 5 |
| **Segurança** | JWT (JSON Web Tokens) | Autenticação RBAC e criptografia via Passlib (Bcrypt) |
| **Engenharia de Doc.** | html2pdf.js | Motor de renderização em tela (`html2canvas`) |
| **Hospedagem (CI/CD)** | Render & Vercel | Deploy contínuo e integrado ao repositório |
| **Versionamento** | Git & GitHub | Fluxo baseado em Git Flow |

---

## 📁 Estrutura do Projeto

```text
NutriSocial/
├── app/                      # Lógica da API RESTful e persistência de dados
│   ├── main.py               # Configuração do FastAPI e rotas de segurança
│   ├── database.py           # Conexão com o PostgreSQL e modelos SQLAlchemy
│   ├── requirements.txt      # Gerenciamento de dependências Python
│   └── taco.json             # Base de dados oficial de alimentos (TACO)
├── frontend/                 # Aplicação Web (Interface Gráfica)
│   ├── index.html            # Dashboard gerencial
│   ├── login.html            # Porta de entrada e geração de Token
│   ├── cadastro.html         # Formulário de prontuário e anamnese
│   ├── antropometria.html    # Motor de cálculos físicos
│   ├── dieta.html            # Montagem estrutural e geração de PDF
│   ├── style.css             # Padronização de identidade visual
│   └── logo.png              # Ativos gráficos
├── .gitignore                # Regras de segurança de repositório
└── README.md                 # Documentação principal

```
---  

## 🚀 Como Rodar o Projeto (Ambiente Local)


### Pré-requisitos
- **Python 3.11+** instalado
- **Extensão Live Server** instalada no VS Code (para o Front-End)
- **Git** para versionamento

```bash
# 1. Clone o repositório
git clone [https://github.com/Mikeszs/NutriSocial.git](https://github.com/Mikeszs/NutriSocial.git)
cd NutriSocial
# 2. Entre na pasta da API
cd app
# 3. Crie e ative um ambiente virtual (Opcional, mas recomendado)
python -m venv .venv
source .venv/bin/activate  # No Windows use: .venv\Scripts\activate
# 4. Instale as dependências
pip install -r requirements.txt
# 5. Execute o servidor de desenvolvimento
uvicorn main:app --reload

```

Front-End (Interface Vanilla)

```bash

Com o VS Code aberto na pasta raiz do projeto, navegue até o diretório frontend/.
Clique com o botão direito no arquivo login.html.
Selecione "Open with Live Server".
O navegador abrirá automaticamente a aplicação conectada à API local.

```

```
```
## 👥 Equipe


| Nome | Função | Responsabilidade |
|------|--------|-----------------|
| **Miqueias Souza da Silva** | Full-Stack Developer | Modelagem do banco de dados, desenvolvimento da API RESTful, design da interface de usuário, engenharia de PDF e orquestração de deploy (Render/Vercel). |

## 🔀 Fluxo de Desenvolvimento e Gestão
- A gestão do código fonte seguiu os princípios ágeis de desenvolvimento, utilizando uma adaptação estrita do modelo Git Flow para garantir a integridade do ambiente de produção:

- main → Branch de Produção. Contém apenas código testado, estável e conectado aos pipelines de CI/CD (Render e Vercel) para atualização automática em nuvem.
- test → Branch de Homologação/Develop. Ambiente de integração e desenvolvimento diário, utilizado para testes de novas features (como autenticação JWT e regras de CSS) antes do Merge oficial.

## 📝 Licença e Finalidade
Este projeto possui finalidade acadêmica e de qualificação técnica, desenvolvido como requisito e comprovação de proficiência prática para o programa de Projeto Trainee.
