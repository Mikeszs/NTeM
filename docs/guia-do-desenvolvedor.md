# Guia do desenvolvedor

Este guia responde às perguntas de quem vai continuar o projeto. Ele descreve o que o código faz hoje; o que ainda não existe aparece marcado como **não existe hoje**.

## 1. Como o front-end se comunica com o back-end

1. Cada tela carrega `config.js`, que define `API_BASE`: `http://localhost:8000` quando a página roda em `localhost` ou em IP local, e `https://ntandm.onrender.com` nos demais casos.
2. Após o login, `auth.js` guarda o JWT em `sessionStorage`. A tela chama `auth.exigir()` ao abrir; sem token, redireciona para o login.
3. Cada chamada usa `fetch(`${API_BASE}/rota`, { headers: { Authorization: `Bearer ${auth.token()}` } })`.
4. O navegador só consegue chamar a API se a origem da página estiver em `allow_origins` (CORS), em `app/main.py`. **Ao publicar o front-end em outro endereço, inclua-o nessa lista.**

## 2. Caminho de uma requisição

```
fetch (tela) → CORS (middleware) → rota FastAPI → Depends(obter_usuario_atual)   valida o JWT e carrega o usuário
             → Depends(get_db)   abre a sessão SQLAlchemy
             → validação do corpo (Pydantic) → regra de negócio → banco (PostgreSQL)
             → JSON de resposta → a tela trata o status (200, 401, 403, 422...)
```

Um 401 indica sessão expirada: as telas avisam e pedem novo login (o tratamento ainda varia entre telas: a antropometria redireciona, a dieta exibe um aviso). Um 422 traz a lista `detail` com o campo (`loc`) e a mensagem; a tela de antropometria mostra cada mensagem junto ao campo correspondente.

## 3. Onde implementar uma nova funcionalidade

| O que muda | Onde |
|---|---|
| Nova tabela ou coluna | Modelo em `app/database.py` (e a migração manual da seção 5) |
| Formato do corpo e limites | Classe Pydantic em `app/main.py` |
| Regra de negócio complexa | Módulo próprio em `app/`, como `antropometria.py`, e não dentro da rota |
| Nova rota | `app/main.py`, na seção da área correspondente |
| Nova tela | Arquivo `.html` em `frontend/`, com `auth.exigir()` e o link no menu lateral (o menu está repetido em cada página) |
| Teste | `tests/` |

## 4. Como adicionar uma nova rota

Exemplo ilustrativo (a rota `/pacientes/{id}/resumo` não existe hoje):

```python
@app.get("/pacientes/{paciente_id}/resumo")
async def resumo_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(obter_profissional),   # 401 sem token, 403 sem perfil profissional
):
    """Propósito, perfil exigido, retorno e erros possíveis (404)."""
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return {"id": paciente.id, "nome": paciente.nome}
```

Checklist: perfil exigido no servidor (`obter_profissional` ou verificação de `role`); corpo validado por Pydantic com limites; mensagem de erro amigável, sem detalhe técnico; consultas sem `SELECT *` desnecessário e paginadas se a lista puder crescer; transação única quando a operação grava em mais de uma tabela; teste em `tests/` com perfil permitido, perfil sem permissão e entrada inválida.

## 5. Como alterar o banco sem perder dados

`Base.metadata.create_all()` cria tabelas que **não existem**, mas **não altera** tabelas existentes. Por isso, adicionar uma coluna ao modelo não a cria no banco de produção. Alembic **não existe hoje**; o procedimento manual é:

1. Faça um backup do banco (`pg_dump`) antes de qualquer alteração.
2. Escreva o `ALTER TABLE` (ou `CREATE TABLE`) e guarde o script no repositório.
3. Teste o script em uma cópia do banco, nunca direto em produção.
4. Atualize o modelo em `database.py` para refletir o banco.
5. Aplique o script em produção e só depois publique o código que usa a coluna.
6. Colunas novas em tabelas com dados devem aceitar `NULL` ou ter valor padrão.

Não remova nem renomeie colunas sem avaliar o histórico: as avaliações antropométricas guardam o resultado da época em JSON de propósito, para continuarem corretas mesmo se uma fórmula mudar.

## 6. Como configurar e publicar uma nova versão

- **Ambientes.** `main` é produção e `test` é desenvolvimento. Não existe ambiente de homologação separado.
- **Variáveis.** `DATABASE_URL` e `SECRET_KEY` são obrigatórias; `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `FRONTEND_URL` e `ACCESS_TOKEN_EXPIRE_MINUTES` são opcionais. No Render, ficam no painel do serviço. Nunca as coloque no código.
- **Fluxo sugerido.** Trabalhe em uma branch, rode `pytest`, abra um Pull Request para `main` e revise antes de aceitar.
- **Publicação.** O front-end (pasta `frontend/`) é servido pelo Vercel e a API (`app/`) pelo Render. Se a publicação é automática a cada push na `main` é uma configuração dos painéis e **está a confirmar**; o repositório não tem arquivo que a defina.
- **Keep-alive.** O `keep-alive.yml` está na raiz; o GitHub Actions só executa workflows em `.github/workflows/`. Mova o arquivo para lá para a rotina funcionar.

## 7. Como verificar se uma funcionalidade está funcionando

**Testes automatizados** (cobrem fórmulas e a API de antropometria):

```bash
pip install pytest
pytest
```

Eles usam um SQLite temporário e uma chave descartável, nunca o banco real. Rotas de autenticação, pacientes e dieta **não têm testes hoje**.

**Verificação manual**, quando não houver teste: com a API rodando, abra `http://localhost:8000/docs`, use "Authorize" com o token obtido em `POST /auth/login` e execute a rota. Depois confira na tela:

- [ ] Fluxo feliz: login, cadastro de paciente, avaliação, dieta e PDF.
- [ ] Perfil sem permissão (`paciente`): a API responde 403 nas rotas de escrita.
- [ ] Entrada inválida: o campo mostra a mensagem, sem erro técnico.
- [ ] Lista vazia e paciente inexistente: a tela exibe estado vazio ou erro claro.
- [ ] Duplo clique em "Salvar": não grava duas vezes.

## 8. Convenções do código

- Comentários explicam o motivo da decisão, não a mecânica.
- Cada rota nova tem docstring com propósito, perfil de acesso, corpo esperado e erros possíveis.
- Mensagens de login e de "esqueci minha senha" são genéricas de propósito.
- Os cálculos clínicos ficam no servidor; o front-end não envia resultados prontos.
