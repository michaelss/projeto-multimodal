"""Voz: transcrição (fala para texto) e síntese (texto para fala) (Encontro 3, bloco 3.4).

- transcrever: usa o Whisper do provedor, pelo src/cliente.py (o mesmo cliente das outras chamadas).
- sintetizar: usa o edge-tts, um serviço gratuito e sem chave, com vozes em português.
  É ótimo para protótipos; em produção, prefira a síntese de fala paga de um provedor, com contrato
  e limites claros. No Groq, a síntese de fala disponível hoje não tem português.
"""
import re
from pathlib import Path

from src.cliente import transcrever  # noqa: F401  (reexportado: from src.audio import transcrever)
from src.config import PASTA_DADOS, VOZ

MAX_CARACTERES_FALA = 900     # respostas longas viram áudios longos: leia só o começo


def texto_para_fala(texto):
    """Limpa o Markdown (asteriscos, títulos, links) para a voz não ler símbolos em voz alta."""
    t = re.sub(r"```.*?```", " ", texto or "", flags=re.S)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"[*_#>`|]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > MAX_CARACTERES_FALA:
        t = t[:MAX_CARACTERES_FALA].rsplit(".", 1)[0] + "."
    return t


def sintetizar(texto, caminho=None, voz=VOZ):
    """Gera um MP3 com o texto falado e devolve o caminho; devolve None se o serviço não responder."""
    try:
        import edge_tts
    except ImportError:
        print("Para a síntese de fala, instale: pip install edge-tts")
        return None
    fala = texto_para_fala(texto)
    if not fala:
        return None
    destino = Path(caminho or PASTA_DADOS / "saidas" / "resposta.mp3")
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        edge_tts.Communicate(fala, voz).save_sync(str(destino))
    except Exception as erro:                    # sem internet, serviço fora do ar ou bloqueado pela rede
        print(f"Síntese de fala indisponível agora: {type(erro).__name__}")
        return None
    return str(destino)
