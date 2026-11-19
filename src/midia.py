"""Preparação de mídia: imagem para data URL, mensagens com várias imagens, recorte, marcas e cupons de exemplo.

Encontro 2, blocos 2.1 (envio de imagens) e 2.4 (prompt visual, recorte e zoom).
"""
import base64
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def imagem_para_data_url(imagem, lado_max=1024, qualidade=85):
    """Recebe um caminho ou uma imagem PIL; reduz o lado maior para lado_max e devolve uma data URL JPEG em base64."""
    img = imagem if isinstance(imagem, Image.Image) else Image.open(imagem)
    img = img.convert("RGB")
    img.thumbnail((lado_max, lado_max))          # mantém a proporção; só reduz
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=qualidade)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def parte_imagem(imagem, lado_max=1024):
    return {"type": "image_url", "image_url": {"url": imagem_para_data_url(imagem, lado_max)}}


def parte_texto(texto):
    return {"type": "text", "text": texto}


def mensagem(texto, imagens=(), rotulos=None, lado_max=1024):
    """Monta o conteúdo multimodal com as imagens ANTES do texto e, se houver rótulos, um rótulo antes de cada imagem."""
    partes = []
    for i, img in enumerate(imagens):
        if rotulos:
            partes.append(parte_texto(f"{rotulos[i]}:"))
        partes.append(parte_imagem(img, lado_max))
    partes.append(parte_texto(texto))
    return partes


def recortar(imagem, caixa):
    """Recorta a região (x0, y0, x1, y1) da imagem original, em resolução cheia (recorte e zoom)."""
    img = imagem if isinstance(imagem, Image.Image) else Image.open(imagem)
    return img.crop(caixa)


def _fonte(tamanho, negrito=False):
    nomes = ["DejaVuSans-Bold.ttf" if negrito else "DejaVuSans.ttf", "arialbd.ttf" if negrito else "arial.ttf"]
    for nome in nomes:
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:
        return ImageFont.load_default()


def marcar(imagem, caixas, cor="#E0362C"):
    """Prompt visual (Set-of-Mark): desenha caixas numeradas sobre a imagem. caixas = [(x0, y0, x1, y1), ...]."""
    img = (imagem if isinstance(imagem, Image.Image) else Image.open(imagem)).convert("RGB").copy()
    d = ImageDraw.Draw(img)
    f = _fonte(28, negrito=True)
    for n, (x0, y0, x1, y1) in enumerate(caixas, 1):
        d.rectangle((x0, y0, x1, y1), outline=cor, width=4)
        d.ellipse((x1 + 10, y0 - 4, x1 + 58, y0 + 44), fill=cor)
        d.text((x1 + 34, y0 + 20), str(n), fill="white", font=f, anchor="mm")
    return img


def gerar_cupom(emitente, data, itens, caminho=None):
    """Desenha um cupom fiscal fictício e devolve (imagem, caixas de emitente, data e total, gabarito).

    itens = [("X-SALADA", 24.90), ...]. Útil para testar o pipeline sem dados pessoais.
    """
    f, fb = _fonte(26), _fonte(26, negrito=True)
    linhas = [(emitente, fb), ("Rua das Flores, 100", f), ("CNPJ 00.000.000/0001-00", f), ("", f), (f"{data}  12:41", f), ("", f)]
    for desc, v in itens:
        linhas.append((f"1 {desc[:16]:<16} {v:>8.2f}".replace(".", ","), f))
    total = round(sum(v for _, v in itens), 2)
    linhas += [("", f), (f"TOTAL R$ {total:>12.2f}".replace(".", ","), fb)]
    img = Image.new("RGB", (600, 70 + 56 * len(linhas)), "white")
    d = ImageDraw.Draw(img)
    for i, (t, fonte) in enumerate(linhas):
        d.text((36, 34 + i * 56), t, fill="black", font=fonte)
    def caixa(i):
        return (26, 26 + i * 56, 520, 72 + i * 56)
    caixas = [caixa(0), caixa(4), caixa(len(linhas) - 1)]
    gabarito = {"emitente": emitente, "data": data, "valor_total": total}
    if caminho:
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        img.save(caminho)
    return img, caixas, gabarito
