"""Gerenciamento de contexto da conversa (Encontro 3, bloco 3.2).

A API não tem memória: cada chamada é independente. O que parece memória é o histórico
que a aplicação reenvia a cada pergunta. Este módulo decide O QUE reenviar:

- nenhuma:  só a pergunta atual (o modelo esquece tudo)
- completa: todas as mensagens (simples, mas o custo cresce a cada turno)
- janela:   só os últimos N turnos (custo estável; esquece o começo da conversa)
- resumo:   um resumo dos turnos antigos mais os últimos N (lembra o essencial, com uma chamada extra)

Imagens pesam muito mais que texto: só as imagens mais recentes são reenviadas;
as antigas viram uma marcação de texto, como "[imagem enviada antes: cupom.png]".
"""
from dataclasses import dataclass, field
from pathlib import Path

from src.midia import parte_imagem, parte_texto

ESTRATEGIAS = ("nenhuma", "completa", "janela", "resumo")
TOKENS_POR_IMAGEM = 258          # referência para estimativas: uma imagem de até 768 px no Gemini
EXT_IMAGEM = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
EXT_AUDIO = {".mp3", ".wav", ".m4a", ".ogg", ".webm", ".flac", ".mp4", ".mpeg", ".mpga"}


def eh_imagem(caminho):
    return Path(str(caminho)).suffix.lower() in EXT_IMAGEM


def eh_audio(caminho):
    return Path(str(caminho)).suffix.lower() in EXT_AUDIO


def eh_pdf(caminho):
    return Path(str(caminho)).suffix.lower() == ".pdf"


@dataclass
class Turno:
    """Uma mensagem da conversa, num formato simples e independente do Gradio e do provedor."""
    papel: str                                   # "user" ou "assistant"
    texto: str = ""
    imagens: list = field(default_factory=list)  # caminhos das imagens enviadas nesta mensagem


# ---------------------------------------------------------------------------
# 1. Ler o histórico que o Gradio entrega
# ---------------------------------------------------------------------------

def ler_historico_gradio(history):
    """Converte o histórico do gr.ChatInterface (formato 'messages') em uma lista de Turno.

    O formato muda entre versões do Gradio e entre a interface e o cliente de API: o conteúdo
    pode ser um texto, um dicionário {"path": ...}, uma tupla (caminho,) ou uma lista de partes
    {"type": "text" | "file", ...}. Esta função aceita todos. Mensagens seguidas do mesmo papel
    (o Gradio às vezes separa o arquivo e o texto) são juntadas em um só turno.
    """
    turnos = []
    for msg in history or []:
        papel = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
        conteudo = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", None)
        if papel not in ("user", "assistant"):
            continue
        textos, arquivos = [], []
        _coletar(conteudo, textos, arquivos)
        if turnos and turnos[-1].papel == papel:
            turno = turnos[-1]
        else:
            turno = Turno(papel)
            turnos.append(turno)
        if textos:
            turno.texto = (turno.texto + "\n" + "\n".join(t for t in textos if t)).strip()
        turno.imagens += [a for a in arquivos if eh_imagem(a)]
    return turnos


def _coletar(c, textos, arquivos):
    """Percorre o conteúdo de uma mensagem do Gradio separando textos e caminhos de arquivos."""
    if c is None:
        return
    if isinstance(c, str):
        textos.append(c)
    elif isinstance(c, tuple) and c and isinstance(c[0], str) and Path(c[0]).suffix:
        arquivos.append(c[0])                                  # formato antigo: (caminho, legenda)
    elif isinstance(c, (list, tuple)):
        for parte in c:
            _coletar(parte, textos, arquivos)
    elif isinstance(c, dict):
        if "file" in c:
            _coletar(c["file"], textos, arquivos)              # Gradio 6: {"type": "file", "file": {...}}
        elif c.get("path"):
            arquivos.append(c["path"])                         # {"path": ...}
        elif "text" in c:
            textos.append(c.get("text") or "")                 # {"type": "text", "text": ...}
    else:
        caminho, texto = getattr(c, "path", None), getattr(c, "text", None)
        if caminho:
            arquivos.append(caminho)
        elif texto:
            textos.append(texto)


# ---------------------------------------------------------------------------
# 2. Escolher o que reenviar
# ---------------------------------------------------------------------------

