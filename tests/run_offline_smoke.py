"""Dependency-free smoke runner for the pure logic of investigacion_v2.py."""
import sys, types, importlib.util, unittest, os
from pathlib import Path

dot=types.ModuleType('dotenv'); dot.load_dotenv=lambda:None; sys.modules['dotenv']=dot
lco = types.ModuleType('langchain_openai')
class ChatOpenAI:
    def __init__(self, **kwargs): pass
lco.ChatOpenAI=ChatOpenAI
sys.modules['langchain_openai']=lco

graphpkg = types.ModuleType('langgraph'); graphpkg.__path__=[]
graphmod = types.ModuleType('langgraph.graph')
class StateGraph:
    def __init__(self, *a): pass
    def add_node(self,*a): pass
    def add_edge(self,*a): pass
    def add_conditional_edges(self,*a): pass
    def compile(self):return self
graphmod.START='START';graphmod.END='END';graphmod.StateGraph=StateGraph
sys.modules['langgraph']=graphpkg;sys.modules['langgraph.graph']=graphmod

v=types.ModuleType('guardrails');v.validar_cui=lambda cui: cui;sys.modules['guardrails']=v
v=types.ModuleType('rag');v.buscar_marco=lambda **kw:[];sys.modules['rag']=v
v=types.ModuleType('toolbox')
v.obtener_proyecto_dict=lambda cui: {'encontrado':False}
v.consultar_marco_logico=types.SimpleNamespace(invoke=lambda args: '{}')
sys.modules['toolbox']=v
v=types.ModuleType('schemas')
from typing import Literal
v.Categoria=Literal['Edificios verdes','Energía renovable','Eficiencia energética','Transporte bajo en carbono','Gestión eficiente y resiliente de aguas y aguas residuales','Gestión sostenible de recursos naturales, uso de suelos y áreas marinas protegidas','Agricultura sostenible','Manejo sostenible de residuos','No aplica','Información insuficiente']
sys.modules['schemas']=v

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
spec=importlib.util.spec_from_file_location('investigacion_v2', str(Path(__file__).resolve().parents[1] / 'investigacion_v2.py'))
module=importlib.util.module_from_spec(spec);sys.modules['investigacion_v2']=module;spec.loader.exec_module(module)
suite=unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parent), pattern='test_investigacion_v2.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful(): raise SystemExit(1)
