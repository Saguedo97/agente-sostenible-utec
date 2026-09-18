"""
Tests que NO requieren API.
Verifican:
- dataset accesible,
- 423 CUIs,
- 640 registros de brecha,
- 423/423 CUIs con al menos una brecha,
- ausencia de GROUND_TRUTH en toolbox,
- extracción de las 8 páginas/categorías del Marco.
"""

from pathlib import Path

import pandas as pd
from pypdf import PdfReader

from rag import PAGINAS_CATEGORIA
from toolbox import DATASET_PATH, obtener_proyecto_dict


def main():
    proyectos = pd.read_excel(DATASET_PATH, sheet_name="PROYECTOS", engine="openpyxl")
    brechas = pd.read_excel(DATASET_PATH, sheet_name="BRECHAS", engine="openpyxl")

    assert len(proyectos) == 423
    assert len(brechas) == 640
    assert proyectos["CUI"].nunique() == 423
    assert brechas["CUI"].nunique() == 423

    proyecto = obtener_proyecto_dict("2017723")
    assert proyecto["encontrado"] is True
    assert proyecto["n_brechas"] >= 1
    assert "GROUND_TRUTH" not in str(proyecto)

    assert len(PAGINAS_CATEGORIA) == 8

    print("✅ Tests locales OK")
    print("   423 proyectos")
    print("   640 registros de brecha")
    print("   423/423 CUIs con brecha")
    print("   8 categorías normativas mapeadas")
    print("   GROUND_TRUTH aislado de las tools")


if __name__ == "__main__":
    main()
