"""Cliente de LLM: a única porta de saída para os provedores (Encontros 2 e 3).

Reúne o que uma chamada em produção precisa:
- retentativa só para erros temporários, com backoff exponencial e jitter;
- respeito ao cabeçalho retry-after;
- timeout em toda chamada;
- provedor reserva;
- cache de respostas;
- saída estruturada (JSON Schema a partir de uma classe Pydantic), com descida de nível se o provedor recusar;
- registro de uso (tokens, latência e custo) em logs/uso.csv.

Encontro 3 acrescenta:
- historico: as mensagens anteriores da conversa (a API não guarda nada entre chamadas);
- chamar_modelo_stream: a resposta chega em pedaços, para a interface mostrar enquanto o modelo escreve;
- transcrever: áudio para texto (Whisper), pelo mesmo cliente.
"""
import hashlib
import json
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI
from pydantic import ValidationError

from src import uso
from src.config import PROVEDOR, PROVEDORES, ler_chave

REPETIR = {408, 429, 500, 502, 503, 504}        # erros temporários: vale tentar de novo
CACHE = {}

# Um cliente por provedor com chave cadastrada; ORDEM = principal primeiro, depois as reservas
clientes = {nome: OpenAI(api_key=ler_chave(cfg["chave"]), base_url=cfg["base_url"])
            for nome, cfg in PROVEDORES.items() if ler_chave(cfg["chave"])}
ORDEM = [PROVEDOR] + [p for p in clientes if p != PROVEDOR] if PROVEDOR in clientes else list(clientes)


@dataclass
class Resposta:
    conteudo: object          # texto ou objeto Pydantic
    tok_entrada: int
    tok_saida: int
    provedor: str
    modelo: str
    latencia: float
    do_cache: bool = False
    bruto: str = ""            # texto exatamente como o modelo devolveu, antes da validação


def _codigo(erro):
    return getattr(erro, "status_code", None)


def _retry_after(erro):
    """Segundos indicados pelo provedor no cabeçalho retry-after, se houver."""
    try:
        return float(erro.response.headers.get("retry-after"))
    except Exception:
        return None


def _espera(erro, tentativa, base=1.0):
    """retry-after tem prioridade; senão, sorteio entre 0 e base × 2^tentativa (full jitter)."""
    ra = _retry_after(erro)
    return ra if ra is not None else random.uniform(0, base * 2 ** tentativa)


def _extrair_json(texto):
    """Lê JSON mesmo quando o modelo o envolve em texto ou em blocos de código."""
    try:
        return json.loads(texto)
    except Exception:
        achado = re.search(r"\{.*\}", texto or "", re.S)
        return json.loads(achado.group(0)) if achado else {}


def _formatos(esquema):
    """Níveis de saída estruturada, do mais forte ao mais fraco (slide 'Três níveis de garantia')."""
    if esquema is None:
        return [None]
    return [{"type": "json_schema", "json_schema": {"name": esquema.__name__, "schema": esquema.model_json_schema()}},
            {"type": "json_object"},
            None]


def _resumo_erros(erro):
    """Erros de validação em poucas linhas, no formato campo: mensagem (vão de volta para o modelo)."""
    if isinstance(erro, ValidationError):
        return "; ".join(f"{'.'.join(str(x) for x in e['loc']) or 'raiz'}: {e['msg']}" for e in erro.errors()[:8])
    return f"JSON inválido ({erro})"


def _com_esquema(mensagens, esquema):
    """Nos níveis 2 e 3 o provedor não recebe o JSON Schema: então o esquema vai escrito no prompt.

    Sem isso, o modelo só "adivinha" as chaves pelo texto do pedido e pode devolver valores de exemplo
    (como "data": "data-nota-fiscal") ou listas vazias. No nível 2 (json_object), alguns provedores
    também exigem a palavra JSON nas mensagens.
    """
    regra = ("Responda somente com um objeto JSON válido, sem texto antes ou depois, que siga este JSON Schema "
             "(use os valores lidos no documento, nunca textos de exemplo; null quando não encontrar):\n"
             + json.dumps(esquema.model_json_schema(), ensure_ascii=False))
    if mensagens and mensagens[0]["role"] == "system":
        return [{"role": "system", "content": mensagens[0]["content"] + "\n\n" + regra}] + mensagens[1:]
    return [{"role": "system", "content": regra}] + mensagens


