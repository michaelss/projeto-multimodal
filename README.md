# Projeto multimodal · Desenvolvimento de Aplicações Interativas com LLMs Multimodais

Modelo de projeto da disciplina (PUC Minas). Ele começa no Encontro 2 e cresce a cada encontro até virar o seu Trabalho Orientado.

## Estrutura

```
projeto-multimodal/
├── .env.example      nomes das chaves, sem valores (copie para .env)
├── .gitignore        mantém .env, logs e dados privados fora do GitHub
├── requirements.txt  pacotes do projeto
├── AGENTS.md         regras do projeto para o GitHub Copilot e outros agentes
├── REGISTRO_IA.md    registro do uso de assistentes de IA (exigido no trabalho)
├── src/
│   ├── config.py     provedores, modelos, preços e leitura das chaves
│   ├── cliente.py    chamar_modelo: retentativa, reserva, cache, esquema, registro
│   ├── midia.py      imagens: redução, recorte, marcas, cupons de exemplo
│   ├── esquemas.py   classes Pydantic das respostas
│   ├── validacao.py  regras de negócio
│   ├── prompts.py    leitura dos prompts versionados
│   └── uso.py        registro de tokens, latência e custo em logs/uso.csv
├── prompts/          prompts versionados (.md)
├── praticas/         scripts das aulas e o quiz
├── notebooks/        plano B: as mesmas práticas no Colab
├── dados/exemplos/   imagens de teste (geradas pelos scripts)
└── logs/             uso.csv (criado na primeira chamada)
```

## Como o código se conecta

O caminho de uma chamada da Prática 1 (as outras práticas seguem a mesma ideia):

```
praticas/p1_nota_fiscal.py          o roteiro: chama cada peça na ordem
 │
 ├─1─► src/midia.py      mensagem()       imagem vira data URL (reduzida)
 ├─2─► src/prompts.py    carregar()       lê prompts/extracao_v1.md
 │
 ├─3─► src/cliente.py    chamar_modelo()  a única porta de saída para os modelos
 │        a. já está no cache? devolve
 │        b. escolhe o provedor (principal e reserva)      ◄── src/config.py
 │        c. envia com timeout ───────────────► Groq ou Gemini (API na internet)
 │        d. 429 ou 5xx? espera com jitter e tenta de novo
 │        e. esquema recusado? desce um nível de saída
 │        f. registra o uso                                ──► src/uso.py → logs/uso.csv
 │        g. valida com o esquema                          ◄── src/esquemas.py (NotaFiscal)
 │
 └─4─► src/validacao.py  conferir()       regras de negócio: segue ou revisão humana
```

Cada arquivo tem uma responsabilidade: para trocar de provedor, mexa só em `config.py`; para mudar o formato da resposta, só em `esquemas.py`; para uma regra nova, só em `validacao.py`.

## Preparação (uma vez)

1. Instale o **Python 3.10 ou mais novo** e o **VS Code**, com as extensões **Python** e **GitHub Copilot**.
2. Abra a pasta do projeto no VS Code (**Arquivo > Abrir Pasta**) e abra o terminal (**Terminal > Novo Terminal**).
3. Crie e ative o ambiente virtual:

   | Sistema | Criar | Ativar |
   | --- | --- | --- |
   | Windows | `python -m venv .venv` | `.venv\Scripts\activate` |
   | macOS e Linux | `python3 -m venv .venv` | `source .venv/bin/activate` |

   No Windows, se a ativação for bloqueada, rode uma vez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
4. Instale os pacotes: `pip install -r requirements.txt`
   Depois, no VS Code, **Ctrl+Shift+P > Python: Select Interpreter** e escolha o Python que tem `.venv` no caminho.
5. Copie `.env.example` para `.env` e preencha a sua chave (Groq ou Gemini).
6. Confira tudo: `python praticas/p0_primeira_chamada.py`

## Práticas do Encontro 2

Rode sempre a partir da pasta raiz do projeto, com o ambiente virtual ativado.

| Prática | Comando | O que mostra |
| --- | --- | --- |
| 0 | `python praticas/p0_primeira_chamada.py` | ambiente, chaves e a primeira chamada |
| 1 | `python praticas/p1_nota_fiscal.py` | nota fiscal em JSON validado e regras de negócio |
| 2 | `python praticas/p2_consumo.py` | tokens por resolução, registro de uso e projeção de custo |
| 3 | `python praticas/p3_prompts.py` | três prompts comparados em um conjunto de teste |

Para usar a sua própria foto na Prática 1: `python praticas/p1_nota_fiscal.py dados/minha_nota.jpg` (sem dados pessoais).

**Entrega:** preencha `praticas/quiz_encontro2.py` (nome, tema do Trabalho Orientado, quiz e justificativa da Prática 3), rode-o e envie o link do repositório ou o `.zip` do projeto **sem o arquivo `.env` e sem a pasta `.venv`**.

## Plano B

Se o ambiente local não funcionar, use `notebooks/Plano_B_Colab.ipynb` no Google Colab: ele roda os mesmos scripts, com as chaves nos Secrets do Colab.

## Segurança

- A chave nunca vai no código. Se vazar, apague-a no site do provedor e crie outra.
- Antes de cada `git commit`, confira que o `.env` não aparece em `git status`.
