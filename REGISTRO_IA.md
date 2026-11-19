# Registro do uso de assistentes de IA

Aluno: Marcelo Ribeiro de Oliveira Mello.

## Etapa no Copilot realizada em 11/11/2026

Após autorização do aluno para controlar o VS Code, o Codex encaminhou os
pedidos abaixo ao GitHub Copilot, modelo Copilot Fusion (`mai-code-1.1-flash`),
no modo agente Autopilot da interface disponível. A revisão técnica das
alterações e a execução dos testes foram feitas pelo Codex; o aluno deve
revisar o material antes do envio. Não se atribui ao aluno uma revisão que
ele ainda não declarou ter realizado.

| Data | Ferramenta e modo | O que pedi | O que o assistente fez bem | O que eu corrigi ou recusei |
| --- | --- | --- | --- | --- |
| 11/11/2026 | GitHub Copilot, agente Autopilot, operado pelo Codex com autorização do aluno | Explicar chamar_modelo, cache, Pydantic, registro de uso, retentativa com jitter e provedor reserva, lendo somente AGENTS.md e src/cliente.py, sem alterar arquivos. | Leu os dois arquivos indicados e concluiu a explicação, sem executar terminal. | A interface atual oferecia modos Interactive, Plan e Autopilot; o pedido de explicação foi feito sem edição no modo agente disponível, em vez de registrar falsamente um uso do modo Ask. |
| 11/11/2026 | GitHub Copilot, agente Autopilot, operado pelo Codex com autorização do aluno | Acrescentar revisão humana para notas sem itens ou com item de valor None, preservar as regras existentes, atualizar as docstrings e criar três testes locais. | Alterou somente src/validacao.py e tests/test_validacao.py; usou mensagens em português e preservou as validações anteriores. | O Codex revisou o código e executou os seis testes do projeto, todos aprovados, antes de clicar em Keep All Edits. Não foi necessária correção adicional no código proposto. O Copilot não executou o script: essa verificação ficou a cargo do Codex. |

Motivo da regra escolhida: a extração da nota fornecida pelo aluno retornou
o total, mas deixou o valor de um item como null. A implementação anterior
permitia aprovação automática nesse caso. Ao reaplicar a regra nova ao mesmo
JSON real, a decisão passou a revisão humana por valor de item ausente.

Arquivos desta etapa:

- `src/validacao.py`: regra nova de itens incompletos, criada pelo Copilot.
- `tests/test_validacao.py`: três casos criados pelo Copilot, executados pelo Codex.
- `.gitignore`: adição de `test-input/`, preservando as exclusões anteriores.
- `dados/exemplos/nota_notebook_anonimizada.png`: imagem derivada localmente do PDF fornecido, após remoção das regiões de identificação e revisão visual.
- `RESULTADOS_ENCONTRO2.md` e `GUIA_ATIVIDADE.md`: atualização do resultado e da forma de reproduzir o teste.
- `REGISTRO_IA.md`: registro da intervenção real do Copilot e da participação do Codex.

O PDF original e suas prévias locais não foram enviados ao Groq. Foi enviada
somente a imagem anonimizada. O original permanece em `test-input/` e os
intermediários em `dados/privados/`, excluídos do pacote de entrega.

A repetição da Prática 1 após a alteração foi executada pelo Codex no
terminal, usando a imagem anonimizada. O cliente demonstrou recusa do
primeiro formato, descida para JSON, erro 429 e espera de 309 segundos
indicada pelo provedor. Após a retentativa, a chamada terminou com sucesso:
o total e o valor do item foram R$ 3.254,07, com 2.338 tokens de entrada e
102 de saída. As regras permitiram seguir automaticamente, mas a descrição
do produto ainda estava parcialmente incorreta. Essa limitação foi
registrada no relatório, sem atribuir ao esquema ou à regra uma garantia
de exatidão que eles não oferecem.

## Histórico das etapas anteriores

As menções a pendências abaixo registram o estado em cada etapa anterior.
O estado atualizado está na seção acima e no relatório de resultados.

O Trabalho Orientado pede o registro transparente e crítico do uso de assistentes de IA. Acrescente uma linha a cada uso relevante.

| Data | Ferramenta e modo | O que pedi | O que o assistente fez bem | O que eu corrigi ou recusei |
| --- | --- | --- | --- | --- |
| 11/11/2026 | Codex (agente) | Ajudar a preparar o projeto da atividade e adotar o tema Processamento de NFEs. | Extraiu o ZIP, leu AGENTS.md, preparou o ambiente e o arquivo local de configuração e sugeriu respostas comentadas ao quiz e uma descrição do tema. | Revisão pelo aluno pendente. A justificativa da Prática 3 depende dos resultados reais; esta linha não substitui o uso do GitHub Copilot na Prática 1. |

Arquivos preparados pelo Codex nesta etapa:

- `.env`: cópia local de `.env.example`, para configuração da chave pelo aluno.
- `.vscode/settings.json`: indica o interpretador Python do ambiente `.venv`.
- `praticas/quiz_encontro2.py`: identificação do aluno, proposta de tema e respostas comentadas para revisão; justificativa ainda pendente.
- `GUIA_ATIVIDADE.md`: comandos de execução e pedidos sugeridos para a etapa no Copilot.
- `REGISTRO_IA.md`: registra esta assistência sem atribuí-la ao Copilot.

