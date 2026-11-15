# Qualidade de software

Avaliação do NTeM segundo os três núcleos de estudo: documentação de código, documentação de usuário e qualidade (arquitetura e skins). Esta página descreve o que o código faz hoje; o que não existe aparece como lacuna.

## Arquitetura

Cliente-servidor em três camadas, implantadas separadamente: navegador (HTML, CSS e JavaScript no Vercel), API FastAPI (Render) e PostgreSQL (Neon). O envio de e-mail usa o Resend. O front-end descobre o endereço da API sozinho em `frontend/config.js`.

```
Navegador (Vercel)  ──HTTPS + JSON──▶  API FastAPI (Render)  ──SQLAlchemy──▶  PostgreSQL (Neon)
                                              │
                                              └──▶ Resend (e-mail de redefinição)
```

No back-end a separação é parcial: `app/database.py` isola conexão e modelos e `app/antropometria.py` isola as fórmulas (sem acesso a banco ou HTTP), mas `app/main.py` ainda concentra schemas, autenticação e rotas. A regra "somente profissionais alteram dados clínicos" é verificada no servidor, não apenas escondida na interface. Detalhes em [arquitetura.md](arquitetura.md).

## Skins e temas (claro e escuro)

- `style.css` define variáveis semânticas (`--bg-app`, `--input-bg` e outras); o bloco `[data-theme="dark"]` só redefine esses valores, mantendo as cores de marca.
- `theme.js` aplica `data-theme` e `data-bs-theme` ao mesmo tempo; o segundo ativa o modo escuro nativo do Bootstrap 5.3.
- A escolha fica em `localStorage` (chave `_ns_tema`); sem escolha prévia, vale a preferência do sistema operacional.
- Para criar uma nova skin (por exemplo, alto contraste), basta um bloco `[data-theme="alto-contraste"]` com as mesmas variáveis e um valor a mais em `theme.js`.
- Limite atual: classes fixas do Bootstrap (`bg-white`, `text-dark`) em algumas telas ignoram as variáveis e devem ser trocadas.

## Atributos de qualidade (ISO/IEC 25010)

| Característica | Evidência no código | Situação |
|---|---|---|
| Adequação funcional | RF01 a RF07 implementados; fórmulas de percentual de gordura | Parcial: anamnese não é gravada; GET não é calculado |
| Eficiência de desempenho | Índices em chaves estrangeiras; histórico de avaliações paginado (máx. 50); rotina de keep-alive contra cold start | Parcial: demais listas sem paginação |
| Compatibilidade | CORS restrito às origens listadas; integração com Resend | Atende |
| Usabilidade | Spinner nos botões, mensagens claras, tema escuro, `aria-label` no menu e no tema | Parcial: feedback via `alert()` e validação sem destaque no campo |
| Confiabilidade | Salvamento de avaliação idempotente (30 s); falha de e-mail não derruba a rota | Parcial: testes só na antropometria; `/dietas/` não é atômica |
| Segurança | Senhas com bcrypt, JWT com expiração, token de reset guardado como hash, segredos só em variáveis de ambiente | Em evolução; pontos em revisão são tratados no repositório, fora desta página |
| Manutenibilidade | Comentários explicam decisões; fórmulas em módulo próprio; documentação modular | Parcial: `main.py` extenso, TMB repetida em `dieta.html`, sem migrações versionadas |
| Portabilidade | Deploy em Render e Vercel; configuração por variáveis de ambiente | Atende |

## Referências

- ISO/IEC 25010:2011 — Modelos de qualidade de sistemas e de software.
- Lei nº 13.709/2018 (LGPD) — tratamento de dados pessoais sensíveis de saúde.
- Documentação oficial do FastAPI e do Bootstrap 5.3 (modos de cor).
- NEPA/UNICAMP — Tabela Brasileira de Composição de Alimentos (TACO).
