"""Esquemas Pydantic: o contrato da resposta do modelo (Encontro 2, bloco 2.1).

Cada classe vira um JSON Schema com Classe.model_json_schema() e é enviada ao provedor.
Na volta, Classe.model_validate(...) confere os campos e os tipos.
Campos "X | None" permitem que o modelo diga "não encontrei" (null), em vez de inventar.
"""
import re

from pydantic import BaseModel, Field, field_validator


class Item(BaseModel):
    descricao: str
    valor: float | None = Field(description="valor do item em reais, número com ponto decimal")


class NotaFiscal(BaseModel):
    emitente: str | None = Field(description="nome do estabelecimento, como aparece no topo")
    data: str | None = Field(description="data da compra no formato DD/MM/AAAA, sem a hora")
    valor_total: float | None = Field(description="valor total em reais, número com ponto decimal")
    itens: list[Item] = Field(default_factory=list, description="itens comprados, na ordem do cupom")

    @field_validator("data", mode="before")
    @classmethod
    def normalizar_data(cls, valor):
        """Aceita a data em formatos comuns e devolve sempre DD/MM/AAAA.

        Modelos às vezes devolvem a data com a hora ("06/01/2022 12:12:39"), no formato ISO ("2022-01-06")
        ou com outro separador ("06.01.2022"). O validador do Pydantic corrige o formato antes da validação;
        o conteúdo (se a data existe e faz sentido) continua sendo conferido em src/validacao.py.
        """
        if valor is None:
            return None
        texto = str(valor).strip()
        br = re.search(r"(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})", texto)
        iso = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", texto)
        if iso:
            ano, mes, dia = iso.groups()
        elif br:
            dia, mes, ano = br.groups()
            if len(ano) == 2:
                ano = "20" + ano
        else:
            return texto or None
        return f"{int(dia):02d}/{int(mes):02d}/{ano}"
