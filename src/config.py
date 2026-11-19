"""Configuração do projeto: provedores, modelos e leitura das chaves.

Nunca escreva uma chave de API neste arquivo. As chaves ficam no arquivo .env
(que não vai para o GitHub) ou, no Colab, nos Secrets.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[1]      # pasta raiz do projeto
load_dotenv(RAIZ / ".env")                      # lê o .env, se existir

# Provedor principal; os outros com chave cadastrada viram reserva
PROVEDOR = os.getenv("PROVEDOR", "groq")

# Todos aceitam o formato da API de chat da OpenAI: muda o endereço, o modelo e a chave.
# Os nomes de modelos mudam com frequência; se der "model not found", confira a documentação.
PROVEDORES = {
    "groq": {"base_url": "https://api.groq.com/openai/v1", "chave": "GROQ_API_KEY",
             "modelo": "qwen/qwen3.8-27b", "max_imagens": 3},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "chave": "GEMINI_API_KEY",
               "modelo": "gemini-3.8-flash", "max_imagens": 10},
    "openai": {"base_url": None, "chave": "OPENAI_API_KEY",
               "modelo": "gpt-4o-mini", "max_imagens": 10},
}

# Preços de referência em US$ por milhão de tokens (entrada, saída), plano pago, nov. 2026.
# Confira a página de preços do provedor antes de usar em uma estimativa real.
PRECOS = {"groq": (0.80, 4.00), "gemini": (0.75, 3.75), "openai": (0.15, 0.60)}

PASTA_LOGS = RAIZ / "logs"
PASTA_DADOS = RAIZ / "dados"
PASTA_PROMPTS = RAIZ / "prompts"


def ler_chave(nome):
    """Lê a chave do .env (ou das variáveis de ambiente) e, no Colab, dos Secrets. Nunca imprime a chave."""
    valor = os.getenv(nome)
    if valor:
        return valor
    try:                                        # plano B: rodando no Colab
        from google.colab import userdata
        return userdata.get(nome)
    except Exception:
        return None


def chaves_disponiveis():
    """Devolve os provedores que têm chave cadastrada, sem mostrar as chaves."""
    return [p for p, cfg in PROVEDORES.items() if ler_chave(cfg["chave"])]
