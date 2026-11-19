# Resultados do Encontro 2

Aluno: Marcelo Ribeiro de Oliveira Mello.

Tema: processamento de NF-e a partir de imagens ou PDFs do DANFE,
com extração de campos em JSON validado e revisão humana de inconsistências.

Execução local em 11/11/2026, Python 3.10.11, Groq,
modelo `qwen/qwen3.8-27b`. As chamadas passaram por `src/cliente.py`.
As Práticas 2 e 3 usaram cupons fictícios gerados pelo próprio projeto.
Na Prática 1 também foi usada uma imagem anonimizada do DANFE fornecido pelo aluno.

Origem dos cupons: a função `gerar_cupom()` em `src/midia.py` usa Pillow
para desenhar os dados definidos nos scripts. A Prática 1 usa
LANCHONETE EXEMPLO LTDA (R$ 42,90). A Prática 3 cria PADARIA PAO DOURADO,
FARMACIA SAO LUCAS e POSTO ESTRELA como casos de teste; RESTAURANTE BOM SABOR
é o exemplo adicional usado no few-shot. Não foram baixados cupons da internet.

## Prática 0

A chave do Groq foi reconhecida sem ser exibida. A primeira chamada respondeu
à pergunta sobre o que é uma API, com 29 tokens de entrada, 53 de saída e
latência registrada de 7,10 segundos. Nenhum provedor reserva foi configurado.

## Prática 1

Resultado da primeira extração, antes do reforço do contrato de saída:

```json
{
  "emitente": "LANCHONETE EXEMPLO LTDA",
  "data": null,
  "valor_total": 42.9,
  "itens": [
    {"descricao": "X-SALADA", "valor": 24.9},
    {"descricao": "SUCO LARANJA", "valor": 9.0},
    {"descricao": "PAO DE QUEIJO", "valor": 9.0}
  ]
}
```

O cupom continha a data 31/10/2026. O retorno null foi aceito pelo esquema,
que permite valores desconhecidos, mas a regra de negócio sinalizou
**REVISÃO HUMANA: data ausente ou inválida**. Os itens somaram R$ 42,90,
igual ao total extraído. Consumo: 1.463 tokens de entrada, 91 de saída;
latência registrada: 1,10 segundo.

Isso ilustra a diferença entre conferir a estrutura e conferir o conteúdo.
A nota fornecida pelo aluno e a regra nova no Copilot foram trabalhadas
na etapa complementar descrita a seguir.

### Nota fornecida e regra implementada pelo Copilot

O aluno forneceu um DANFE em PDF. Ele foi inspecionado e anonimizado
localmente: foram removidos destinatário, CPF, endereço, contatos, dados
de identificação fiscal, chave de acesso, código de barras e informações
adicionais com identificadores. O original foi preservado e somente uma
imagem da cópia anonimizada foi enviada ao Groq.

Na primeira extração dessa imagem, o modelo retornou:

- emitente: MAGAZINE LUIZA S/A;
- data: 21/05/2019;
- total: R$ 3.254,07;
- um item com descrição parcialmente incorreta e valor null.

Consumo: 2.338 tokens de entrada, 83 de saída e latência registrada de
1,30 segundo. As regras anteriores aprovaram a nota automaticamente,
mesmo com o item sem valor. Isso expôs uma lacuna de validação; o JSON
correto não garantiu a exatidão da descrição nem a completude dos itens.

Com autorização do aluno, o Codex operou o GitHub Copilot no VS Code e
pediu uma regra para revisão humana de notas sem itens ou com item de
valor ausente. O Copilot alterou `src/validacao.py`, atualizou suas docstrings
e criou `tests/test_validacao.py` com três casos. O Codex revisou as alterações
e executou os seis testes do projeto, todos aprovados, antes de manter as
edições com Keep All Edits. Não houve alteração adicional no código do Copilot.

Ao reavaliar exatamente o mesmo JSON extraído, a regra nova retornou:
**REVISÃO HUMANA: item com valor ausente: revisar**. Essa comparação local
isola a mudança de regra da variabilidade de uma nova resposta do modelo.

O Copilot também recebeu e concluiu o pedido de explicação de `src/cliente.py`.
A interface disponível oferecia Interactive, Plan e Autopilot; foi usado o modo
agente Autopilot, com o primeiro pedido restrito à explicação sem edição.
O registro não afirma que foi usado o modo Ask. Os testes e a execução da
prática foram feitos pelo Codex, sem comandar o terminal por automação de UI.

Na repetição posterior da Prática 1, o provedor recusou o primeiro formato,
o cliente passou ao modo JSON e recebeu um erro 429 com `retry-after` de
309 segundos. O cliente aguardou o prazo indicado antes da nova tentativa.

A retentativa terminou com sucesso. A nova resposta manteve o emitente,
a data e o total corretos, agora com valor do item de R$ 3.254,07. Foram
registrados 2.338 tokens de entrada, 102 de saída e latência de 36,80 segundos
na chamada bem-sucedida; essa latência não inclui a espera anterior de 309 s.
A decisão foi automática porque os valores passaram nas regras atuais.
A descrição do produto continuou parcialmente incorreta, mostrando uma
limitação que essas regras não detectam: o conteúdo textual ainda exige
conferência humana ou uma validação adicional específica do domínio.

## Correção necessária no cliente

Na primeira execução da Prática 2, a resposta de 768 px colocou os campos
dentro de um objeto chamado `extracao`. O Pydantic rejeitou esse formato,
e o script interrompeu a execução. O código original havia registrado a chamada
como `ok` antes de validar a resposta.

