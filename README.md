# NTeM — NutriSocial

Plataforma web para estudantes e formandos de Nutrição gerenciarem pacientes e planos alimentares, desenvolvida como produto real do Projeto Trainee para ADS e do PIESC (Programa de Integração Escola Comunidade), em parceria com a Entidade Social **Nutrição Acessível**.

**Autor:** Miqueias Souza da Silva

---

## 1. Objetivo

O NTeM tem como objetivo permitir que estudantes de Nutrição realizem, de forma ágil e organizada, o atendimento completo de um paciente de baixa renda: cadastro, anamnese, avaliação antropométrica, cálculos metabólicos automáticos e montagem de um plano alimentar personalizado com base na Tabela TACO, gerando ao final um documento em PDF pronto para entrega ao paciente.

O sistema resolve um problema real da ES Nutrição Acessível: a dificuldade de oferecer orientação nutricional organizada e gratuita, sem depender de cálculos manuais e planilhas soltas durante o atendimento.

---

## 2. Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3 + FastAPI |
| Banco de dados | PostgreSQL (hospedado no Neon.tech), acessado via SQLAlchemy (ORM) |
| Front-end | HTML, CSS e JavaScript, com Bootstrap 5.3 |
| Autenticação | JWT (JSON Web Token), com proteção de rota no front-end e validação no back-end |
| Geração de PDF | html2pdf.js (no navegador, a partir de um layout de prontuário renderizado em DOM) |
| E-mail transacional | Resend (fluxo de recuperação de senha) |
| Hospedagem back-end | Render — `https://ntandm.onrender.com` |
| Hospedagem front-end | Vercel — `https://ntem.vercel.app` |
| Controle de versão | Git / GitHub — `https://github.com/Mikeszs/NTeM` (branches `main` e `test`) |
| Base nutricional | Tabela TACO (Tabela Brasileira de Composição de Alimentos), aprox. 282 alimentos validados |

---

## 3. Como executar

### 3.1 Acesso direto (produto publicado)

O produto já está publicado e acessível, sem necessidade de instalação:

- **Front-end (aplicação):** https://ntem.vercel.app
- **Back-end (API):** https://ntandm.onrender.com

> ⚠️ O back-end roda em plano gratuito do Render, que hiberna por inatividade. O primeiro acesso após um período sem uso pode levar alguns segundos a mais para responder (cold start) — isso é uma limitação conhecida, não um erro do sistema.

### 3.2 Execução local (para desenvolvimento)

**Pré-requisitos:** Python 3.10+, Node/npm (opcional, apenas se for usar um servidor local para o front-end) e uma instância PostgreSQL (local ou Neon.tech).

```bash
# Clonar o repositório
git clone https://github.com/Mikeszs/NTeM.git
cd NTeM

# Back-end
cd backend
pip install -r requirements.txt

# Configurar variáveis de ambiente (arquivo .env, não versionado)
# DATABASE_URL=postgresql://usuario:senha@host:porta/banco
# JWT_SECRET=chave-secreta-aqui
# RESEND_API_KEY=chave-do-resend

# Subir a API localmente
uvicorn main:app --reload

# Front-end
cd ../frontend
# Basta abrir os arquivos .html em um servidor local (ex.: Live Server)
# ou apontar o auth.js/dieta.js para a URL do back-end local
```

> As variáveis sensíveis (string de conexão do banco, chave JWT, chave do Resend) nunca ficam no código-fonte — são configuradas por variável de ambiente, tanto localmente quanto nos painéis do Render/Vercel em produção.

---

## 4. Recursos entregues

| Código | Recurso | Situação |
|---|---|---|
| RF01 | Gestão de Pacientes (cadastro, edição e listagem) | ✅ Entregue |
| RF02 | Registro de Anamnese (histórico clínico, alergias, hábitos) | ✅ Entregue |
| RF03 | Avaliação Antropométrica com histórico por data | ✅ Entregue |
| RF04 | Cálculo automático de IMC | ✅ Entregue |
| RF05 | Cálculo de TMB e GET (fórmula de Harris-Benedict) | ✅ Entregue |
| RF06 | Montagem de dieta com busca de alimentos (TACO) e totais em tempo real | ✅ Entregue |
| RF07 | Exportação do plano alimentar em PDF | ✅ Entregue |
| — | Autenticação e proteção de rotas via JWT | ✅ Entregue |
| — | Recuperação de senha via e-mail (Resend) | ✅ Entregue |
| — | Modo escuro (dark mode) | ✅ Entregue |
| — | Dashboard com métricas e totais de macronutrientes | ✅ Entregue |

