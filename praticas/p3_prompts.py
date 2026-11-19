"""Prática 3 · Comparando prompts com um conjunto de teste (Encontro 2, bloco 2.4). Versão curta.

O que acontece:
1. Gera 3 cupons fictícios com respostas conhecidas (o gabarito).
2. Roda três variantes de prompt sobre os mesmos cupons:
   A: zero-shot  ·  B: few-shot (1 exemplo com a resposta)  ·  C: prompt visual (caixas numeradas)
3. Mede a acurácia por campo e os tokens de cada variante.

Como rodar, a partir da pasta raiz do projeto:
    python praticas/p3_prompts.py
São 9 chamadas: se aparecer o erro 429, a retentativa com jitter cuida.
"""
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from src.cliente import chamar_modelo  # noqa: E402
from src.esquemas import NotaFiscal  # noqa: E402
from src.midia import gerar_cupom, marcar, parte_imagem, parte_texto  # noqa: E402
from src.prompts import carregar  # noqa: E402

LADO = 768   # resolução usada em todas as variantes (comparação justa)

# 1. Conjunto de teste: cupons com gabarito conhecido
CASOS = [gerar_cupom("PADARIA PAO DOURADO", "03/11/2026", [("CAFE COM LEITE", 6.50), ("PAO NA CHAPA", 5.00)]),
         gerar_cupom("FARMACIA SAO LUCAS", "28/10/2026", [("PROTETOR SOLAR", 59.90), ("ESCOVA DENTAL", 12.40)]),
         gerar_cupom("POSTO ESTRELA", "15/10/2026", [("GASOLINA", 150.00), ("AGUA MINERAL", 4.50), ("CAFE", 7.00)])]
EXEMPLO = gerar_cupom("RESTAURANTE BOM SABOR", "20/10/2026", [("PRATO FEITO", 32.00), ("REFRIGERANTE", 7.00)])


def normalizar(v):
    """Compara sem diferença de maiúsculas, acentos, espaços ou vírgula/ponto decimal."""
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.2f}"
    s = unicodedata.normalize("NFKD", str(v)).encode("ascii", "ignore").decode().lower()
    return " ".join(s.replace("r$", "").replace(",", ".").split())


# 2. As três variantes: cada uma é uma função que monta a mensagem a partir do caso
sis_v1, usu_v1 = carregar("extracao_v1")
sis_vis, usu_vis = carregar("extracao_visual")


def variante_a(caso):
    img, _, _ = caso
    return sis_v1, [parte_imagem(img, LADO), parte_texto(usu_v1)]


def variante_b(caso):
    img, _, _ = caso
    ex_img, _, ex_gab = EXEMPLO
    resposta_ex = NotaFiscal(emitente=ex_gab["emitente"], data=ex_gab["data"], valor_total=ex_gab["valor_total"]).model_dump_json()
    return sis_v1, [parte_texto("Exemplo:"), parte_imagem(ex_img, LADO), parte_texto(f"Resposta esperada: {resposta_ex}"),
                    parte_texto("Agora esta nota:"), parte_imagem(img, LADO), parte_texto(usu_v1)]


def variante_c(caso):
    img, caixas, _ = caso
    return sis_vis, [parte_imagem(marcar(img, caixas), LADO), parte_texto(usu_vis)]


VARIANTES = {"A zero-shot": variante_a, "B few-shot": variante_b, "C visual": variante_c}

# 3. O laço de avaliação: mesmas notas para todas as variantes
linhas = []
for nome, montar in VARIANTES.items():
    for caso in CASOS:
        sistema, conteudo = montar(caso)
        r = chamar_modelo(conteudo, esquema=NotaFiscal, sistema=sistema, etiqueta=f"p3_{nome[0]}")
        for campo, certo in caso[2].items():
            linhas.append({"variante": nome, "campo": campo,
                           "acertou": normalizar(getattr(r.conteudo, campo)) == normalizar(certo),
                           "tokens": r.tok_entrada})

df = pd.DataFrame(linhas)
tabela = df.groupby("variante").agg(acuracia_por_campo=("acertou", "mean"), tokens_por_chamada=("tokens", "mean"))
print(tabela.round(2).to_string())
print("\nAcurácia por campo e variante:")
print(df.pivot_table(index="campo", columns="variante", values="acertou", aggfunc="mean").round(2).to_string())
print("\nEscolha a variante considerando acurácia E tokens, e escreva a justificativa em praticas/quiz_encontro2.py.")
