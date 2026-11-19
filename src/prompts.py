"""Leitura de prompts versionados na pasta prompts/ (Encontro 2, bloco 2.4).

Cada arquivo .md tem duas seções: '## sistema' e '## usuario'.
Versionar o prompt como arquivo permite comparar versões e registrar qual foi usada.
"""
from src.config import PASTA_PROMPTS


def carregar(nome):
    """Lê prompts/<nome>.md e devolve (sistema, usuario)."""
    texto = (PASTA_PROMPTS / f"{nome}.md").read_text(encoding="utf-8")
    partes = {}
    atual = None
    for linha in texto.splitlines():
        if linha.strip().lower().startswith("## "):
            atual = linha.strip()[3:].strip().lower()
            partes[atual] = []
        elif atual:
            partes[atual].append(linha)
    return ("\n".join(partes.get("sistema", [])).strip(), "\n".join(partes.get("usuario", [])).strip())
