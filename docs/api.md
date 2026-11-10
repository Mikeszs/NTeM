# Referência da API

Base: `https://ntandm.onrender.com` (produção) ou `http://localhost:8000` (local). A documentação interativa gerada pelo FastAPI está em `/docs`; este arquivo é o resumo legível. A fonte única é `app/main.py`.

## Convenções

- Corpos em JSON, exceto `POST /auth/login`, que usa `application/x-www-form-urlencoded` com os campos `username` (o e-mail) e `password`.
- Rotas protegidas exigem o cabeçalho `Authorization: Bearer <access_token>`.
- Acesso **Autenticado** = qualquer usuário logado; **Profissional** = usuário com `role` igual a `profissional`.
- Erros de regra: `{"detail": "mensagem"}`. Erros de validação (422): `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}`, sem o valor recebido.

| Código | Significado |
|---|---|
| 400 | Dado inválido ou conflito de regra (e-mail já cadastrado, senha curta, link expirado) |
| 401 | Token ausente, inválido ou expirado; senha atual incorreta; login incorreto |
| 403 | Perfil sem permissão (`Acesso restrito a profissionais.`) |
| 404 | Recurso não encontrado |
| 422 | Corpo ou parâmetro fora do formato ou dos limites |
| 500 | Falha inesperada; a mensagem exibida ao usuário é genérica e o detalhe fica no log |

## Rotas

| Rota | Acesso | Função |
|---|---|---|
| `GET /` | Público | Verificação de que a API está no ar (usada pelo `keep-alive.yml`) |
| `POST /auth/cadastro` | Público | Cria usuário: `nome`, `email`, `senha`, `role` |
| `POST /auth/login` | Público | Retorna `access_token`, `token_type`, `role` e `nome` |
| `POST /auth/esqueci-senha` | Público | Corpo `{email}`. Responde sempre a mesma mensagem |
| `POST /auth/redefinir-senha` | Token do e-mail | Corpo `{token, senha_nova}` (mínimo de 6 caracteres) |
| `GET /perfil/me` | Autenticado | Dados do próprio usuário |
| `PUT /perfil/me` | Autenticado | Corpo `{nome, email}` |
| `PUT /perfil/senha` | Autenticado | Corpo `{senha_atual, senha_nova}` |
| `GET /pacientes/` | Autenticado | Lista pacientes |
| `GET /pacientes/{id}` | Autenticado | Detalha um paciente |
| `POST /pacientes/` | Profissional | Corpo `{nome, objetivo, email?, telefone?}` |
| `PUT /pacientes/{id}` | Profissional | Atualiza o paciente: `nome`, `objetivo`, `sexo` e `idade` são obrigatórios; `email`, `telefone` e as medidas atuais (peso, altura, cintura, quadril, abdômen) são opcionais |
| `GET /alimentos/` | Autenticado | Lista os alimentos TACO |
| `POST /importar-taco-completa/` | Profissional | Carga inicial de `taco.json`; aborta se já houver alimentos |
| `POST /dietas/` | Profissional | Substitui o plano alimentar do paciente (não há histórico de planos) |
| `GET /dietas/{paciente_id}` | Autenticado | Refeições e itens, com valores base por 100 g |
| `GET /dashboard/resumo` | Autenticado | Total de pacientes, com e sem dieta, e distribuição por objetivo |
| `GET /antropometria/formulas?sexo=M\|F` | Profissional | Catálogo de fórmulas e das medidas que cada uma exige |
| `POST /antropometria/calcular` | Profissional | Calcula sem gravar (retorno em tempo real da tela) |
| `POST /pacientes/{id}/avaliacoes` | Profissional | Calcula e grava uma avaliação no histórico; devolve 201 (ou 200 se for reenvio idêntico em até 30 s) |
| `GET /pacientes/{id}/avaliacoes?limite=10&deslocamento=0` | Profissional | Histórico, do mais recente ao mais antigo; `limite` de 1 a 50 |

## Avaliação antropométrica

Corpo de `POST /antropometria/calcular` e de `POST /pacientes/{id}/avaliacoes` (campos desconhecidos são rejeitados):

```json
{
  "sexo": "M",
  "formula": "petroski",
  "idade": 32,
  "peso": 83,
  "altura": 175,
  "dobras": {"subescapular": 12, "tricipital": 10, "suprailiaca": 11, "panturrilha": 8},
  "circunferencias": {"cintura": 90, "quadril": 104},
  "data_avaliacao": "2026-11-10"
}
```

- `sexo`: `M` ou `F`. `formula`: `pollock3`, `pollock7`, `petroski`, `guedes`, `durnin`, `faulkner`, `rfm`, `navy` ou `nenhuma` (padrão).
- Limites: idade 1 a 120; peso maior que 0 e até 500 kg; altura de 30 a 272 cm; dobra maior que 0 e até 100 mm; circunferência maior que 0 e até 250 cm. A data não pode ser futura.
- É preciso informar ao menos uma medida; caso contrário, 422.
- O resultado traz, entre outros campos: `imc`, `classificacao_imc`, `faixa_peso_ideal`, `rcq`, `risco_rcq`, `razao_cintura_altura`, `cmb`, `tmb`, `soma_dobras`, `densidade`, `percentual_gordura`, `peso_gordura`, `peso_residual`, `massa_livre_gordura`, além de `pendencias` (medidas que faltam para a fórmula) e `avisos` (por exemplo, idade fora da faixa de validade da fórmula).
- Ao gravar, as medidas informadas também atualizam o prontuário atual do paciente, na mesma transação.

As equações e referências estão em [antropometria-formulas.md](antropometria-formulas.md).
