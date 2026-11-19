# Atividade do Encontro 2

Aluno: Marcelo Ribeiro de Oliveira Mello.

Tema proposto: processamento de NF-e a partir de imagens ou PDFs do DANFE,
com extração estruturada e revisão humana de inconsistências.

## Configurar a chave

Abra `.env` no VS Code. Preencha a variável `GROQ_API_KEY` com a chave fornecida
pelo professor e mantenha `PROVEDOR=groq`. Salve o arquivo. Não publique `.env`.

## Executar no PowerShell

Abra o terminal na pasta que contém `requirements.txt`, `src/` e `praticas/`.
O Python do ambiente pode ser usado diretamente, sem alterar a política de
execução de scripts do Windows:

```powershell
.\.venv\Scripts\python.exe praticas/p0_primeira_chamada.py
.\.venv\Scripts\python.exe praticas/p1_nota_fiscal.py
```

Confira emitente, data, itens e total extraídos com a imagem em
`dados/exemplos/cupom_exemplo.png`. O esquema valida o formato; a função
`conferir` em `src/validacao.py` decide se os valores exigem revisão humana.

Para a segunda execução da Prática 1, use uma foto sua sem dados pessoais:

```powershell
.\.venv\Scripts\python.exe praticas/p1_nota_fiscal.py dados/minha_nota.jpg
```

Nesta atividade foi fornecido um PDF, convertido localmente em imagem
anonimizada. Para repetir o teste com essa cópia já preparada:

```powershell
.\.venv\Scripts\python.exe praticas/p1_nota_fiscal.py dados/exemplos/nota_notebook_anonimizada.png
```

O script continua recebendo imagens; não foi acrescentado suporte direto a
PDF no cliente. PyMuPDF foi usado apenas na preparação local do documento.

## Etapa no GitHub Copilot realizada

O pedido de explicação encaminhado ao Copilot foi:

> Explique o que faz o arquivo src/cliente.py e como ele trata retentativas,
> provedor reserva, cache, saída estruturada e registro de uso.

O pedido de alteração foi:

> Siga AGENTS.md. Em src/validacao.py, encaminhe à revisão humana as notas
> sem itens ou com algum item cujo valor seja None, preservando as regras
> existentes. Atualize as docstrings e crie três testes locais: itens completos,
> item sem valor e lista vazia. Não leia arquivos privados e não use terminal;
> a execução dos testes e da prática será feita separadamente pelo Codex.

Na interface disponível foi usado o modo agente Autopilot. O Codex revisou
o código, executou os seis testes do projeto e manteve as alterações no
Copilot. O registro distingue esse uso real do Copilot das demais ações do Codex.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Práticas seguintes

Execute um comando por vez e guarde os resultados:

```powershell
.\.venv\Scripts\python.exe praticas/p2_consumo.py
.\.venv\Scripts\python.exe praticas/p2_consumo.py --estresse
.\.venv\Scripts\python.exe praticas/p3_prompts.py
```

O modo de estresse consome chamadas adicionais. Compare os tokens em 384, 768
e 1024 pixels e observe os registros em `logs/uso.csv`. Os custos calculados
usam os preços de referência de `src/config.py`; confira-os antes de tratar
esses números como orçamento real.

Na Prática 3, use os resultados efetivamente obtidos para preencher
`JUSTIFICATIVA_P3` em `praticas/quiz_encontro2.py`, comparando acurácia e tokens.
O nome, a proposta de tema, as oito respostas comentadas do quiz e uma
justificativa baseada na execução real da Prática 3 estão preenchidos para
sua revisão. Os resultados e as pendências estão em `RESULTADOS_ENCONTRO2.md`.

```powershell
.\.venv\Scripts\python.exe praticas/quiz_encontro2.py
```

## Entrega

O roteiro pede o projeto em ZIP ou um link do repositório, com o quiz preenchido
e o registro do uso do Copilot. Exclua `.env`, `.venv`, caches e dados pessoais
do pacote. O `.gitignore` protege arquivos no Git, mas não filtra automaticamente
o conteúdo de um ZIP. A entrega deve ser revisada pelo aluno antes do envio
pelo portal.
