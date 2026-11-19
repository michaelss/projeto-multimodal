"""Prática 1 · Nota fiscal em JSON validado (Encontro 2, bloco 2.1).

O que acontece:
1. Gera um cupom fictício em dados/exemplos/ (ou usa a foto que você indicar).
2. Pede ao modelo os campos no esquema NotaFiscal (saída estruturada com Pydantic).
3. Confere as regras de negócio e decide: segue automático ou vai para revisão.

Como rodar, a partir da pasta raiz do projeto:
    python praticas/p1_nota_fiscal.py                      # cupom de exemplo
    python praticas/p1_nota_fiscal.py dados/minha_nota.jpg # sua foto (sem dados pessoais)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cliente import chamar_modelo  # noqa: E402
from src.config import PASTA_DADOS  # noqa: E402
from src.esquemas import NotaFiscal  # noqa: E402
from src.midia import gerar_cupom, mensagem  # noqa: E402
from src.prompts import carregar  # noqa: E402
from src.validacao import conferir  # noqa: E402

# 1. A imagem: a sua foto, se indicada, ou um cupom de exemplo
if len(sys.argv) > 1:
    caminho = Path(sys.argv[1])
else:
    caminho = PASTA_DADOS / "exemplos" / "cupom_exemplo.png"
    gerar_cupom("LANCHONETE EXEMPLO LTDA", "31/10/2026",
                [("X-SALADA", 24.90), ("SUCO LARANJA", 9.00), ("PAO DE QUEIJO", 9.00)], caminho)
print("Imagem:", caminho)

# 2. A chamada com saída estruturada: o esquema vem da classe NotaFiscal
sistema, usuario = carregar("extracao_v1")
r = chamar_modelo(mensagem(usuario, [caminho]), esquema=NotaFiscal, sistema=sistema, etiqueta="p1")
nota = r.conteudo
print("\nNota extraída (já validada pelo Pydantic):")
print(nota.model_dump_json(indent=2))
print(f"\n{r.provedor} · {r.tok_entrada} tokens de entrada · {r.tok_saida} de saída · {r.latencia:.1f} s")

# 3. Regras de negócio: a terceira camada de validação
problemas = conferir(nota)
if problemas:
    print("\nDecisão: REVISÃO HUMANA. Problemas encontrados:")
    for p in problemas:
        print("  -", p)
    print("\nResposta bruta do modelo, antes da validação (útil para entender o erro):")
    print(r.bruto)
else:
    print("\nDecisão: segue automaticamente (nenhum problema nas regras de negócio).")
