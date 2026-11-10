# Manual do usuário

Este manual ensina o estudante ou formando de Nutrição a atender um paciente no NTeM, do login à entrega do plano alimentar em PDF.

| Item | Informação |
|---|---|
| Quem usa | Estudantes e formandos de Nutrição que atendem pacientes na ES Nutrição Acessível |
| Endereço | https://ntem.vercel.app, em navegador atualizado (Chrome, Edge ou Firefox), no computador |
| Versão | `main` do repositório, conferida contra o código em 10/11/2026 |
| Contas | Criadas pela equipe do projeto; a tela de login não tem opção de criar conta |

## Antes de começar

- No primeiro acesso do dia, o sistema pode levar até um minuto para responder. Aguarde; é normal.
- O menu lateral leva a Dashboard, Cadastro & Anamnese, Antropometria, Plano Alimentar e Meu Perfil. O botão de lua ou sol alterna entre tema claro e escuro.
- A sessão dura 60 minutos e termina ao fechar a aba.

## Passo a passo do atendimento

1. **Entrar.** Informe e-mail e senha e clique em "Entrar no Sistema". O Dashboard mostra o total de pacientes, quantos já têm dieta e a distribuição por objetivo.
2. **Cadastrar o paciente.** Em "Cadastro & Anamnese", preencha o nome (obrigatório) e o objetivo principal; e-mail e telefone são opcionais. Salve e aguarde a confirmação com o número do paciente. Os campos de anamnese (alergias, histórico familiar, intestino e sono) aparecem na tela, mas ainda não são gravados; registre essas informações fora do sistema.
3. **Registrar a avaliação.** Em "Antropometria", clique em "Buscar Prontuário do Paciente", escolha o paciente e clique em "Carregar Dados". Informe sexo biológico, idade, data da avaliação, peso (kg) e altura (cm). Para o percentual de gordura, escolha uma fórmula; as dobras cutâneas (mm) e circunferências (cm) que ela usa ficam destacadas. Os resultados analíticos (IMC, TMB e demais) aparecem enquanto você preenche. Clique em "Salvar avaliação". Cada avaliação salva entra no histórico, em "Avaliações anteriores", e não pode ser alterada depois; use "Carregar mais antigas" para ver as anteriores.
4. **Montar a dieta.** Em "Plano Alimentar", clique em "Selecionar / Trocar Paciente", escolha o paciente e confirme em "Confirmar e Carregar". Use "Nova Refeição" (o nome padrão é "Nova Refeição" e o horário 12:00; ambos são editáveis), busque o alimento da Tabela TACO e informe a quantidade em gramas. Calorias, carboidratos, proteínas, gorduras, fibras e sódio são recalculados a cada item, e o painel do dia compara o total com a TMB do paciente.
5. **Guardar o plano.** Clique em "Guardar Plano Alimentar". O novo plano **substitui** o anterior do mesmo paciente.
6. **Gerar o PDF.** Clique em "Gerar Plano em PDF". O plano abre em uma nova aba e a janela de impressão aparece sozinha: escolha "Salvar como PDF" ou imprima. Se nada abrir, permita pop-ups para o site.
7. **Sair.** Use "Sair do Sistema" no menu lateral.

## Procedimentos (POPs)

Os três procedimentos abaixo estão em rascunho até serem validados por quem os executa.

### POP-01 — Atendimento completo de um paciente

| Item | Descrição |
|---|---|
| Quando se aplica | A cada novo atendimento nutricional |
| Pré-condições | Conta ativa com perfil profissional; navegador atualizado; internet; paciente informou nome e objetivo |
| Quem pode executar | Usuário com perfil "profissional"; o servidor recusa cadastro, avaliação e dieta para outros perfis |
| Passos | Os sete passos acima |
| Resultado esperado | Paciente com avaliação e plano alimentar salvos e PDF entregue |
| Verificações | O número do paciente apareceu na confirmação; a avaliação aparece em "Avaliações anteriores"; apareceu "Plano Alimentar atualizado com sucesso!"; o PDF mostra todas as refeições |
| Exceções | Sessão expirada: entre de novo e refaça o passo; servidor lento: aguarde até um minuto |
| Escalonamento | Se o erro persistir, acione o responsável técnico do projeto (contato a definir pela ES) |
| Riscos e ações irreversíveis | Guardar o plano substitui o anterior; avaliações salvas não podem ser editadas ou apagadas |

### POP-02 — Atualizar o plano alimentar

