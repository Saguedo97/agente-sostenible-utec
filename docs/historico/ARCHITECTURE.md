# Arquitectura del agente

## Objetivo

Dado un CUI, el sistema reúne evidencia estructurada y documental, consulta el
Marco del Bono Sostenible del Perú 2021, propone una clasificación verde o se
abstiene, y registra una trayectoria auditable.

## Flujo

```text
CUI
 │
 ▼
Agente de evidencia (agent.py)
 │
 ├─ obtener_proyecto()
 ├─ buscar_criterios_marco()
 └─ consultar_marco_logico() [cuando hace falta]
 │
 ▼
Clasificador estructurado
 │
 ▼
Validación determinista
 │
 ▼
Verificador semántico
 │
 ├─ aprobado -> resultado
 ├─ rechazado -> feedback -> agente
 └─ límite de iteraciones -> revisión humana
```

## Qué parte es agéntica

`agent.py` usa `create_agent`. El orden de herramientas, las consultas RAG, la
cantidad de búsquedas y el uso o no del marco lógico no están prefijados.

## Qué parte es determinista

`guardrails.py` y el routing de `graph.py` controlan reglas que no necesitan
creatividad: formato de CUI, requisitos mínimos de evidencia, límite de
iteraciones y estados finales.

## Anti-leakage

El agente puede consultar únicamente `PROYECTOS`, `BRECHAS`, el Marco 2021 y,
si existe, el marco lógico del CUI.

`GROUND_TRUTH` solo se abre desde `evaluate.py`, después de la inferencia.

## Estados finales

- `APROBADO`: el sistema cerró una clasificación sin requerir revisión humana.
- `REVISION_HUMANA`: abstención, evidencia incompleta, caso sensible o candidato
  marcado para revisión.

Que el verificador "apruebe" una abstención significa que considera correcta la
decisión de no clasificar; no significa que el proyecto haya sido aprobado como
sostenible.
