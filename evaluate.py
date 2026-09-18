"""
Benchmark contra GROUND_TRUTH.

Importante:
- Este módulo SÍ lee GROUND_TRUTH.
- Ningún módulo de inferencia importa evaluate.py.
- Por defecto corre solo 10 casos para controlar costo.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from graph import clasificar_cui

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = Path(
    os.getenv(
        "DATASET_PATH",
        BASE_DIR / "data" / "dataset_limpio_agente_sostenible.xlsx",
    )
)
OUT_DIR = BASE_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True)


def cargar_ground_truth() -> pd.DataFrame:
    gt = pd.read_excel(DATASET_PATH, sheet_name="GROUND_TRUTH", engine="openpyxl")
    gt["CUI"] = gt["CUI"].astype(str).str.replace(r"\.0$", "", regex=True)
    gt = gt[gt["CONFLICTO_GROUND_TRUTH"].astype(str).str.upper() != "SI"].copy()
    gt = gt[
        gt["CLASIFICACION_CONSOLIDADA_PRELIMINAR"].notna()
        & (gt["CLASIFICACION_CONSOLIDADA_PRELIMINAR"] != "")
    ].copy()
    return gt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    gt = cargar_ground_truth()
    if not args.all:
        n = min(args.limit, len(gt))
        gt = gt.sample(n=n, random_state=args.seed)

    records = []

    for i, row in enumerate(gt.itertuples(index=False), 1):
        cui = str(row.CUI)
        real = row.CLASIFICACION_CONSOLIDADA_PRELIMINAR
        print(f"[{i}/{len(gt)}] CUI {cui}")

        try:
            state = clasificar_cui(cui)
            result = state["resultado"]
            pred = result["clasificacion"]
            records.append(
                {
                    "CUI": cui,
                    "REAL": real,
                    "PRED": pred,
                    "CORRECTO": int(pred == real),
                    "ESTADO": result["estado"],
                    "EVIDENCIA_SUFICIENTE": result["evidencia_suficiente"],
                    "ITERACIONES": result["iteraciones"],
                    "N_TOOL_CALLS": len(state.get("tool_calls", [])),
                    "HERRAMIENTAS": " | ".join(result["herramientas_utilizadas"]),
                    "CONSULTAS_MARCO": " | ".join(result["consultas_marco"]),
                    "JUSTIFICACION": result["justificacion"],
                    "ERROR": "",
                }
            )
        except Exception as e:
            records.append(
                {
                    "CUI": cui,
                    "REAL": real,
                    "PRED": "ERROR",
                    "CORRECTO": 0,
                    "ESTADO": "ERROR",
                    "EVIDENCIA_SUFICIENTE": False,
                    "ITERACIONES": 0,
                    "N_TOOL_CALLS": 0,
                    "HERRAMIENTAS": "",
                    "CONSULTAS_MARCO": "",
                    "JUSTIFICACION": "",
                    "ERROR": repr(e),
                }
            )

    df = pd.DataFrame(records)

    evaluables = df[~df["PRED"].isin(["ERROR", "Información insuficiente"])]
    coverage = len(evaluables) / len(df) if len(df) else 0.0

    metrics = {
        "n": len(df),
        "coverage": coverage,
        "abstention_rate": float((df["PRED"] == "Información insuficiente").mean()),
        "error_rate": float((df["PRED"] == "ERROR").mean()),
    }

    if len(evaluables):
        metrics["selective_accuracy"] = accuracy_score(evaluables["REAL"], evaluables["PRED"])
        metrics["macro_f1_selective"] = f1_score(
            evaluables["REAL"],
            evaluables["PRED"],
            average="macro",
            zero_division=0,
        )
        metrics["classification_report"] = classification_report(
            evaluables["REAL"],
            evaluables["PRED"],
            zero_division=0,
            output_dict=True,
        )

        labels = sorted(set(evaluables["REAL"]) | set(evaluables["PRED"]))
        metrics["confusion_matrix_labels"] = labels
        metrics["confusion_matrix"] = confusion_matrix(
            evaluables["REAL"],
            evaluables["PRED"],
            labels=labels,
        ).tolist()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = OUT_DIR / f"benchmark_{timestamp}.csv"
    json_path = OUT_DIR / f"metrics_{timestamp}.json"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    json_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nMÉTRICAS")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"\nResultados: {csv_path}")
    print(f"Métricas:   {json_path}")


if __name__ == "__main__":
    main()
