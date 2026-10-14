"""Búsqueda lexical en TODO el Marco 2021; también cubre potenciales categorías sociales.
Mantiene criterio normativo separado de otros PDFs de políticas públicas.
"""
from __future__ import annotations
from functools import lru_cache
from rag import MARCO_PATH
from pypdf import PdfReader
from rag_multifuente import limpiar_palabras

@lru_cache(maxsize=1)
def _paginas():
    reader=PdfReader(str(MARCO_PATH))
    return [(i+1,' '.join((p.extract_text() or '').split())) for i,p in enumerate(reader.pages)]

def buscar_criterios_completos(consulta: str, top_k: int=3) -> list[dict]:
    palabras=limpiar_palabras(consulta)
    if not palabras: return []
    ranked=[]
    # Recuperar paginas sectoriales pertinentes; sin presuponer elegibilidad.
    import unicodedata
    q=unicodedata.normalize('NFKD',consulta.casefold())
    q=''.join(ch for ch in q if not unicodedata.combining(ch))
    anclas={
        35: ('agua potable','alcantarill','desague','saneamiento','aguas residuales'),
        37: ('agricultur','agrari','riego','cultiv'),
        38: ('residuos solidos','reciclaje','relleno sanitario'),
        34: ('transporte urbano','movilidad electrica','metro','trenes'),
        32: ('energia solar','fotovolta','eolica','energia renovable'),
        33: ('eficiencia energetica','electrific','iluminacion eficiente'),
        36: ('biodiversidad','areas naturales','conservacion de bosques','reforest'),
        31: ('edificio verde','edificaciones verdes'),
    }
    paginas_preferidas={page for page,patrones in anclas.items() if any(p in q for p in patrones)}
    for pagina,texto in _paginas():
        if len(texto)<45: continue
        low=texto.casefold()
        score=sum(min(low.count(t),6) for t in palabras)
        if pagina in paginas_preferidas: score+=80
        if score>0:
            ranked.append((score,pagina,texto))
    ranked.sort(key=lambda x:(-x[0],x[1]))
    return [{'fuente':'Marco del Bono Sostenible del Perú 2021','documento':'Marco 2021','pagina':p,'texto':t[:6000], 'tipo_fuente':'criterio_marco_2021','score':s} for s,p,t in ranked[:top_k]]