Verificação inicial: o quiz mostra o nome e as oito respostas e informa que
a justificativa da Prática 3 está faltando. A Prática 0 encontra `.env`,
confirma sua exclusão no `.gitignore` e interrompe a execução porque a chave
ainda não foi cadastrada. Nenhuma chamada a um modelo foi realizada nesta etapa.

Instalação concluída: `pip check` não encontrou dependências incompatíveis,
e as bibliotecas foram importadas com sucesso. Foi gerado localmente
`dados/exemplos/cupom_exemplo.png`, com total conhecido de R$ 42,90,
para uso na Prática 1. Isso não representa uma extração feita pelo modelo.

| Data | Ferramenta e modo | O que pedi | O que o assistente fez bem | O que eu corrigi ou recusei |
| --- | --- | --- | --- | --- |
| 11/11/2026 | Codex (agente) | Executar as práticas após salvar a chave fornecida pelo professor. | Executou a primeira chamada e a extração do cupom; identificou uma resposta fora do esquema na Prática 2, reforçou o contrato de saída no cliente e distinguiu falhas de validação nos registros. Validou a correção com três testes locais e uma execução completa da Prática 2. | O aluno ainda deve revisar os resultados e as alterações. A extração inicial retornou a data como null e foi encaminhada à revisão humana. Não foi feito uso do Copilot nesta intervenção. |

Arquivos alterados nesta intervenção:

- `src/cliente.py`: inclui o esquema também na mensagem de sistema, especifica campos na raiz e registra `erro_validacao` com os tokens efetivamente consumidos antes de rejeitar uma resposta inválida. Não preenche campos ausentes nem aceita silenciosamente um objeto fora do contrato.
- `tests/test_cliente.py`: verifica resposta válida com null, rejeição de um objeto envoltório e rejeição de JSON incompleto, sem chamadas à API.
- `logs/uso.csv`: recebeu os registros reais das chamadas. Na execução inicial anterior à correção, a chamada `p2_768px` de `2026-11-11T22:01:18` foi registrada como `ok` pelo código original, embora tenha falhado no Pydantic. Essa ocorrência deve ser considerada falha de validação na análise dos resultados.

Verificação: os três testes locais passaram. Após a correção, a Prática 2
retornou R$ 42,90 nas três resoluções, com 1.826 tokens de entrada em cada uma.
As alterações foram baseadas também na documentação oficial do provedor:
https://console.groq.com/docs/structured-outputs.

| Data | Ferramenta e modo | O que pedi | O que o assistente fez bem | O que eu corrigi ou recusei |
| --- | --- | --- | --- | --- |
| 11/11/2026 | Codex (agente) | Comparar os prompts e preparar a análise da atividade com os resultados reais. | Executou as nove chamadas da Prática 3 e sugeriu C: 9/9 campos e 1.790 tokens de entrada por chamada, frente a A com 9/9 e 1.826 tokens e B com 8/9 e 3.160 tokens. Identificou que os limites de 768 e 1024 px enviavam a mesma imagem de 600 × 686 px. | O aluno ainda precisa revisar a justificativa e executar a etapa exigida no Copilot e o teste com cupom próprio. O controle da janela foi interrompido pelo usuário; nenhuma ação no Copilot foi concluída. |

Arquivos atualizados para esta análise:

- `praticas/quiz_encontro2.py`: justificativa sugerida a partir da execução real da Prática 3, com as limitações da amostra e do custo das marcas visuais.
- `RESULTADOS_ENCONTRO2.md`: resultados medidos, origem fictícia dos cupons, erro observado, correção, projeção de custo e pendências.
- `GUIA_ATIVIDADE.md`: atualização do estado do preenchimento do quiz.
- `REGISTRO_IA.md`: identificação transparente desta intervenção.

Verificação: `quiz_encontro2.py` exibiu o nome completo, o tema, as oito
respostas e a justificativa preenchida. Isso não substitui as práticas ainda
pendentes, mesmo que o verificador imprima "Entrega completa".

Teste de estresse concluído: os oito pedidos adicionais foram respondidos
pelo Groq, com latência média de 24,49 segundos. Não apareceram mensagens de
429/jitter do laço do projeto e não houve troca de provedor, pois não havia
reserva configurada. Essas limitações constam no relatório.

Correção transparente do histórico: o status da chamada `p2_768px` de
`2026-11-11T22:01:18`, comprovadamente rejeitada pelo Pydantic, passou de
`ok` para `erro_validacao` em `logs/uso.csv`. Horário, tokens e custo foram
mantidos; a versão anterior foi preservada em
`logs/uso_antes_correcao_historica.csv`.

Verificação local de segredos: a chave cadastrada não foi encontrada nos
arquivos de código, documentos ou logs analisados, excluindo o próprio `.env`.
Nenhum ZIP de entrega foi produzido nesta etapa, pois ainda faltam a foto
própria e a intervenção exigida no Copilot.
