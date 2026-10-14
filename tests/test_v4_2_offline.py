"""Pruebas locales sin API, SQLite ni PDF de clasificación de V4.2."""
import ast
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from typing import Literal
from pydantic import BaseModel, Field, ValidationError

ROOT=Path(__file__).resolve().parents[1]

class TestsV42(unittest.TestCase):
    def _schema(self):
        source=(ROOT/'investigacion_v4.py').read_text(encoding='utf8')
        tree=ast.parse(source)
        defs=[]
        for n in tree.body:
            if isinstance(n,ast.Assign) and any(getattr(t,'id',None) in ('CATEGORIAS_PAGINAS','CategoriaMarco2021') for t in n.targets): defs.append(n)
            if isinstance(n,ast.AnnAssign) and getattr(n.target,'id',None)=='CategoriaMarco2021': defs.append(n)
            if isinstance(n,ast.ClassDef) and n.name=='Dictamen':defs.append(n)
        m=ast.fix_missing_locations(ast.Module(body=defs,type_ignores=[]))
        ns={'Literal':Literal,'BaseModel':BaseModel,'Field':Field}
        exec(compile(m,'schema','exec'),ns)
        return ns['Dictamen'],ns['CATEGORIAS_PAGINAS']
    def _dictamen(self,category):
        return dict(clasificacion_preliminar=category,certeza='media',explicacion='Prueba')
    def test_no_permite_pip_mayor(self):
        Schema,_=self._schema()
        with self.assertRaises(ValidationError):Schema.model_validate(self._dictamen('PIP Mayor'))
    def test_permita_agua_y_social_y_abstenerse(self):
        Schema,_=self._schema()
        for v in ['Gestión eficiente y resiliente de aguas y aguas residuales','Apoyo a grupos vulnerables y personas en situación de vulnerabilidad','Información insuficiente']:
            with self.subTest(v=v):self.assertEqual(Schema.model_validate(self._dictamen(v)).clasificacion_preliminar,v)
    def test_paginas_sectoriales(self):
        _,p=self._schema()
        self.assertEqual(p['Gestión eficiente y resiliente de aguas y aguas residuales'],{35})
        self.assertEqual(p['Eficiencia energética'],{33})
    def test_rag_favorece_saneamiento(self):
        import unicodedata,re
        def limpiar_palabras(s):return [x for x in re.findall(r'[a-z]{3,}',unicodedata.normalize('NFKD',s.lower())) if x not in ('de','la','del','para')]
        faux_rag=types.ModuleType('rag');faux_rag.MARCO_PATH='irrelevante'
        faux_ctx=types.ModuleType('rag_multifuente');faux_ctx.limpiar_palabras=limpiar_palabras
        oldrag=sys.modules.get('rag');oldctx=sys.modules.get('rag_multifuente')
        sys.modules['rag']=faux_rag;sys.modules['rag_multifuente']=faux_ctx
        try:
            spec=importlib.util.spec_from_file_location('rag_marco_v42_test',ROOT/'rag_marco_completo.py')
            mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
            mod._paginas=lambda:[(39,'Planificación y programación de inversiones públicas para cierre de brechas '*5),(35,'Construcción y ampliación de infraestructura de aguas residuales y saneamiento urbano '*5)]
            results=mod.buscar_criterios_completos('clasificación de inversión pública para ampliación de sistema de desagüe Acolla',top_k=2)
            self.assertEqual(results[0]['pagina'],35)
        finally:
            if oldrag is None:sys.modules.pop('rag',None)
            else:sys.modules['rag']=oldrag
            if oldctx is None:sys.modules.pop('rag_multifuente',None)
            else:sys.modules['rag_multifuente']=oldctx

if __name__=='__main__':unittest.main()
