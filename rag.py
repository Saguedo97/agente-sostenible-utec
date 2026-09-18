"""
RAG normativo del Marco del Bono Sostenible del Perú 2021.

El agente NO indexa RA2021/RA2023/RA2024 para evitar leakage.
Las páginas 31-38 del PDF corresponden a las ocho categorías verdes.
"""

from __future__ import annotations

import os
import unicodedata
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MARCO_PATH = Path(
    os.getenv(
        "MARCO_2021_PATH",
        BASE_DIR / "data" / "marco_bono_sostenible_peru_2021.pdf",
    )
)
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

PAGINAS_CATEGORIA = {
    31: "Edificios verdes",
    32: "Energía renovable",
    33: "Eficiencia energética",
    34: "Transporte bajo en carbono",
    35: "Gestión eficiente y resiliente de aguas y aguas residuales",
    36: "Gestión sostenible de recursos naturales, uso de suelos y áreas marinas protegidas",
    37: "Agricultura sostenible",
    38: "Manejo sostenible de residuos",
}

CATEGORIAS_VERDES = list(PAGINAS_CATEGORIA.values())


def _norm(texto: str) -> str:
    texto = (texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return " ".join(texto.split())


@lru_cache(maxsize=1)
def cargar_documentos_marco() -> list[Document]:
    if not MARCO_PATH.exists():
        raise FileNotFoundError(f"No se encontró el Marco 2021: {MARCO_PATH}")

    reader = PdfReader(str(MARCO_PATH))
    docs: list[Document] = []

    # Página 30: mapa general de las 8 categorías.
    overview_idx = 29
    if overview_idx < len(reader.pages):
        overview = " ".join((reader.pages[overview_idx].extract_text() or "").split())
        if overview:
            docs.append(
                Document(
                    page_content=overview,
                    metadata={
                        "fuente": "Marco del Bono Sostenible del Perú",
                        "anio": 2021,
                        "pagina_pdf": 30,
                        "categoria": "Resumen de categorías verdes",
                    },
                )
            )

    for pagina, categoria in PAGINAS_CATEGORIA.items():
        idx = pagina - 1
        if idx >= len(reader.pages):
            continue
        texto = " ".join((reader.pages[idx].extract_text() or "").split())
        if not texto:
            continue

        docs.append(
            Document(
                page_content=texto,
                metadata={
                    "fuente": "Marco del Bono Sostenible del Perú",
                    "anio": 2021,
                    "pagina_pdf": pagina,
                    "categoria": categoria,
                },
            )
        )

    if len(docs) < 8:
        raise RuntimeError(
            "No se extrajeron suficientes páginas normativas del Marco 2021."
        )
    return docs


@lru_cache(maxsize=1)
def obtener_vectorstore() -> InMemoryVectorStore:
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    store = InMemoryVectorStore(embedding=embeddings)
    store.add_documents(cargar_documentos_marco())
    return store


def _categoria_exacta(categoria: str) -> str | None:
    target = _norm(categoria)
    for oficial in CATEGORIAS_VERDES:
        if _norm(oficial) == target:
            return oficial
    return None


def buscar_marco(
    query: str,
    top_k: int = 4,
    categoria: str | None = None,
) -> list[dict]:
    query = (query or "").strip()
    if not query and not categoria:
        raise ValueError("Debes indicar query o categoria.")

    top_k = max(1, min(int(top_k), 8))

    # Si el agente ya identificó una categoría candidata, recuperación exacta y auditable.
    if categoria:
        oficial = _categoria_exacta(categoria)
        if oficial:
            docs = [
                d for d in cargar_documentos_marco()
                if d.metadata.get("categoria") == oficial
            ]
        else:
            docs = []
    else:
        docs = []

    # Si no hubo match exacto, búsqueda semántica.
    if not docs:
        docs = obtener_vectorstore().similarity_search(query, k=top_k)

    return [
        {
            "categoria": d.metadata.get("categoria"),
            "pagina": d.metadata.get("pagina_pdf"),
            "fuente": d.metadata.get("fuente"),
            "texto": d.page_content,
        }
        for d in docs[:top_k]
    ]
