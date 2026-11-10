# Arquitetura

O NTeM tem três camadas implantadas separadamente: o navegador, a API e o banco. O código é a fonte única do comportamento; este documento é um mapa para encontrá-lo.

```
Navegador (Vercel)  ──HTTPS + JSON──▶  API FastAPI (Render)  ──SQLAlchemy──▶  PostgreSQL (Neon)
 HTML, CSS, JS                          app/main.py                              pacientes, usuarios,
 Bootstrap 5.3                          app/antropometria.py                     avaliacoes, dietas
                                              │
                                              └──▶ Resend (e-mail de redefinição de senha)
```

## Estrutura de pastas

| Caminho | Responsabilidade |
|---|---|
| `app/main.py` | Cria o app FastAPI, configura CORS, define schemas Pydantic, autenticação JWT e todas as rotas |
| `app/database.py` | Conexão, sessão e modelos SQLAlchemy; lê `DATABASE_URL` do ambiente |
| `app/antropometria.py` | Fórmulas, classificações e o cálculo completo da avaliação; não acessa banco nem HTTP |
| `app/taco.json` | Base de alimentos TACO, importada por `POST /importar-taco-completa/` |
| `frontend/config.js` | Define `API_BASE` (local ou Render) conforme o endereço da página |
| `frontend/auth.js` | Guarda o JWT em `sessionStorage` e protege as páginas (`auth.exigir`) |
| `frontend/theme.js`, `style.css` | Tema claro e escuro por variáveis de cor |
| `frontend/*.html` | Uma tela por arquivo, com o script da tela dentro do próprio HTML |
| `tests/` | Testes automatizados (pytest) |

## Modelo de dados

| Tabela | Campos principais | Relações |
|---|---|---|
| `usuarios` | id, nome, email (único), senha_hash, role, reset_token_hash, reset_token_expira | — |
| `pacientes` | id, nome, email, telefone, objetivo, sexo, idade, peso, altura, cintura, quadril, abdomen | — |
| `avaliacoes_antropometricas` | id, paciente_id, profissional_id, data_avaliacao, criado_em, sexo, idade, peso, altura, formula, dobras (JSON), circunferencias (JSON), resultado (JSON) | N:1 com `pacientes` e `usuarios` |
| `alimentos_taco` | id, nome, kcal, carb, prot, gord, fibra, sodio | — |
| `refeicoes` | id, paciente_id, nome, horario | N:1 com `pacientes` |
| `itens_refeicao` | id, refeicao_id, alimento_id, quantidade | N:1 com `refeicoes` e `alimentos_taco` |

`pacientes` guarda as medidas **atuais** (usadas pela tela de dieta); `avaliacoes_antropometricas` guarda o **histórico**.

## Decisões de projeto

- **Cálculo no servidor.** Toda a antropometria é calculada em `app/antropometria.py`; o front-end só envia medidas e exibe o retorno. Nada que vem pronto do cliente é gravado.
- **Histórico imutável.** Cada avaliação salva é um registro novo, com as medidas e o resultado da época. Se uma fórmula for corrigida depois, as avaliações antigas continuam mostrando o que foi entregue ao paciente.
- **Perfil verificado no servidor.** As rotas de escrita clínica exigem o perfil `profissional` (dependência `obter_profissional` e verificações em `main.py`); esconder um botão na tela não é proteção.
- **Token em `sessionStorage`.** A sessão termina ao fechar a aba. O token expira em 60 minutos por padrão.
- **Redefinição de senha.** O token enviado por e-mail é aleatório; no banco fica só o hash SHA-256, com validade de 30 minutos e uso único. As respostas de login e de "esqueci minha senha" são genéricas para não revelar quais e-mails existem.
- **Tema por tokens.** `style.css` define variáveis semânticas; o tema escuro só as redefine. `theme.js` aplica `data-theme` e `data-bs-theme` juntos, para o Bootstrap 5.3 ativar seu modo escuro nativo.
- **Idempotência no salvamento da avaliação.** Um reenvio idêntico em até 30 segundos (duplo clique, nova tentativa de rede) devolve a mesma avaliação em vez de duplicar.
