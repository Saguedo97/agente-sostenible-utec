"""Checks offline sin OpenAI ni dependencias LangGraph."""
import importlib, os, sys, types, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
# router_cui solo necesita guardrails.validar_cui para los tests puros.
if 'guardrails' not in sys.modules:
    try: import guardrails
    except ImportError:
        g=types.ModuleType('guardrails');g.validar_cui=lambda x: str(x);sys.modules['guardrails']=g
from router_cui import unir_fuentes
from rag_multifuente import buscar_contexto, DB

class TestsV4(unittest.TestCase):
 def test_sin_datos(self):
    r=unir_fuentes('123',{'encontrado':False},{'encontrado':False})
    self.assertEqual(r['caso'],'no_encontrado')
 def test_423_ciego_y_union(self):
    h={'encontrado':True,'proyecto':{'NOMBRE_INVERSION':'Agua potable','COSTO_ACTUALIZADO':40},'brechas':[{'brecha':'agua'}]}
    u={'encontrado':True,'proyecto':{'NOMBRE_INVERSION':'Otra','DEVENGADO_2023':15,'DEPARTAMENTO':'JUNIN'}}
    r=unir_fuentes('123',h,u)
    self.assertEqual(r['caso'],'A_historico_423')
    self.assertEqual(r['proyecto']['NOMBRE_INVERSION'],'Agua potable')
    self.assertEqual(r['proyecto']['DEPARTAMENTO'],'JUNIN')
    self.assertNotIn('GROUND_TRUTH',str(r))
 def test_b_gasto(self):
    r=unir_fuentes('123',{}, {'encontrado':True,'proyecto':{'DEVENGADO_2025':10}})
    self.assertEqual(r['caso'],'B_universo_con_ejecucion')
 def test_c_inicio_confirmado(self):
    r=unir_fuentes('123',{}, {'encontrado':True,'proyecto':{'NO_HA_EMPEZADO':1,'DEVENGADO_2025':0}})
    self.assertEqual(r['caso'],'C_prospectivo_sin_inicio')
 def test_c_sin_gasto_ambiguo(self):
    r=unir_fuentes('123',{}, {'encontrado':True,'proyecto':{'DEVENGADO_2025':0}})
    self.assertEqual(r['caso'],'C_prospectivo_por_confirmar')
 def test_fts_presente(self):
    self.assertTrue(DB.exists())
    r=buscar_contexto('agua saneamiento cambio climatico',departamento='Junin')
    self.assertGreaterEqual(len(r),1)
    self.assertTrue(all(x['pagina']>0 and x['ambito']=='nacional' for x in r))
 def test_fts_lalibertad(self):
    r=buscar_contexto('inundaciones movimientos masa vulnerabilidad La Libertad',departamento='La Libertad',top_k=12)
    self.assertTrue(any('Cenepred' in x['documento'] for x in r))
 def test_fts_fuera_ambito(self):
    r=buscar_contexto('inundaciones movimientos masa vulnerabilidad La Libertad',departamento='Junin',top_k=12)
    self.assertFalse(any('Cenepred' in x['documento'] for x in r))

if __name__=='__main__':unittest.main()