def _mensagens(conteudo, sistema=None, historico=None):
    """Monta a lista enviada à API: sistema, depois o histórico da conversa, depois a pergunta nova."""
    return (([{"role": "system", "content": sistema}] if sistema else [])
            + list(historico or [])
            + [{"role": "user", "content": conteudo}])


def chamar_modelo(conteudo, esquema=None, sistema=None, historico=None, max_tokens=600, tentativas=4,
                  usar_cache=True, etiqueta="", timeout=60, max_correcoes=2):
    """Envia uma mensagem (texto ou lista com texto e imagens) e devolve um objeto Resposta.

    conteudo:  texto, ou lista de partes {"type": "text"|"image_url", ...}
    esquema:   classe Pydantic; se informada, a resposta volta como objeto validado
    sistema:   instruções fixas da aplicação (mensagem de sistema)
    historico: mensagens anteriores [{"role": "user"|"assistant", "content": ...}], já recortadas
               pela estratégia de memória (src/contexto.py)
    max_correcoes: quantas vezes devolver ao modelo uma resposta fora do esquema, pedindo a correção
    """
    if not clientes:
        raise RuntimeError("Nenhuma chave encontrada. Copie .env.example para .env e preencha GROQ_API_KEY ou GEMINI_API_KEY.")
    mensagens = _mensagens(conteudo, sistema, historico)

    # 1. Cache: mesmo pedido -> mesma impressão digital (hash) -> resposta guardada
    chave_cache = hashlib.sha256(json.dumps([mensagens, esquema.__name__ if esquema else None]).encode()).hexdigest()
    if usar_cache and chave_cache in CACHE:
        r = CACHE[chave_cache]
        return Resposta(r.conteudo, r.tok_entrada, r.tok_saida, r.provedor, r.modelo, 0.0, do_cache=True, bruto=r.bruto)

    ultimo_erro = None
    for prov in ORDEM:                                         # 2. principal, depois reservas
        modelo = PROVEDORES[prov]["modelo"]
        formatos = _formatos(esquema)
        nivel = 0
        correcoes = 0
        t = 0
        while t < tentativas:                                  # 3. tentativas para erros temporários
            msgs = mensagens if (esquema is None or nivel == 0) else _com_esquema(mensagens, esquema)
            args = dict(model=modelo, messages=msgs, max_tokens=max_tokens, timeout=timeout)
            if formatos[nivel] is not None:
                args["response_format"] = formatos[nivel]
            inicio = time.time()
            try:
                r = clientes[prov].chat.completions.create(**args)
            except Exception as erro:
                ultimo_erro = erro
                cod = _codigo(erro)
                if cod == 400 and esquema is not None and nivel < len(formatos) - 1:
                    nivel += 1                                 # 4. provedor recusou o formato: desce um nível
                    print(f"[{prov}] formato não aceito; tentando nível de saída {nivel + 1}")
                    continue
                if cod in REPETIR and t < tentativas - 1:
                    espera = _espera(erro, t)
                    print(f"[{prov}] erro {cod}; nova tentativa em {espera:.1f} s")
                    uso.registrar(prov, modelo, 0, 0, time.time() - inicio, status=f"erro {cod}", etiqueta=etiqueta)
                    time.sleep(espera)
                    t += 1
                    continue
                print(f"[{prov}] erro {cod or type(erro).__name__}: passando para o próximo provedor")
                uso.registrar(prov, modelo, 0, 0, time.time() - inicio, status=f"erro {cod}", etiqueta=etiqueta)
                break
            latencia = time.time() - inicio
            texto = r.choices[0].message.content
            tok_in, tok_out = r.usage.prompt_tokens, r.usage.completion_tokens
            uso.registrar(prov, modelo, tok_in, tok_out, latencia, etiqueta=etiqueta)   # 5. registro de uso
            try:
                saida = esquema.model_validate(_extrair_json(texto)) if esquema else texto   # 6. validação Pydantic
            except (ValidationError, ValueError) as erro:
                # 7. Autocorreção: devolve ao modelo a própria resposta e os erros, e pede o JSON corrigido.
                #    É o que frameworks como o Pydantic AI fazem com retries (Encontro 4).
                if correcoes >= max_correcoes:
                    raise
                correcoes += 1
                print(f"[{prov}] resposta fora do esquema; pedindo correção ({correcoes}/{max_correcoes})")
                mensagens = mensagens + [
                    {"role": "assistant", "content": texto or ""},
                    {"role": "user", "content": "A resposta acima não segue o esquema. Erros: " + _resumo_erros(erro)
                     + "\nResponda de novo, somente com o objeto JSON corrigido, usando exatamente as chaves do esquema "
                       "e os valores lidos no documento."}]
                continue
            resp = Resposta(saida, tok_in, tok_out, prov, modelo, latencia, bruto=texto)
            CACHE[chave_cache] = resp
            return resp
    raise RuntimeError(f"Nenhum provedor respondeu. Último erro: {ultimo_erro}")


