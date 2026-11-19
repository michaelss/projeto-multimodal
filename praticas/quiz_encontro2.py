"""Entrega do Encontro 2: identificação, tema do Trabalho Orientado, quiz e justificativa da Prática 3.

Preencha os campos abaixo e rode:
    python praticas/quiz_encontro2.py
As perguntas estão em praticas/QUIZ.md.
"""

ALUNO = "Marcelo Ribeiro de Oliveira Mello"            # seu nome completo
MATRICULA = ""        # opcional

# Trabalho Orientado: comece a pensar no tema. Uma ou duas frases bastam por enquanto.
TEMA_TRABALHO = (
    "Protótipo para processamento de notas fiscais eletrônicas (NF-e) a partir de "
    "imagens ou PDFs do DANFE, com extração de campos em JSON validado e regras "
    "de negócio para encaminhar inconsistências à revisão humana."
)

RESPOSTAS = {
    1: "b",   # API: contrato de comunicação entre programas.
    2: "c",   # .env e .gitignore evitam publicar a chave no repositório.
    3: "a",   # AGENTS.md define as regras para os agentes de código.
    4: "b",   # O esquema confere o formato; os valores precisam de validação.
    5: "d",   # Erro 401 exige corrigir a autenticação, sem repetir a mesma chamada.
    6: "a",   # Jitter distribui as retentativas no tempo.
    7: "c",   # Alternativa conforme a escada de blocos apresentada na atividade.
    8: "b",   # Caixas numeradas indicam as regiões de interesse.
}

# Prática 3: qual variante você escolheria para produção, e por quê? (acurácia e tokens)
JUSTIFICATIVA_P3 = (
    "Escolheria a variante C (prompt visual), considerando a execução com o Groq: "
    "ela acertou os 9 campos avaliados (100%) e consumiu em média 1.790 tokens "
    "de entrada por chamada. A variante A também acertou 9 de 9, mas usou "
    "1.826 tokens; a B acertou 8 de 9 (88,9%) e usou 3.160 tokens. Assim, C "
    "manteve a maior acurácia observada com o menor consumo de entrada. "
    "A vantagem sobre A foi pequena, cerca de 2%; antes da produção, eu "
    "validaria mais documentos e incluiria o custo de localizar e desenhar "
    "as caixas numeradas. O teste com apenas três cupons fictícios não "
    "garante o mesmo desempenho em NF-e reais."
)


if __name__ == "__main__":
    faltando = [q for q, r in RESPOSTAS.items() if str(r).strip().lower() not in ("a", "b", "c", "d")]
    print("Aluno:", ALUNO or "NOME NÃO PREENCHIDO")
    print("Tema do Trabalho Orientado:", TEMA_TRABALHO or "AINDA NÃO DEFINIDO: comece a pensar nele")
    print("Respostas:", {q: str(r).strip().lower() for q, r in RESPOSTAS.items()})
    print("Justificativa da Prática 3:", "preenchida" if JUSTIFICATIVA_P3.strip() else "FALTANDO")
    if faltando:
        print("Atenção, perguntas sem resposta válida:", faltando)
    elif ALUNO and JUSTIFICATIVA_P3.strip():
        print("Entrega completa. Envie o link do seu repositório (ou o .zip, sem o arquivo .env) pelo portal.")
