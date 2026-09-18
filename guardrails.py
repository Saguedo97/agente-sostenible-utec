from __future__ import annotations

import re

CUI_RE = re.compile(r"^\d{6,10}$")

SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard previous",
    "system prompt",
    "developer message",
    "act as system",
    "jailbreak",
]


def validar_cui(cui: str) -> str:
    cui = str(cui).strip().replace(".0", "")
    if not CUI_RE.fullmatch(cui):
        raise ValueError("El CUI debe contener únicamente entre 6 y 10 dígitos.")
    return cui


def detectar_inyeccion(texto: str) -> list[str]:
    lower = (texto or "").lower()
    return [p for p in SUSPICIOUS_PATTERNS if p in lower]


def validar_candidato_basico(candidato: dict, cui: str) -> tuple[bool, list[str]]:
    problemas: list[str] = []

    if str(candidato.get("cui")) != str(cui):
        problemas.append("El CUI de la salida no coincide con el CUI solicitado.")

    clasificacion = candidato.get("clasificacion")
    if not clasificacion:
        problemas.append("Falta clasificacion.")

    evidencia_suficiente = candidato.get("evidencia_suficiente")
    if clasificacion == "Información insuficiente" and evidencia_suficiente is True:
        problemas.append(
            "Información insuficiente no puede marcar evidencia_suficiente=true."
        )

    if clasificacion not in {"No aplica", "Información insuficiente"}:
        if not candidato.get("paginas_marco"):
            problemas.append("La clasificación no cita páginas del Marco 2021.")
        if not candidato.get("evidencia_marco"):
            problemas.append("La clasificación no incluye evidencia normativa.")
        if not (
            candidato.get("evidencia_proyecto")
            or candidato.get("evidencia_brechas")
            or candidato.get("evidencia_marco_logico")
        ):
            problemas.append("La clasificación no incluye evidencia del proyecto.")

    paginas = candidato.get("paginas_marco", [])
    invalidas = [p for p in paginas if not isinstance(p, int) or p < 30 or p > 38]
    if invalidas:
        problemas.append(f"Páginas del Marco fuera del rango normativo esperado: {invalidas}")

    return (len(problemas) == 0, problemas)
