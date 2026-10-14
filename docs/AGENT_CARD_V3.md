# Agent Card · Investigador de elegibilidad sostenible V3

**Tipo:** agente orientado a objetivos con planificación, uso dinámico de herramientas, reflexión y replanning. **Alcance:** evaluación preliminar de proyectos de inversión pública del Perú conforme al Marco del Bono Sostenible 2021.

**Usuario:** analista de inversión pública, finanzas sostenibles o evaluador humano.

**Objetivo:** investigar criterios potencialmente aplicables, identificar evidencia disponible y documentar vacíos de información, **sin certificar elegibilidad**.

**Entradas:** CUI y ficha local en universo 2023–2026 (121,477 CUIs) o base histórica de 423 CUIs; PDF Marco 2021; imágenes de marcos lógicos cuando estén disponibles.

**Acciones posibles:** consulta normativa RAG, análisis visual, contraste normativo-técnico, replanning o finalizar.

**Autonomía:** crea tareas investigables, elige herramientas, evalúa observaciones, actualiza estados de tareas y modifica estrategia o termina cuando la evidencia o los límites lo justifican. El supervisor propone; controles deterministas validan estados y cierre.

**Memoria/estado:** memoria de ejecución LangGraph (`plan`, `evidencia`, `opiniones`, `contadores`, `trayectoria`) sin memoria persistente entre consultas. No afirmar memoria a largo plazo.

**Salidas:** clasificación potencial, justificación y páginas citadas, diagnóstico de brechas, recomendaciones, tareas resueltas/bloqueadas y trayectoria exportable JSON.

**Guardrails:** aislamiento `GROUND_TRUTH`, verificación de fuentes registradas, límites de pasos y llamadas, veto a cierres prematuros, decisión humana para casos incompletos.

**Limitaciones:** sin acceso automático a expedientes externos; página citada no valida por sí sola la interpretación; dictámenes independientes no equivalen a debate iterativo; resultados no son aprobación financiera.

**Evaluación:** comparar V1/V2/V3, tres escenarios de ambigüedad, calidad de evidencia por tarea, replanning justificado, precisión y cobertura donde exista etiqueta histórica, coste/latencia y revisión experta.