def montar_historico(turnos, estrategia="janela", max_turnos=4, imagens_recentes=1, lado_max=768, resumo=""):
    """Transforma os turnos em mensagens para a API, aplicando a estratégia de memória.

    max_turnos:       quantas trocas (pergunta e resposta) a janela mantém
    imagens_recentes: quantas imagens do histórico são reenviadas como imagem; as outras viram texto
    lado_max:         as imagens reenviadas vão menores (768 px), porque já foram analisadas uma vez
    resumo:           texto do resumo dos turnos antigos (estratégia "resumo")
    """
    if estrategia not in ESTRATEGIAS:
        raise ValueError(f"estratégia desconhecida: {estrategia}. Use uma de {ESTRATEGIAS}.")
    if estrategia == "nenhuma":
        return []
    escolhidos = list(turnos) if estrategia == "completa" else list(turnos)[-2 * max_turnos:]

    # as imagens mais recentes continuam imagem; as antigas viram marcação de texto
    todas = [img for t in escolhidos for img in t.imagens]
    manter = set(todas[-imagens_recentes:]) if imagens_recentes else set()

    mensagens = []
    if estrategia == "resumo" and resumo:
        mensagens += [{"role": "user", "content": f"Resumo do que conversamos antes:\n{resumo}"},
                      {"role": "assistant", "content": "Entendido, vou considerar esse resumo."}]
    for t in escolhidos:
        if t.papel == "user" and t.imagens:
            partes = []
            for img in t.imagens:
                if img in manter:
                    partes.append(parte_imagem(img, lado_max))
                else:
                    partes.append(parte_texto(f"[imagem enviada antes: {Path(img).name}]"))
            partes.append(parte_texto(t.texto or "(sem texto)"))
            mensagens.append({"role": "user", "content": partes})
        else:
            mensagens.append({"role": t.papel, "content": t.texto or "(vazio)"})
    return mensagens


def estimar_tokens(mensagens):
    """Estimativa grosseira de tokens: cerca de 4 caracteres por token de texto e 258 por imagem.

    Serve para comparar estratégias e mostrar a ordem de grandeza na interface. O número exato
    vem do campo usage da resposta, e o custo de uma imagem varia com o provedor e a resolução.
    """
    total = 0
    for m in mensagens:
        c = m["content"] if isinstance(m, dict) else m
        if isinstance(c, str):
            total += len(c) // 4 + 4
        else:
            for p in c:
                if p.get("type") == "image_url":
                    total += TOKENS_POR_IMAGEM
                else:
                    total += len(p.get("text", "")) // 4 + 1
    return total


# ---------------------------------------------------------------------------
# 3. Memória para scripts e aplicações sem Gradio
# ---------------------------------------------------------------------------

class Memoria:
    """Guarda a conversa e devolve o histórico já recortado pela estratégia escolhida.

    No Gradio, o próprio componente guarda o histórico e o entrega à função a cada mensagem.
    Em um script ou em uma API própria, quem guarda é esta classe.
    """

    def __init__(self, estrategia="janela", max_turnos=4, imagens_recentes=1):
        self.estrategia = estrategia
        self.max_turnos = max_turnos
        self.imagens_recentes = imagens_recentes
        self.turnos = []
        self.resumo = ""
        self.chamadas_de_resumo = 0

    def historico(self):
        """Mensagens anteriores que vão junto com a próxima pergunta.

        Na estratégia 'resumo', quando a conversa passa da janela, as trocas mais antigas viram
        um resumo (uma chamada extra ao modelo) e só as mais recentes continuam inteiras.
        """
        if self.estrategia == "resumo" and len(self.turnos) > 2 * self.max_turnos:
            manter = 2 * max(1, self.max_turnos // 2)          # mantém metade da janela inteira
            antigos, self.turnos = self.turnos[:-manter], self.turnos[-manter:]
            self.resumo = resumir(antigos, self.resumo)
            self.chamadas_de_resumo += 1
        return montar_historico(self.turnos, self.estrategia, self.max_turnos, self.imagens_recentes,
                                resumo=self.resumo)

    def registrar(self, pergunta, resposta, imagens=()):
        """Acrescenta uma troca (pergunta e resposta) à memória."""
        self.turnos += [Turno("user", pergunta, [str(i) for i in imagens]), Turno("assistant", resposta)]


def resumir(turnos, resumo_anterior=""):
    """Pede ao modelo um resumo curto dos turnos (fatos, números, decisões e pedidos do usuário)."""
    from src.cliente import chamar_modelo          # importado aqui para evitar importação circular
    from src.prompts import carregar
    sistema, usuario = carregar("resumo_conversa")
    conversa = "\n".join(f"{'Usuário' if t.papel == 'user' else 'Assistente'}: {t.texto}"
                         + (f" [enviou {len(t.imagens)} imagem(ns)]" if t.imagens else "") for t in turnos)
    pedido = usuario.replace("{resumo_anterior}", resumo_anterior or "(nenhum)").replace("{conversa}", conversa)
    return chamar_modelo(pedido, sistema=sistema, max_tokens=250, etiqueta="resumo").conteudo.strip()
