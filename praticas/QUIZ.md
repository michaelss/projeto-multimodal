# Quiz · Encontro 2

Responda em `praticas/quiz_encontro2.py`, com a letra da alternativa certa. Cada pergunta tem uma única resposta correta.

**1. O que é uma API?**
- a) Um modelo de linguagem treinado pela OpenAI
- b) Um contrato que define como um programa pede algo a outro programa e o que recebe de volta
- c) Uma biblioteca Python para treinar redes neurais
- d) Um tipo de banco de dados na nuvem

**2. Por que a chave fica no arquivo `.env`, e o `.env` fica listado no `.gitignore`?**
- a) Para a chamada ficar mais rápida
- b) Porque o Python só lê chaves de arquivos `.env`
- c) Para a chave não ir para o repositório no GitHub, onde qualquer pessoa poderia copiá-la
- d) Para ativar o plano gratuito do provedor

**3. Para que serve o arquivo `AGENTS.md` na raiz do projeto?**
- a) Guardar as instruções e regras do projeto que o agente de código (Copilot) deve seguir
- b) Listar os pacotes que precisam ser instalados
- c) Guardar as chaves de API dos agentes
- d) Registrar o custo de cada chamada

**4. Com saídas estruturadas (JSON Schema), o que fica garantido?**
- a) Que todos os valores extraídos estão corretos
- b) Que a resposta segue o formato do esquema, mas os valores ainda podem estar errados
- c) Que a chamada nunca dá erro 429
- d) Que a resposta sai mais barata

**5. A API devolveu o erro 401. O que o código deve fazer?**
- a) Tentar de novo com espera exponencial
- b) Reduzir a imagem e reenviar
- c) Tentar de novo imediatamente, várias vezes
- d) Não repetir: a chave é inválida ou sem permissão; avisar e parar

**6. Por que acrescentar jitter (um sorteio) à espera entre as tentativas?**
- a) Para espalhar as retentativas no tempo e evitar que todos os clientes voltem juntos
- b) Para deixar a resposta do modelo mais criativa
- c) Para pagar menos por token
- d) Porque o provedor exige um número aleatório no pedido

**7. No Gemini, por que reduzir uma imagem de 1024 para 768 pixels pode economizar tanto?**
- a) Porque o Gemini cobra por pixel
- b) Porque imagens menores são enviadas sem base64
- c) Porque a imagem cai de 4 blocos de 768 px (1.032 tokens) para 1 bloco (258 tokens)
- d) Porque o Gemini não aceita imagens maiores que 768 px

**8. No prompt visual (Set-of-Mark), o que as caixas numeradas fazem?**
- a) Escondem as partes sensíveis da imagem
- b) Apontam as regiões de interesse, para o modelo localizar e citar cada uma pelo número
- c) Aumentam a resolução da imagem
- d) Reduzem os tokens da imagem pela metade
