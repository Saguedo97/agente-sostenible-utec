from __future__ import annotations

import argparse
import json

from graph import clasificar_cui


def main():
    parser = argparse.ArgumentParser(description="Clasificador sostenible por CUI")
    parser.add_argument("cui", help="Código Único de Inversión")
    parser.add_argument("--trace", action="store_true", help="Muestra trayectoria resumida")
    args = parser.parse_args()

    state = clasificar_cui(args.cui)
    print("\n" + "=" * 90)
    print("RESULTADO")
    print("=" * 90)
    print(json.dumps(state["resultado"], ensure_ascii=False, indent=2))

    if args.trace:
        print("\n" + "=" * 90)
        print("TRAYECTORIA")
        print("=" * 90)
        print(json.dumps(state.get("trajectory", []), ensure_ascii=False, indent=2))
        if state.get("veredicto"):
            print("\nVEREDICTO FINAL")
            print(json.dumps(state["veredicto"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
