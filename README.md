# NTeM — NutriSocial

Plataforma web para estudantes e formandos de Nutrição gerenciarem pacientes e planos alimentares, desenvolvida como produto real do Projeto Trainee para ADS e do PIESC (Programa de Integração Escola Comunidade), em parceria com os Acadêmicos do curso de  **Nutrição da UNINGÁ**.

**Autor:** Miqueias Souza da Silva

> Este README descreve o estado do código na branch `main`. Fatos que dependem de configuração externa (painéis do Render, Vercel e Neon) estão marcados como "a confirmar".

---

## 1. Objetivo

O NTeM tem como objetivo permitir que estudantes de Nutrição realizem, de forma ágil e organizada, o atendimento de um paciente de baixa renda: cadastro, avaliação antropométrica com cálculos automáticos e montagem de um plano alimentar personalizado com base na Tabela TACO, gerando ao final um documento em PDF pronto para entrega ao paciente.

O sistema resolve um problema real dos acadêmicos de Nutrição: a dificuldade de oferecer orientação nutricional organizada, sem depender de cálculos manuais e planilhas soltas durante o atendimento.

---

## 2. Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3 + FastAPI |
| Banco de dados | PostgreSQL (hospedado no Neon.tech), acessado via SQLAlchemy (ORM) |
| Front-end | HTML, CSS e JavaScript, com Bootstrap 5.3 |
| Autenticação | JWT (JSON Web Token), com verificação do perfil no back-end e proteção de rota no front-end |
| Geração de PDF | Layout de impressão aberto em nova aba, com `window.print()` (o usuário escolhe "Salvar como PDF") |
| E-mail transacional | Resend (fluxo de recuperação de senha) |
| Testes | pytest com `TestClient` do FastAPI (ver seção 5) |
| Hospedagem back-end | Render — `https://ntandm.onrender.com` |
| Hospedagem front-end | Vercel — `https://ntem.vercel.app` |
| Controle de versão | Git / GitHub — `https://github.com/Mikeszs/NTeM` (branches `main` e `test`) |
| Base nutricional | Tabela TACO (Tabela Brasileira de Composição de Alimentos), cerca de 282 alimentos em `app/taco.json` |

---

## 3. Estrutura do repositório

```
app/
  main.py            API FastAPI: CORS, autenticação, schemas e rotas
  database.py        Conexão SQLAlchemy e modelos
  antropometria.py   Fórmulas e cálculos antropométricos (fonte única dos cálculos)
  taco.json          Base de alimentos TACO
frontend/            Telas HTML, config.js, auth.js, theme.js e style.css
tests/               Testes automatizados (pytest)
docs/                Documentação (ver docs/README.md)
keep-alive.yml       Rotina para acordar a API do Render (ver seção 6)
requirements.txt     Dependências do back-end
```

---

## 4. Como executar

### 4.1 Acesso direto (produto publicado)

- **Front-end (aplicação):** https://ntem.vercel.app
- **Back-end (API):** https://ntandm.onrender.com

> O back-end roda em plano gratuito do Render, que hiberna por inatividade. O primeiro acesso após um período sem uso pode levar até cerca de um minuto (cold start). É uma limitação conhecida, não um erro do sistema.

### 4.2 Execução local (para desenvolvimento)

**Pré-requisitos:** Python 3.10+ e uma instância PostgreSQL (local ou Neon.tech).

```bash
git clone https://github.com/Mikeszs/NTeM.git
cd NTeM
pip install -r requirements.txt
```

Crie um arquivo `.env` **na raiz do projeto** (não versionado), com:

```
DATABASE_URL=postgresql://usuario:senha@host:porta/banco
SECRET_KEY=valor-longo-e-aleatorio
```

Gere a `SECRET_KEY` com `python -c "import secrets; print(secrets.token_hex(32))"`. Variáveis opcionais: `ACCESS_TOKEN_EXPIRE_MINUTES` (padrão 60), `RESEND_API_KEY`, `RESEND_FROM_EMAIL` e `FRONTEND_URL`. Sem `RESEND_API_KEY`, o e-mail de redefinição de senha não é enviado.

Suba a API **de dentro da pasta `app/`**, porque `main.py` importa `database` e `antropometria` diretamente e abre `taco.json` por caminho relativo:

```bash
cd app
uvicorn main:app --reload      # API em http://localhost:8000; documentação interativa em /docs
```

Front-end: abra a pasta `frontend/` com um servidor local (por exemplo, a extensão Live Server do VS Code, porta 5500). O arquivo `config.js` detecta `localhost` e aponta sozinho para `http://localhost:8000`; não é preciso alterar código. A API só aceita requisições das origens listadas em `allow_origins` no `main.py` (produção e `localhost:5500`).

> As variáveis sensíveis (string de conexão do banco, chave JWT, chave do Resend) nunca ficam no código-fonte: são configuradas por variável de ambiente, localmente e nos painéis do Render e do Vercel.

---

## 5. Testes

```bash
pip install pytest
pytest
```

