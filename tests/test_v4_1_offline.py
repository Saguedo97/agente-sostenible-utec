"""Verificaciones sin consumo de API para el parche V4.1."""
import ast
import unittest
from pathlib import Path

from rag_multifuente import DB, buscar_contexto


class V41Tests(unittest.TestCase):
    def test_recuperacion_contexto_saneamiento(self):
        if not DB.exists():
            self.skipTest('Sin índice documental local')
        resultados = buscar_contexto(
            'AMPLIACION DEL SISTEMA DE DESAGUE DEL BARRIO ROMANCOTO II EN CHILCA JUNIN',
            top_k=5, departamento='JUNIN'
        )
        fuentes = [r['documento'] for r in resultados]
        self.assertTrue(any('boletin_agua' in f for f in fuentes))
        self.assertTrue(any('cierre_de_brechas' in f for f in fuentes))
        self.assertFalse(any('electrico' in f for f in fuentes))

    def test_citas_de_contexto_se_toman_del_retrieval(self):
        codigo = (Path(__file__).resolve().parents[1] / 'investigacion_v4.py').read_text(encoding='utf-8')
        ast.parse(codigo)
        self.assertIn("d['fuentes_contexto']=contexto_recuperado", codigo)

    def test_existe_control_de_consulta_repetida(self):
        codigo = (Path(__file__).resolve().parents[1] / 'investigacion_v4.py').read_text(encoding='utf-8')
        self.assertIn("x['motivo']='La consulta ya se ejecutó", codigo)


if __name__ == '__main__':
    unittest.main()
