"""Pruebas sin API ni dataset grande."""
import json
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path
from universo_v2 import consultar_universo, preparar_excel

class DatosV2Tests(unittest.TestCase):
    def test_consulta_indexada(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'u.sqlite'
            with closing(sqlite3.connect(p)) as con:
                con.execute('CREATE TABLE proyectos (cui TEXT PRIMARY KEY,payload TEXT NOT NULL)')
                con.execute('INSERT INTO proyectos VALUES (?, ?)', (
                    '1234567', json.dumps({'CODIGO_UNICO': 1234567, 'NOMBRE_INVERSION': 'Proyecto de prueba', 'TOTAL_DEV': 0, 'BRECHAS_TODAS': 'Agua', 'N_BRECHAS': 1})
                ))
                con.commit()
            r = consultar_universo('1234567', p)
            self.assertTrue(r['encontrado'])
            self.assertEqual(r['n_brechas'], 1)
            self.assertNotIn('GROUND_TRUTH', str(r))
            self.assertFalse(consultar_universo('8888888', p)['encontrado'])

    def test_ingesta_excel_minimo(self):
        from openpyxl import Workbook
        with tempfile.TemporaryDirectory() as d:
            x = Path(d)/'datos.xlsx'
            b = Workbook(); h=b.active;h.title='proyectos_terna_brechas'
            h.append(['CODIGO_UNICO','NOMBRE_INVERSION','TOTAL_DEV','BRECHAS_TODAS'])
            h.append([2345678,'Proyecto nuevo',0,'Transporte'])
            b.save(x)
            resultado=preparar_excel(x, Path(d)/'indice.sqlite')
            self.assertEqual(resultado['filas_leidas'],1)
            self.assertTrue(consultar_universo('2345678', Path(d)/'indice.sqlite')['encontrado'])

if __name__ == '__main__':
    unittest.main()
