"""RAG documental local para contexto y recomendaciones: SQLite FTS5.

No confundir este corpus con los CRITERIOS de elegibilidad del Marco 2021 (rag.py).
Para demo puede usarse el índice ya precalculado incluido en el ZIP: sin costos de embeddings.
Las referencias son documento + página física del PDF + fragmento.
"""
from __future__ import annotations
import argparse, json, re, sqlite3, unicodedata
from pathlib import Path

DB = Path(__file__).resolve().parent / 'data' / 'biblioteca_v4.sqlite'

CATALOGO = {
    'Documento-NDC-3.0_UNFCCC.pdf': ('politica', 'nacional', 'clima;agua;agricultura;mitigacion;adaptacion', 2025),
    'Actualización de las NDC del Perú al 2030.pdf': ('politica', 'nacional', 'clima;mitigacion;adaptacion', 2020),
    'Estrategia Nacional Frente Al Cambio Climatico.pdf': ('politica', 'nacional', 'clima;riesgos;adaptacion', 2025),
    'ESTRATEGIA NACIONAL DE DIVERSIDAD BIOLOGICA AL 2050.pdf': ('politica', 'nacional', 'biodiversidad;ecosistemas;bosques', 2024),
    'Estrategia Nacional de Div Biologica al 2050.pdf': ('norma_aprobatoria', 'nacional', 'biodiversidad', 2024),
    'Informe_cierre_de_brechas_2024_publicado.pdf': ('brechas', 'nacional', 'inversion_publica;brechas', 2024),
    'boletin_agua_2024.pdf': ('indicadores', 'nacional', 'agua;saneamiento', 2024),
    'boletin_condiciones_vida peru.pdf': ('indicadores', 'nacional', 'social;educacion;salud', 2025),
    'Evol Pobreza Monet 2015 2024.pdf': ('indicadores', 'nacional', 'pobreza;social', 2025),
    'INEI Poblacion 1950 2070.pdf': ('indicadores', 'nacional', 'demografia;poblacion', 2019),
    'informe-tecnico-empleo-nacional-primer-trimestre-2024.pdf': ('indicadores', 'nacional', 'empleo', 2024),
    'cifras-preliminares-del-sector-electrico-diciembre-2024.pdf': ('indicadores', 'nacional', 'energia;electricidad', 2025),
    'Cenepred Informe.pdf': ('riesgo', 'La Libertad', 'inundaciones;movimientos_masa', 2024),
    'estrategia gi activos pasivos _2025_2028.pdf': ('contexto_fiscal', 'nacional', 'gestion_deuda;tesoreria', 2024),
    'Ley Presupuesto 2025.pdf': ('contexto_fiscal', 'nacional', 'presupuesto;inversion_publica', 2024),
}

STOP = {'para','sobre','entre','desde','hasta','este','esta','como','cual','cuales','donde','quien','que','del','los','las','una','unos','unas','por','con','sin','proyecto','proyectos','peru','marco','sostenible','2021','2023','2024','2025','2026','analisis','criterios','informacion','documentacion'}


