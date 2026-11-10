# Documentação do NTeM

Índice da documentação. Cada assunto tem uma única fonte; os demais documentos apontam para ela.

| Documento | Para quem | O que responde |
|---|---|---|
| [manual-do-usuario.md](manual-do-usuario.md) | Estudantes e formandos de Nutrição | Como atender um paciente de ponta a ponta; o que fazer quando algo dá errado |
| [guia-do-desenvolvedor.md](guia-do-desenvolvedor.md) | Quem vai manter o sistema | Como o front-end fala com a API, como criar rotas, alterar o banco, publicar e verificar |
| [api.md](api.md) | Quem consome a API | Rotas, perfis de acesso, corpos e códigos de erro |
| [arquitetura.md](arquitetura.md) | Quem precisa entender o conjunto | Camadas, estrutura de pastas, modelo de dados e decisões de projeto |
| [antropometria-formulas.md](antropometria-formulas.md) | Nutricionistas e desenvolvedores | Fórmulas implementadas, unidades, referências e caso de conferência |

`index.html` é uma cópia de 05/11/2026 do documento do trabalho de Qualidade de Software. Ela é anterior à refatoração da antropometria e, nos pontos em que diverge destes arquivos, valem estes arquivos.

## Cartão de saúde da documentação

| Item | Situação |
|---|---|
| Versão coberta | `main` do repositório `Mikeszs/NTeM`, conferida contra o código em 10/11/2026 |
| Gatilho de revisão | Qualquer mudança em rota, tela, mensagem, modelo de dados ou regra de cálculo |
| Verificação com leitores | Ainda não feita; ver as tarefas de verificação em `manual-do-usuario.md` |
| Lacunas conhecidas | Capturas de tela, contato de apoio técnico e teste do manual com estudantes |
