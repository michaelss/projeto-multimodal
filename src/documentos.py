"""Documentos PDF: páginas como imagem e texto extraído (Encontro 3, bloco 3.4; estratégias vistas no Encontro 2).

Estratégia híbrida:
- página com bastante texto digital: envia o texto extraído (barato e preciso);
- página com pouco texto (escaneada, tabela, gráfico): envia a página como imagem.
Usa o PyMuPDF (pip install pymupdf).
"""
from pathlib import Path

MIN_CARACTERES = 200          # abaixo disso, a página provavelmente é imagem (escaneada) ou gráfico


def _abrir(caminho):
    try:
        import pymupdf
    except ImportError as erro:
        raise RuntimeError("Para ler PDFs, instale o PyMuPDF: pip install pymupdf") from erro
    return pymupdf.open(str(caminho))


def paginas_como_imagens(caminho, max_paginas=3, dpi=110, pasta_saida=None):
    """Renderiza as primeiras páginas como PNG e devolve a lista de caminhos.

    dpi 110 deixa uma página A4 com cerca de 900 x 1290 pixels: legível e sem tokens demais.
    """
    doc = _abrir(caminho)
    pasta = Path(pasta_saida or Path(caminho).with_suffix(""))
    pasta.mkdir(parents=True, exist_ok=True)
    saidas = []
    for i, pagina in enumerate(doc):
        if i >= max_paginas:
            break
        destino = pasta / f"pagina_{i + 1}.png"
        pagina.get_pixmap(dpi=dpi).save(str(destino))
        saidas.append(str(destino))
    return saidas


def texto_do_pdf(caminho, max_paginas=10, max_caracteres=12000):
    """Extrai o texto digital das páginas (vazio em PDFs escaneados)."""
    doc = _abrir(caminho)
    partes = []
    for i, pagina in enumerate(doc):
        if i >= max_paginas:
            break
        partes.append(f"--- página {i + 1} ---\n{pagina.get_text().strip()}")
    return "\n".join(partes)[:max_caracteres]


def preparar_pdf(caminho, max_paginas=3):
    """Decide, página a página, entre texto e imagem. Devolve (texto, lista de imagens) para montar a mensagem."""
    doc = _abrir(caminho)
    textos, imagens = [], []
    pasta = Path(caminho).with_suffix("")
    pasta.mkdir(parents=True, exist_ok=True)
    for i, pagina in enumerate(doc):
        if i >= max_paginas:
            break
        conteudo = pagina.get_text().strip()
        if len(conteudo) >= MIN_CARACTERES:
            textos.append(f"--- página {i + 1} (texto extraído) ---\n{conteudo}")
        else:
            destino = pasta / f"pagina_{i + 1}.png"
            pagina.get_pixmap(dpi=110).save(str(destino))
            imagens.append(str(destino))
            textos.append(f"--- página {i + 1}: enviada como imagem ---")
    if len(doc) > max_paginas:
        textos.append(f"(documento com {len(doc)} páginas; só as {max_paginas} primeiras foram enviadas)")
    return "\n".join(textos), imagens
