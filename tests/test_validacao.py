import unittest

from src.esquemas import Item, NotaFiscal
from src.validacao import conferir


class ConferirValidacaoTests(unittest.TestCase):
    def test_itens_completos(self):
        nota = NotaFiscal(
            emitente="Loja Exemplo",
            data="10/01/2024",
            valor_total=100.0,
            itens=[
                Item(descricao="Arroz", valor=60.0),
                Item(descricao="Feijão", valor=40.0),
            ],
        )

        self.assertEqual(conferir(nota), [])

    def test_item_sem_valor(self):
        nota = NotaFiscal(
            emitente="Loja Exemplo",
            data="10/01/2024",
            valor_total=100.0,
            itens=[
                Item(descricao="Arroz", valor=None),
                Item(descricao="Feijão", valor=100.0),
            ],
        )

        problemas = conferir(nota)
        self.assertIn("item com valor ausente: revisar", problemas)

    def test_lista_vazia(self):
        nota = NotaFiscal(
            emitente="Loja Exemplo",
            data="10/01/2024",
            valor_total=100.0,
            itens=[],
        )

        problemas = conferir(nota)
        self.assertIn("lista de itens vazia: revisar", problemas)


if __name__ == "__main__":
    unittest.main()
