"""Prática 2 · Medindo consumo e protegendo as chamadas (Encontro 2, blocos 2.2 e 2.3).

O que acontece:
1. Envia o mesmo cupom em três resoluções e registra os tokens de cada chamada.
2. Resume o arquivo logs/uso.csv com pandas: tokens, latência e custo.
3. Projeta o custo de 10 mil documentos.
4. (Opcional) --estresse: dispara chamadas seguidas, sem cache, para ver a retentativa com jitter
   e a troca de provedor. Gasta parte do seu limite por minuto.

Como rodar, a partir da pasta raiz do projeto:
    python praticas/p2_consumo.py
    python praticas/p2_consumo.py --estresse
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import uso  # noqa: E402
from src.cliente import chamar_modelo  # noqa: E402
from src.config import PASTA_DADOS  # noqa: E402
from src.esquemas import NotaFiscal  # noqa: E402
from src.midia import gerar_cupom, mensagem  # noqa: E402
from src.prompts import carregar  # noqa: E402

caminho = PASTA_DADOS / "exemplos" / "cupom_exemplo.png"
gerar_cupom("LANCHONETE EXEMPLO LTDA", "31/10/2026",
            [("X-SALADA", 24.90), ("SUCO LARANJA", 9.00), ("PAO DE QUEIJO", 9.00)], caminho)
sistema, usuario = carregar("extracao_v1")

# 1. Mesma imagem, três resoluções: a escada de tokens na prática
print("Resolução | tokens de entrada | total lido")
for lado in (384, 768, 1024):
    r = chamar_modelo(mensagem(usuario, [caminho], lado_max=lado), esquema=NotaFiscal, sistema=sistema,
                      usar_cache=False, etiqueta=f"p2_{lado}px")
    print(f"{lado:>7} px | {r.tok_entrada:>17} | {r.conteudo.valor_total}")

# 4. Opcional: provocar o limite por minuto para ver a retentativa e a reserva
if "--estresse" in sys.argv:
    print("\nDisparando 8 chamadas seguidas, sem cache...")
    for i in range(8):
        r = chamar_modelo(mensagem(usuario + f" (pedido {i})", [caminho], lado_max=768), esquema=NotaFiscal,
                          sistema=sistema, usar_cache=False, etiqueta="p2_estresse")
        print(f"  pedido {i}: respondido por {r.provedor} em {r.latencia:.1f} s")

# 2. Resumo do arquivo de uso
df = uso.resumo()
ok = df[df.status == "ok"]
print("\nMédia por etiqueta (chamadas bem-sucedidas):")
print(ok.groupby("etiqueta")[["tok_entrada", "tok_saida", "latencia_s", "custo_usd"]].mean().round(5).to_string())
print("\nLatência p50 e p95 (s):", ok.latencia_s.quantile([0.5, 0.95]).round(2).tolist())
print("Chamadas com erro registradas:", int((df.status != "ok").sum()))

# 3. Projeção de custo para 10 mil documentos, usando a resolução de 768 px
media = ok[ok.etiqueta.str.startswith("p2_768")].custo_usd.mean()
print(f"\nProjeção: 10 mil documentos a 768 px custariam cerca de US$ {media * 10_000:.2f} no plano pago.")
