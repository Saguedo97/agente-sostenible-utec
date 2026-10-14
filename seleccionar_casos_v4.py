"""Elige ejemplos B/C solo con SQLite local. No ejecuta OpenAI."""
import json, sqlite3
from router_cui import _num, _si
from universo_v2 import DB_PATH

def seleccionar():
    if not DB_PATH.exists():
        raise FileNotFoundError(f'Falta el universo indexado: {DB_PATH}')
    muestras={'B':None,'C':None,'C_por_confirmar':None}
    with sqlite3.connect(f'file:{DB_PATH.resolve()}?mode=ro',uri=True) as conn:
        for cui,payload in conn.execute('SELECT cui,payload FROM proyectos'):
            p=json.loads(payload)
            nombre=p.get('NOMBRE_INVERSION') or ''
            if len(nombre)<35:continue
            gastos=[_num(p.get('DEVENGADO_'+str(y))) for y in (2023,2024,2025,2026)]
            empezado=_si(p.get('EMPEZO'))
            no_empezo=_si(p.get('NO_HA_EMPEZADO'))
            primero=p.get('PRIMER_DEVENGADO')
            if muestras['B'] is None and sum(gastos)>0:
                muestras['B']={'cui':cui,'nombre':nombre[:110],'devengado_23_26':round(sum(gastos),2)}
            elif not any(gastos) and no_empezo and not empezado and not primero and muestras['C'] is None:
                muestras['C']={'cui':cui,'nombre':nombre[:110],'nota':'Sin inicio según campos disponibles; verificar antes de informar'}
            elif not any(gastos) and muestras['C_por_confirmar'] is None:
                muestras['C_por_confirmar']={'cui':cui,'nombre':nombre[:110],'nota':'No hay gasto reciente, etapa no confirmada'}
            if muestras['B'] and muestras['C']:break
    return muestras
if __name__=='__main__':print(json.dumps(seleccionar(),ensure_ascii=False,indent=2))
