"""Prática 0 · Conferir o ambiente e fazer a primeira chamada pelo projeto.

Como rodar, a partir da pasta raiz do projeto, com o ambiente virtual ativado:
    python praticas/p0_primeira_chamada.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # permite "from src..." rodando da raiz

from src.config import PROVEDOR, PROVEDORES, RAIZ, chaves_disponiveis  # noqa: E402

print("Python:", sys.version.split()[0])
if sys.version_info < (3, 10):
    sys.exit("Use Python 3.10 ou mais novo.")

# 1. O arquivo .env existe e está protegido pelo .gitignore?
env = RAIZ / ".env"
print(".env encontrado:", "sim" if env.exists() else "NÃO: copie .env.example para .env e preencha a chave")
gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8") if (RAIZ / ".gitignore").exists() else ""
print(".env no .gitignore:", "sim" if ".env" in gitignore.split() else "NÃO: acrescente a linha .env ao .gitignore")

# 2. Quais chaves o projeto encontrou (sem mostrar o valor)?
disponiveis = chaves_disponiveis()
for nome, cfg in PROVEDORES.items():
    print(f"  {cfg['chave']:<16} {'OK' if nome in disponiveis else 'não cadastrada'}")
if not disponiveis:
    sys.exit("Nenhuma chave encontrada. Preencha GROQ_API_KEY ou GEMINI_API_KEY no arquivo .env.")
print("Provedor principal:", PROVEDOR, "| reservas:", [p for p in disponiveis if p != PROVEDOR] or "nenhuma")

# 3. A primeira chamada pelo cliente do projeto
from src.cliente import chamar_modelo  # noqa: E402

r = chamar_modelo("Em uma frase, explique o que é uma API para quem não é programador.", etiqueta="p0")
print("\nResposta:", r.conteudo)
print(f"Provedor: {r.provedor} | modelo: {r.modelo} | tokens: {r.tok_entrada} de entrada, {r.tok_saida} de saída"
      f" | {r.latencia:.1f} s")
print("\nTudo certo: o ambiente está pronto. A chamada foi registrada em logs/uso.csv.")
