"""Regras de negócio: a terceira camada de validação (Encontro 2, bloco 2.1).

O esquema garante o formato; estas regras conferem se os valores fazem sentido juntos.
Uma nota com qualquer problema vai para revisão humana. A regra extra deste módulo exige
revisão quando a lista de itens estiver vazia ou quando houver algum item com valor ausente,
mesmo que o valor_total esteja preenchido, porque não há como confirmar o cupom sem dados
suficientes para validar o total e os itens.
"""
from datetime import datetime

from src.esquemas import NotaFiscal

LIMITE_REVISAO = 5000.00     # acima deste valor, alguém confere mesmo que tudo pareça certo
TOLERANCIA = 0.05            # diferença aceitável entre o total e a soma dos itens (arredondamentos)


def conferir(nota: NotaFiscal) -> list[str]:
    """Devolve a lista de problemas encontrados; lista vazia = a nota pode seguir automaticamente.

    A nota também deve ir para revisão quando a lista de itens estiver vazia ou quando qualquer
    item tiver valor ausente, mesmo que o valor_total esteja preenchido.
    """
    problemas = []
    if not nota.emitente:
        problemas.append("emitente não encontrado")
    if nota.valor_total is None:
        problemas.append("total não encontrado")
    try:
        data = datetime.strptime(nota.data or "", "%d/%m/%Y")
        if data > datetime.now():
            problemas.append("data no futuro")
    except ValueError:
        problemas.append("data ausente ou inválida")
    if not nota.itens:
        problemas.append("lista de itens vazia: revisar")
    if any(i.valor is None for i in nota.itens):
        problemas.append("item com valor ausente: revisar")
    valores = [i.valor for i in nota.itens if i.valor is not None]
    if nota.valor_total is not None and valores and abs(sum(valores) - nota.valor_total) > TOLERANCIA:
        problemas.append(f"total ({nota.valor_total:.2f}) diferente da soma dos itens ({sum(valores):.2f})")
    if nota.valor_total is not None and nota.valor_total > LIMITE_REVISAO:
        problemas.append("valor alto: revisar")
    return problemas