Os testes usam um SQLite temporário (nunca o banco real) e cobrem as fórmulas antropométricas e a API de antropometria (cálculo, histórico, permissões e validação de entradas). Rotas de autenticação, pacientes e dieta ainda não têm testes próprios, e não há pipeline de integração contínua que rode os testes automaticamente.

---

## 6. Recursos entregues

| Código | Recurso | Situação |
|---|---|---|
| RF01 | Gestão de pacientes (cadastro e listagem) | Entregue. A tela não permite editar os dados cadastrais depois de salvos |
| RF02 | Registro de anamnese (histórico clínico, alergias, hábitos) | **Parcial.** A tela existe, mas os campos clínicos não são enviados nem gravados; só nome, objetivo, e-mail e telefone são salvos |
| RF03 | Avaliação antropométrica com histórico por data | Entregue: cada avaliação salva gera um registro imutável, com as medidas e o resultado da época |
| RF04 | Cálculo automático de IMC | Entregue |
| RF05 | Cálculo de TMB (Harris-Benedict) | Entregue. O gasto energético total (GET) **não** é calculado |
| RF06 | Montagem de dieta com busca de alimentos (TACO) e totais em tempo real | Entregue |
| RF07 | Exportação do plano alimentar em PDF | Entregue, pela impressão do navegador |
| — | Fórmulas de percentual de gordura (Pollock 3 e 7, Petroski, Guedes, Durnin e Womersley, Faulkner, RFM e US Navy) | Entregue (ver `docs/antropometria-formulas.md`) |
| — | Autenticação e proteção de rotas via JWT | Entregue |
| — | Recuperação e troca de senha (e-mail via Resend) | Entregue |
| — | Modo escuro e dashboard com métricas | Entregue |

Fluxo principal coberto pelo sistema:

```
Login → Cadastro do Paciente → Antropometria (IMC, TMB, % de gordura)
      → Montagem da Dieta (busca TACO + cálculo em tempo real) → Geração do PDF
```

---

## 7. Evidências dos principais fluxos

> As evidências em vídeo do funcionamento da plataforma foram registradas separadamente e acompanham a entrega do trabalho bimestral.

1. **Tela e fluxo principal:** login do estudante, seleção de um paciente e tela de montagem da dieta carregada com os dados do paciente.
2. **Operação importante:** adição de um alimento da base TACO a uma refeição, com a quantidade em gramas e atualização em tempo real dos totais de calorias, carboidratos, proteínas, gorduras, fibras e sódio, seguida da geração do plano em PDF.
3. **Situações inválidas:** alimento sem quantidade (`"Preencha o alimento e a quantidade."`) e PDF sem paciente selecionado (`"Selecione um paciente para gerar o documento."`).
4. **Versão apresentada:** v1.0 (3º bimestre), branch `main`, publicada em `ntem.vercel.app` e `ntandm.onrender.com`.

---

## 8. Problemas conhecidos e limitações

- **Cold start do back-end:** o plano gratuito do Render hiberna a API após inatividade, e o primeiro acesso é lento. O arquivo `keep-alive.yml` na raiz do repositório foi escrito para acordar a API a cada 14 minutos, mas o GitHub Actions só executa workflows que estão em `.github/workflows/`; enquanto o arquivo ficar na raiz, a rotina **não roda** (a confirmar no painel Actions).
- **Anamnese não gravada** e **GET não calculado** (ver seção 6).
- **Testes parciais:** só a antropometria tem testes automatizados; o restante é validado manualmente. Um teste (`test_registrar_avaliacao_grava_snapshot_e_atualiza_prontuario`) compara a data local com a data UTC e falha quando as duas diferem (por exemplo, à noite no horário de Brasília).
- **Migrações de banco manuais:** `create_all()` do SQLAlchemy cria tabelas novas, mas não altera tabelas existentes; mudanças estruturais exigem `ALTER TABLE` manual ou, no futuro, Alembic. Ver `docs/guia-do-desenvolvedor.md`.
- **Sem ambiente de homologação** separado da produção.
- **Dois perfis apenas:** `profissional` e `paciente`. As rotas de escrita clínica exigem `profissional`; não há perfis de administrador ou professor.
- **Sem consulta clínica individual:** o sistema é uma ferramenta de apoio e não substitui o acompanhamento de um nutricionista.

## 9. O que ficou para depois

- Perfis com mais níveis de permissão (administrador, professor, aluno).
- Gravação dos campos de anamnese e cálculo do GET.
- Migrações de banco versionadas com Alembic.
- Pipeline de integração contínua que rode os testes e ampliação da cobertura.
- Modernização do front-end (migração gradual para React + TypeScript + Vite).

---

## 10. Documentação

Veja `docs/README.md`: manual do usuário, guia do desenvolvedor, referência da API, arquitetura e fórmulas antropométricas.

## 11. Repositório e links

- **Código-fonte:** https://github.com/Mikeszs/NTeM
- **Aplicação (front-end):** https://ntem.vercel.app
- **API (back-end):** https://ntandm.onrender.com