O cliente foi ajustado para incluir o JSON Schema também na instrução de
sistema, exigir os campos na raiz e registrar respostas rejeitadas como
`erro_validacao`, preservando seus tokens e custo. A validação continua
obrigatória; não foram inventados valores nem aceitos objetos fora do contrato.

Referência: [Structured Outputs — Groq](https://console.groq.com/docs/structured-outputs).
O modo sem `strict: true` é de melhor esforço e pode descumprir o esquema.

Três testes locais passaram: resposta válida com null, rejeição de objeto
envoltório e rejeição de JSON incompleto. Os testes não fazem chamadas à API.

## Prática 2: primeira execução completa após a correção

| Limite configurado | Imagem efetivamente enviada | Tokens de entrada | Tokens de saída | Total lido | Latência |
| --- | --- | ---: | ---: | ---: | ---: |
| 384 px | 336 × 384 | 1.826 | 101 | R$ 42,90 | 1,00 s |
| 768 px | 600 × 686 | 1.826 | 101 | R$ 42,90 | 12,54 s |
| 1024 px | 600 × 686 | 1.826 | 104 | R$ 42,90 | 23,99 s |

O cupom original tem 600 × 686 pixels. A função de mídia só reduz imagens;
por isso, 768 e 1024 resultaram na mesma imagem enviada. Esta execução com
Groq não reproduziu uma escada de tokens de imagem do Gemini. Não é possível
concluir, com esses dados, que resoluções maiores nunca aumentam o consumo.

Com os preços de referência do projeto (US$ 0,80 por milhão de tokens de
entrada e US$ 4,00 por milhão de saída), a chamada de 768 px desta execução
custa teoricamente US$ 0,0018648. Para 10 mil documentos semelhantes:
**US$ 18,648, aproximadamente US$ 18,65**, considerando somente as chamadas.
Isso é uma projeção com os preços do material, não uma cobrança observada.
Não inclui erros, retentativas, infraestrutura ou revisão humana.

O resumo impresso pelo script agrega o histórico inteiro de `logs/uso.csv`,
inclusive execuções anteriores à mudança de prompt. Por esse motivo, pode
diferir da projeção calculada apenas para esta execução completa.

Após as execuções, o status da chamada inválida de `2026-11-11T22:01:18`,
etiqueta `p2_768px`, foi corrigido de `ok` para `erro_validacao`, sem alterar
tokens, custo ou horário. O arquivo anterior foi preservado em
`logs/uso_antes_correcao_historica.csv`. Os resumos capturados antes dessa
correção ainda mostram zero erros e incluem essa chamada nas médias;
o histórico corrigido permite distinguir a falha sem apagar a evidência original.

### Teste de estresse

O comando `praticas/p2_consumo.py --estresse` foi concluído, incluindo as três
resoluções e os oito pedidos adicionais sem cache. Todos os oito pedidos
adicionais foram respondidos pelo Groq; a latência média registrada foi de
24,49 segundos, com 1.831 tokens de entrada em cada pedido.

Nesta execução, o script não exibiu mensagens de erro 429 nem de espera
sorteada. Portanto, não houve demonstração visível do jitter pelo laço do
projeto. Não houve troca de provedor, pois só existe uma chave cadastrada.
Isso não impede o estudo do mecanismo no código nem significa que a troca
de provedor tenha sido testada.

No código, `_espera` prioriza `retry-after`; sem esse cabeçalho, sorteia uma
espera entre zero e `base × 2**tentativa`. O sorteio distribui as tentativas
no tempo. O conjunto `REPETIR` contém 408, 429, 500, 502, 503 e 504.
O erro 401 não pertence a esse conjunto e não deve levar a repetir a mesma
requisição com a mesma chave inválida. Se houver outro provedor configurado,
o cliente pode passar a ele; nesta execução não havia reserva.

## Prática 3

As nove chamadas foram executadas com o mesmo cliente corrigido. O contrato
de saída adicional foi comum às três variantes. Cada variante foi avaliada
em três cupons e três campos, totalizando nove comparações.

| Variante | Campos corretos | Acurácia | Média de tokens de entrada por chamada |
| --- | ---: | ---: | ---: |
| A — zero-shot | 9/9 | 100% | 1.826 |
| B — few-shot | 8/9 | 88,89% | 3.160 |
| C — visual | 9/9 | 100% | 1.790 |

Emitente e data tiveram 100% de acertos nas três variantes. No campo total,
B acertou dois dos três casos; A e C acertaram os três.

A justificativa sugerida no arquivo de entrega escolhe C pelo empate na melhor
acurácia e pelo menor consumo de entrada. A economia de entrada frente a A
foi de apenas 36 tokens por chamada, cerca de 2%. A decisão de produção
depende de validar uma amostra maior e de viabilizar a localização das caixas
em documentos reais; o custo dessa preparação não foi medido aqui.

## Revisão e envio

O teste com documento fornecido foi realizado com um PDF convertido em imagem
anonimizada, em vez de uma fotografia. O uso real do Copilot está registrado
em `REGISTRO_IA.md`, distinguindo a autoria das alterações e a revisão do Codex.
O verificador `quiz_encontro2.py` confirmou os campos preenchidos.

Antes de enviar pelo portal, o aluno deve revisar o tema, as respostas,
a justificativa e os resultados. O pacote de entrega deve excluir `.env`,
`.venv`, caches, `test-input/` e `dados/privados/`.

O pacote inclui o código, o quiz preenchido, os testes, este relatório,
o registro de IA, os registros de execução e a imagem anonimizada de teste.
O PDF original e o ambiente local não fazem parte da entrega.
