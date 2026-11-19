# Instruções para agentes de código (GitHub Copilot e outros)

Este é um projeto acadêmico de aplicação multimodal com LLMs (PUC Minas). Siga estas regras ao sugerir ou editar código.

## Regras que nunca podem ser quebradas
- Nunca escreva chaves de API, senhas ou tokens no código, em comentários ou em exemplos. As chaves ficam no arquivo `.env`, lido por `src/config.py`.
- Nunca altere o `.gitignore` para remover `.env`, `logs/` ou `dados/privados/`.
- Toda chamada a um modelo passa por `src/cliente.py` (`chamar_modelo`). Não crie clientes da OpenAI, Groq ou Gemini em outros arquivos: é ali que estão a retentativa, o provedor reserva, o cache e o registro de uso.
- Não envie dados pessoais (CPF, endereço, documentos de terceiros) para APIs de plano gratuito.

## Organização
- `src/config.py`: provedores, modelos, preços e leitura das chaves.
- `src/cliente.py`: chamadas ao modelo.
- `src/midia.py`: preparação de imagens (redução, recorte, marcas).
- `src/esquemas.py`: classes Pydantic das respostas estruturadas.
- `src/validacao.py`: regras de negócio sobre as respostas.
- `src/uso.py`: registro de tokens, latência e custo.
- `prompts/`: prompts versionados em Markdown, com as seções `## sistema` e `## usuario`.
- `praticas/`: scripts das aulas. Rode sempre a partir da raiz: `python praticas/<arquivo>.py`.

## Estilo
- Python 3.10 ou mais novo, com type hints simples.
- Comentários e mensagens ao usuário em português do Brasil.
- Funções pequenas, com docstring dizendo o que recebem e o que devolvem.
- Ao criar uma função nova em `src/`, explique em uma frase no início do arquivo onde ela se encaixa.

## Antes de concluir uma tarefa
- Rode o script afetado e mostre a saída.
- Liste os arquivos alterados e o motivo de cada alteração, para o registro em `REGISTRO_IA.md`.