# ---------------------------------------------------------------------------
# Encontro 3 · streaming: a resposta chega em pedaços
# ---------------------------------------------------------------------------

def _uso_do_pedaco(pedaco):
    """Tokens informados no último pedaço do stream. OpenAI e Gemini usam 'usage'; o Groq também usa 'x_groq.usage'."""
    u = getattr(pedaco, "usage", None)
    if u is None:
        extra = getattr(pedaco, "x_groq", None)
        u = extra.get("usage") if isinstance(extra, dict) else getattr(extra, "usage", None)
    if u is None:
        return None
    ler = (lambda k: u.get(k)) if isinstance(u, dict) else (lambda k: getattr(u, k, None))
    return ler("prompt_tokens"), ler("completion_tokens")


def chamar_modelo_stream(conteudo, sistema=None, historico=None, max_tokens=800, tentativas=3,
                         etiqueta="", timeout=60, info=None):
    """Igual a chamar_modelo, mas devolve um gerador: cada 'yield' é um pedaço novo do texto.

    Uso:
        for pedaco in chamar_modelo_stream("Explique streaming"):
            print(pedaco, end="", flush=True)

    info: dicionário opcional; ao final recebe provedor, modelo, tokens, latência e tempo até o primeiro pedaço.
    Retentativa e troca de provedor só acontecem ANTES do primeiro pedaço: depois que o texto começou
    a aparecer na tela, recomeçar em outro provedor confundiria o usuário.
    """
    if not clientes:
        raise RuntimeError("Nenhuma chave encontrada. Copie .env.example para .env e preencha GROQ_API_KEY ou GEMINI_API_KEY.")
    mensagens = _mensagens(conteudo, sistema, historico)
    info = info if info is not None else {}
    ultimo_erro = None
    for prov in ORDEM:
        modelo = PROVEDORES[prov]["modelo"]
        pedir_uso = True                                       # stream_options: pede os tokens no último pedaço
        t = 0
        while t < tentativas:
            args = dict(model=modelo, messages=mensagens, max_tokens=max_tokens, timeout=timeout, stream=True)
            if pedir_uso:
                args["stream_options"] = {"include_usage": True}
            inicio = time.time()
            try:
                stream = clientes[prov].chat.completions.create(**args)
            except Exception as erro:
                ultimo_erro = erro
                cod = _codigo(erro)
                if cod == 400 and pedir_uso:
                    pedir_uso = False                          # provedor não aceita stream_options: tenta sem
                    continue
                if cod in REPETIR and t < tentativas - 1:
                    espera = _espera(erro, t)
                    print(f"[{prov}] erro {cod}; nova tentativa em {espera:.1f} s")
                    time.sleep(espera)
                    t += 1
                    continue
                print(f"[{prov}] erro {cod or type(erro).__name__}: passando para o próximo provedor")
                uso.registrar(prov, modelo, 0, 0, time.time() - inicio, status=f"erro {cod}", etiqueta=etiqueta)
                break

            texto, primeiro, tokens = "", None, None
            for pedaco in stream:
                if pedaco.choices:
                    delta = pedaco.choices[0].delta.content or ""
                    if delta:
                        if primeiro is None:
                            primeiro = time.time() - inicio    # TTFT: tempo até o primeiro pedaço
                        texto += delta
                        yield delta
                tokens = _uso_do_pedaco(pedaco) or tokens
            latencia = time.time() - inicio
            status = "ok"
            if not tokens or tokens[0] is None:                # sem contagem do provedor: estimativa grosseira
                tokens = (_estimar(mensagens), max(1, len(texto) // 4))
                status = "ok (tokens estimados)"
            uso.registrar(prov, modelo, tokens[0], tokens[1], latencia, status=status, etiqueta=etiqueta)
            info.update(provedor=prov, modelo=modelo, tok_entrada=tokens[0], tok_saida=tokens[1],
                        latencia=latencia, ttft=primeiro or latencia, custo=uso.custo(prov, *tokens), texto=texto)
            return
    raise RuntimeError(f"Nenhum provedor respondeu. Último erro: {ultimo_erro}")


def _estimar(mensagens):
    """Estimativa grosseira de tokens de entrada: cerca de 4 caracteres por token e 258 por imagem."""
    from src.contexto import estimar_tokens
    return estimar_tokens(mensagens)


# ---------------------------------------------------------------------------
# Encontro 3 · áudio para texto (reconhecimento de fala)
# ---------------------------------------------------------------------------

def transcrever(caminho, idioma="pt", etiqueta="stt", timeout=120):
    """Transcreve um arquivo de áudio (mp3, wav, m4a, ogg, webm...) e devolve o texto.

    Usa o primeiro provedor da ORDEM que tenha modelo de transcrição (no config, campo 'stt').
    O endpoint é outro (/audio/transcriptions) e o arquivo vai como upload, não como JSON.
    """
    candidatos = [p for p in ORDEM if PROVEDORES[p].get("stt")]
    if not candidatos:
        raise RuntimeError("Transcrição precisa de uma chave do Groq (GROQ_API_KEY) ou da OpenAI no arquivo .env.")
    ultimo_erro = None
    for prov in candidatos:
        modelo = PROVEDORES[prov]["stt"]
        inicio = time.time()
        try:
            with open(caminho, "rb") as f:
                r = clientes[prov].audio.transcriptions.create(model=modelo, file=(Path(caminho).name, f.read()),
                                                               language=idioma, timeout=timeout)
        except Exception as erro:
            ultimo_erro = erro
            print(f"[{prov}] transcrição falhou: {_codigo(erro) or type(erro).__name__}")
            uso.registrar(prov, modelo, 0, 0, time.time() - inicio, status=f"erro {_codigo(erro)}", etiqueta=etiqueta)
            continue
        texto = getattr(r, "text", None) or (r if isinstance(r, str) else "")
        uso.registrar(prov, modelo, 0, 0, time.time() - inicio, etiqueta=etiqueta,
                      segundos_audio=_duracao(caminho))
        return texto.strip()
    raise RuntimeError(f"Não foi possível transcrever o áudio. Último erro: {ultimo_erro}")


def _duracao(caminho):
    """Duração do áudio em segundos, quando dá para ler sem bibliotecas extras (WAV); senão None."""
    try:
        import wave
        with wave.open(str(caminho)) as w:
            return w.getnframes() / w.getframerate()
    except Exception:
        return None