| Item | Descrição |
|---|---|
| Quando se aplica | Retorno do paciente ou ajuste de refeições e quantidades |
| Passos | Em "Plano Alimentar", carregue o paciente, edite refeições, alimentos e gramas e clique em "Guardar Plano Alimentar" |
| Verificações | Recarregue a página e carregue o paciente de novo: o plano exibido é o novo |
| Exceções | Fechar ou recarregar a página antes de guardar perde o rascunho |
| Riscos e ações irreversíveis | A substituição não pode ser desfeita. Antes de alterar um plano já entregue, gere e salve o PDF do plano atual |

### POP-03 — Recuperar o acesso à conta

| Item | Descrição |
|---|---|
| Pré-condições | Acesso ao e-mail cadastrado |
| Passos | Em "Esqueci minha senha", informe o e-mail, abra o link recebido, digite a nova senha (mínimo de 6 caracteres) e confirme |
| Resultado esperado | Mensagem "Senha redefinida com sucesso" e login com a nova senha |
| Exceções | Link com mais de 30 minutos ou já usado: peça outro. E-mail não chegou: veja o spam |
| Riscos | O link é pessoal; não o encaminhe |

## Conta e senha

| Situação | O que fazer |
|---|---|
| Esqueci minha senha | Veja o POP-03 |
| Quero trocar a senha | Em "Meu Perfil", informe a senha atual e a nova (mínimo de 6 caracteres) |
| Mudei de e-mail | Em "Meu Perfil", altere nome e e-mail e salve |
| Não recebi o e-mail | Confira o spam; por segurança, o sistema responde igual mesmo se o e-mail não estiver cadastrado |

## Mensagens do sistema

| Mensagem | Causa e solução |
|---|---|
| "E-mail ou senha incorretos" | Confira os dados; o sistema não informa qual está errado, de propósito |
| "Sua sessão expirou. Por favor, faça login novamente." | A sessão dura 60 minutos; entre de novo e refaça a ação |
| "Selecione um paciente primeiro." | Escolha o paciente antes de editar a dieta |
| "Preencha o alimento e a quantidade." | Selecione um alimento e informe gramas maiores que zero |
| "Selecione um paciente para gerar o documento." | Carregue um paciente antes de gerar o PDF |
| "Este paciente ainda não possui refeições cadastradas no plano." | Adicione ao menos uma refeição e guarde o plano |
| "Informe ao menos uma medida antes de salvar." | Preencha ao menos um campo na antropometria |
| "O servidor pode estar iniciando — aguarde alguns segundos…" | A API estava hibernada; aguarde |
| "Erro de conexão com o Back-End" | Verifique a internet e tente de novo |
| "Link inválido ou expirado" | Peça um novo link em "Esqueci minha senha" |

## Glossário

| Termo | Significado no sistema |
|---|---|
| Prontuário | Dados e medidas atuais de um paciente |
| IMC | Peso (kg) dividido pela altura (m) ao quadrado, com classificação da OMS |
| TMB | Taxa Metabólica Basal, pela fórmula de Harris-Benedict. O sistema não calcula o gasto energético total (GET) |
| % de gordura | Calculado pela fórmula escolhida (ver `antropometria-formulas.md`) |
| Tabela TACO | Tabela Brasileira de Composição de Alimentos; valores por 100 g, proporcionais à quantidade informada |
| Perfil profissional | Perfil que pode cadastrar pacientes, salvar avaliações e montar dietas |

## Lacunas conhecidas

- O manual ainda não tem capturas de tela; ao incluí-las, cada uma deve ter texto alternativo e legenda.
- A anamnese não é gravada, não há edição dos dados cadastrais depois de salvos e o GET não é calculado.
- Não há teste deste manual com estudantes; a tabela abaixo deve ser aplicada na primeira oportunidade. Critério de aprovação proposto: três estudantes cumprem pelo menos quatro das cinco tarefas sem ajuda.

| Tarefa dada ao leitor | Critério de sucesso | Resultado |
|---|---|---|
| Cadastrar um paciente de teste | Chega à confirmação com o número do paciente sem ajuda | |
| Salvar uma avaliação com peso e altura e dizer o IMC | Lê o valor e a classificação corretos | |
| Montar uma refeição com três alimentos e guardar | Vê a mensagem de plano atualizado | |
| Gerar o PDF | Abre ou salva o PDF sem ajuda | |
| Recuperar a senha | Define a nova senha e entra | |
