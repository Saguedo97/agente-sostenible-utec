"""Offline unit tests. Run: python -m unittest discover -s tests -p 'test_*.py'"""
import unittest
from unittest.mock import patch

import investigacion_v2 as v2


class InvestigacionV2Tests(unittest.TestCase):
    def test_ruta_depende_de_decision_del_supervisor(self):
        base = {"decision": {"accion": "vision"}, "pasos": 1, "contadores": {"normativa": 1, "vision": 0, "debate": 0}}
        self.assertEqual(v2.ruta(base), "vision")
        base["decision"]["accion"] = "debate"
        self.assertEqual(v2.ruta(base), "debate")
        base["decision"]["accion"] = "finalizar"
        self.assertEqual(v2.ruta(base), "finalizar")

    def test_no_repite_herramienta_agotada(self):
        state = {"decision": {"accion": "vision"}, "pasos": 1, "contadores": {"vision": 1}}
        self.assertEqual(v2.ruta(state), "finalizar")

    def test_cui_ausente_no_gasta_api(self):
        state = {"cui": "1234567", "proyecto": {"encontrado": False}, "evidencia": [], "trayectoria": []}
        with patch.object(v2, "_modelo", side_effect=AssertionError("No llamar al LLM")):
            self.assertEqual(v2.decidir(state)["decision"]["accion"], "finalizar")
            result = v2.finalizar(state)["diagnostico"]
        self.assertEqual(result["clasificacion_preliminar"], "Información insuficiente")
        self.assertTrue(result["requiere_revision_humana"])

    def test_citas_fuera_de_evidencia_se_descartan(self):
        state = {
            "cui": "2017723", "proyecto": {"encontrado": True}, "opiniones": [],
            "evidencia": [{"tipo": "normativa", "resultados": [{"pagina": 37, "texto": "Texto recuperado"}]}],
            "trayectoria": [], "contadores": {"normativa": 1},
        }
        propuesta = v2.Diagnostico(
            cui="2017723", clasificacion_preliminar="Agricultura sostenible",
            paginas_marco=[37, 38], explicacion="Conclusión preliminar"
        )
        class LLMFalso:
            def with_structured_output(self, schema):
                return self
            def invoke(self, prompt):
                return propuesta
        with patch.object(v2, "_modelo", return_value=LLMFalso()):
            result = v2.finalizar(state)["diagnostico"]
        self.assertEqual(result["paginas_marco"], [37])
        self.assertTrue(result["requiere_revision_humana"])
        self.assertTrue(result["advertencias_control"])


if __name__ == "__main__":
    unittest.main()
