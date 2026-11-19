"""Registro de uso: uma linha por chamada em logs/uso.csv (Encontro 2, bloco 2.3)."""
import csv
from datetime import datetime

from src.config import PASTA_LOGS, PRECOS

ARQUIVO = PASTA_LOGS / "uso.csv"
COLUNAS = ["quando", "provedor", "modelo", "tok_entrada", "tok_saida", "latencia_s", "custo_usd", "status", "etiqueta"]


def custo(provedor, tok_entrada, tok_saida):
    """custo = tokens de entrada × preço de entrada + tokens de saída × preço de saída (preços por milhão)."""
    p_in, p_out = PRECOS.get(provedor, (0.0, 0.0))
    return (tok_entrada * p_in + tok_saida * p_out) / 1_000_000


def registrar(provedor, modelo, tok_entrada, tok_saida, latencia, status="ok", etiqueta=""):
    """Acrescenta uma linha ao arquivo de uso. Cria o arquivo com cabeçalho na primeira vez."""
    PASTA_LOGS.mkdir(exist_ok=True)
    novo = not ARQUIVO.exists()
    with open(ARQUIVO, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(COLUNAS)
        w.writerow([datetime.now().isoformat(timespec="seconds"), provedor, modelo, tok_entrada, tok_saida,
                    round(latencia, 2), f"{custo(provedor, tok_entrada, tok_saida):.6f}", status, etiqueta])


def resumo():
    """Lê o arquivo de uso com pandas e devolve a tabela (ou None, se ainda não houver chamadas)."""
    import pandas as pd
    if not ARQUIVO.exists():
        return None
    return pd.read_csv(ARQUIVO)
