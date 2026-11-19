"""Confere o contrato de saída e os registros sem fazer chamadas à API."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src import cliente
from src.esquemas import NotaFiscal


class ContratoSaidaTest(unittest.TestCase):
    def executar(self, texto):
        """Simula uma resposta do provedor e devolve os mocks de chamada e registro."""
        resposta = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=texto))],
            usage=SimpleNamespace(prompt_tokens=123, completion_tokens=45),
        )
        criar = Mock(return_value=resposta)
        provedor = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=criar)))
        self.criar = criar
        with (
            patch.object(cliente, "clientes", {"teste": provedor}),
            patch.object(cliente, "ORDEM", ["teste"]),
            patch.dict(cliente.PROVEDORES, {"teste": {"modelo": "modelo-teste"}}),
            patch.object(cliente.uso, "registrar", self.registrar),
        ):
            return cliente.chamar_modelo("Leia o cupom.", esquema=NotaFiscal, usar_cache=False)

    def setUp(self):
        self.registrar = Mock()
        self.nota = {"emitente": "LOJA TESTE", "data": None, "valor_total": 10.0, "itens": []}

    def test_resposta_valida_preserva_null_e_declara_contrato(self):
        resposta = self.executar(json.dumps(self.nota))
        self.assertIsNone(resposta.conteudo.data)
        self.assertEqual(resposta.conteudo.valor_total, 10.0)
        self.assertEqual(self.registrar.call_args.args[2:4], (123, 45))
        self.assertNotIn("status", self.registrar.call_args.kwargs)
        sistema = self.criar.call_args.kwargs["messages"][0]["content"]
        self.assertIn("JSON Schema", sistema)
        self.assertIn("emitente", sistema)

    def test_objeto_envoltorio_e_rejeitado_e_contabilizado(self):
        with self.assertRaisesRegex(ValueError, "nao segue o esquema"):
            self.executar(json.dumps({"extracao": self.nota}))
        self.assertEqual(self.registrar.call_args.kwargs["status"], "erro_validacao")
        self.assertEqual(self.registrar.call_args.args[2:4], (123, 45))
        self.criar.assert_called_once()

    def test_json_incompleto_e_rejeitado_e_contabilizado(self):
        with self.assertRaisesRegex(ValueError, "nao segue o esquema"):
            self.executar('{"emitente":')
        self.assertEqual(self.registrar.call_args.kwargs["status"], "erro_validacao")
        self.criar.assert_called_once()


if __name__ == "__main__":
    unittest.main()