Fluxo principal coberto pelo sistema:

```
Login → Seleção/Cadastro de Paciente → Anamnese → Antropometria (IMC/TMB/GET)
      → Montagem da Dieta (busca TACO + cálculo em tempo real) → Geração do PDF
```

---

## 5. Evidências dos principais fluxos

> As evidências em vídeo do funcionamento completo da plataforma (gravação de uso real) já foram registradas separadamente e acompanham esta entrega, conforme solicitado no trabalho bimestral.

Os seguintes fluxos estão demonstrados nas evidências:

1. **Tela/fluxo principal:** login do estudante → seleção de um paciente → tela de montagem da dieta carregada com os dados do paciente selecionado.
2. **Operação importante:** adição de um alimento da base TACO a uma refeição, informando a quantidade em gramas, com atualização em tempo real dos totais de calorias, carboidratos, proteínas, gorduras, fibras e sódio da refeição — seguida da geração do plano alimentar em PDF.
3. **Teste de erro / situação inválida:** tentativa de adicionar um alimento sem selecionar a quantidade (ou com quantidade inválida), demonstrando a validação que impede o registro e o alerta exibido ao usuário (`"Preencha o alimento e a quantidade."`); e tentativa de gerar o PDF sem um paciente selecionado, demonstrando o bloqueio correspondente (`"Selecione um paciente para gerar o documento."`).
4. **Identificação da versão apresentada:** v1.0 — 3º Bimestre, branch `main` do repositório `github.com/Mikeszs/NTeM`, publicada em `ntem.vercel.app` (front-end) e `ntandm.onrender.com` (back-end).

---

## 6. Problemas conhecidos e limitações

- **Cold start do back-end:** por estar em plano gratuito do Render, a API hiberna após um período de inatividade, causando lentidão no primeiro acesso.
- **Sem testes automatizados:** a validação do sistema ainda é feita de forma manual; não há suíte de testes unitários ou de integração.
- **Migrações de banco manuais:** alterações estruturais no banco de dados exigem ajuste manual, pois o `create_all()` do SQLAlchemy não altera tabelas já existentes.
- **Sem ambiente de homologação:** não há um ambiente de teste publicado separado da produção; validações antes do deploy são feitas localmente ou diretamente no ambiente de produção.
- **Login com perfil único:** não há diferentes níveis de permissão (administrador, professor, aluno) — o acesso é simples, voltado ao perfil de estudante/profissional, conforme escopo definido para o MVP.
- **Sem consulta clínica individual:** o sistema é uma ferramenta de apoio ao atendimento e não substitui o acompanhamento presencial de um nutricionista.

## 7. O que ficou para depois (fora desta entrega)

- Login com múltiplos níveis de permissão (administrador, professor, aluno).
- Migrações de banco versionadas com Alembic.
- Pipeline de integração contínua (CI) e testes automatizados.
- Modernização do front-end (migração gradual para React + TypeScript + Vite).

---

## 8. Confirmação do que foi atendido

O produto entregue cobre, de ponta a ponta, o fluxo de atendimento definido como escopo do MVP: cadastro do paciente, anamnese, antropometria com cálculos automáticos, montagem de dieta com base oficial (TACO) e geração do plano alimentar em PDF — todos os sete Requisitos Funcionais (RF01 a RF07) definidos no planejamento do projeto foram implementados e estão em funcionamento na versão publicada. As limitações e os itens deixados para etapas futuras estão listados nas seções 6 e 7 acima, de forma transparente para o cliente/usuário final.

---

## 9. Repositório e links

- **Código-fonte:** https://github.com/Mikeszs/NTeM
- **Aplicação (front-end):** https://ntem.vercel.app
- **API (back-end):** https://ntandm.onrender.com