def limpiar_palabras(texto):
    s = unicodedata.normalize('NFKD', texto.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return [x for x in re.findall(r'[a-z]{3,}|\d{3,}', s) if x not in STOP][:18]


def _trocear(texto, longitud=1350):
    texto = ' '.join(texto.split())
    # Evitar trozos excesivamente cortos y respetar párrafos hasta lo posible.
    if len(texto) <= longitud:
        return [texto] if len(texto) > 50 else []
    return [texto[i:i+longitud] for i in range(0, len(texto), longitud-150) if len(texto[i:i+longitud]) > 90]


def indexar_carpeta(carpeta: str | Path, destino: str | Path=DB) -> dict:
    from pypdf import PdfReader
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix('.tmp')
    if tmp.exists(): tmp.unlink()
    conn = sqlite3.connect(tmp)
    cantidad=0; documentos=0; fallos=[]
    try:
        conn.execute('CREATE VIRTUAL TABLE fragmentos USING fts5(texto, nombre UNINDEXED, tipo UNINDEXED, ambito UNINDEXED, temas UNINDEXED, anio UNINDEXED, pagina UNINDEXED, tokenize="unicode61 remove_diacritics 2")')
        for nombre, meta in CATALOGO.items():
            ruta = Path(carpeta) / nombre
            if not ruta.exists():
                fallos.append(nombre)
                continue
            reader = PdfReader(str(ruta), strict=False)
            documentos += 1
            for pagina, page in enumerate(reader.pages, start=1):
                try: contenido = page.extract_text() or ''
                except Exception: continue
                for fragmento in _trocear(contenido):
                    conn.execute('INSERT INTO fragmentos(texto, nombre, tipo, ambito, temas, anio, pagina) VALUES (?,?,?,?,?,?,?)', (fragmento, nombre, meta[0], meta[1], meta[2], str(meta[3]), str(pagina)))
                    cantidad += 1
        conn.commit()
    finally:
        conn.close()
    tmp.replace(destino)
    return {'documentos': documentos, 'fragmentos': cantidad, 'faltantes': fallos, 'indice':str(destino)}


def _es_saneamiento(texto: str) -> bool:
    # Encaminamiento temático explícito: evita noticias eléctricas cuando el CUI es de desagüe.
    texto = unicodedata.normalize('NFKD', (texto or '').casefold())
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return any(x in texto for x in ('desague', 'alcantarillado', 'saneamiento',
                                    'agua potable', 'aguas residuales', 'tratamiento de agua'))


def _contexto_saneamiento(con, top_k: int) -> list[dict]:
    # Búsquedas enfocadas en documentos pertinentes, un fragmento por fuente.
    # Su contenido sigue siendo contextual: NO implica cumplimiento del Marco 2021.
    fuentes = [
        ('boletin_agua_2024.pdf', 'saneamiento acceso agua'),
        ('Informe_cierre_de_brechas_2024_publicado.pdf', 'saneamiento brechas'),
        ('Documento-NDC-3.0_UNFCCC.pdf', 'agua adaptacion resiliencia'),
        ('Estrategia Nacional Frente Al Cambio Climatico.pdf', 'agua adaptacion'),
        ('Actualización de las NDC del Perú al 2030.pdf', 'agua adaptacion'),
    ]
    salida = []
    for nombre, tema in fuentes:
        palabras = limpiar_palabras(tema)
        expresion = ' OR '.join('"' + t + '"' for t in dict.fromkeys(palabras))
        # El boletín de agua comienza con portada/presentación. Para desagüe,
        # priorizar su sección de indicadores de saneamiento (págs. 35+).
        filtro_pagina = ' AND CAST(pagina AS INTEGER) BETWEEN 35 AND 55' if nombre=='boletin_agua_2024.pdf' else ''
        fila = con.execute('SELECT texto,nombre,tipo,ambito,temas,anio,pagina FROM fragmentos '
                           'WHERE nombre=? AND fragmentos MATCH ?' + filtro_pagina +
                           ' ORDER BY bm25(fragmentos) LIMIT 1',
                           (nombre, expresion)).fetchone()
        if fila:
            salida.append({'texto':fila[0][:1250], 'documento':fila[1],
                           'tipo_fuente':fila[2], 'ambito':fila[3], 'temas':fila[4],
                           'anio':int(fila[5]), 'pagina':int(fila[6]),
                           'fuente':f'{fila[1]} (página PDF {fila[6]})'})
        if len(salida)>=top_k:
            break
    return salida


def buscar_contexto(consulta: str, top_k: int=4, temas: str='', departamento: str='') -> list[dict]:
    if not DB.exists(): return []
    palabras = limpiar_palabras(consulta + ' ' + temas)
    if not palabras: return []
    expresion = ' OR '.join('"' + p + '"' for p in dict.fromkeys(palabras))
    con = sqlite3.connect(f'file:{DB.resolve()}?mode=ro', uri=True)
    try:
        if _es_saneamiento(consulta + ' ' + temas):
            return _contexto_saneamiento(con, top_k)
        n = min(70, max(10, top_k*12))
        rows = con.execute('SELECT texto,nombre,tipo,ambito,temas,anio,pagina,bm25(fragmentos) AS puntuacion FROM fragmentos WHERE fragmentos MATCH ? ORDER BY puntuacion LIMIT ?', (expresion,n)).fetchall()
        # Política de ámbito: fuentes específicas solo para proyectos de ese departamento.
        departamento = (departamento or '').strip().casefold()
        elegibles=[]
        for r in rows:
            if r[3].lower() != 'nacional' and r[3].casefold() not in departamento: continue
            elegibles.append({'texto':r[0][:1250], 'documento':r[1], 'tipo_fuente':r[2], 'ambito':r[3], 'temas':r[4], 'anio':int(r[5]), 'pagina':int(r[6]), 'fuente':f'{r[1]} (página PDF {r[6]})'})
        # Diversificar: a lo sumo 2 fragmentos del mismo documento, hasta top_k.
        resultado=[]; cuotas={}
        for e in elegibles:
            if cuotas.get(e['documento'], 0)>=2: continue
            resultado.append(e)
            cuotas[e['documento']]=cuotas.get(e['documento'],0)+1
            if len(resultado)>=top_k: break
        return resultado
    finally:
        con.close()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('accion', choices=['indexar','buscar'])
    parser.add_argument('valor', help='Carpeta de PDFs o consulta')
    parser.add_argument('--departamento',default='')
    args=parser.parse_args()
    r=indexar_carpeta(args.valor) if args.accion=='indexar' else buscar_contexto(args.valor,departamento=args.departamento)
    print(json.dumps(r,ensure_ascii=False,indent=2))
