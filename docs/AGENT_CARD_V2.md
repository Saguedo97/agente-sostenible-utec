# AGENTIC PROFILE CARD — Investigador de Elegibilidad Sostenible V2

**Proyecto:** UTEC · Agentes IA · Evaluación de inversiones públicas peruanas  
**Autor del repositorio:** Saguedo97 · `agente-sostenible-utec`  
**Versión:** V2 experimental (octubre de 2026) · **Estado:** prototipo, pendiente de evaluación empírica

## 1. COMMUNICATION LAYER — Interacción
- **Interfaz:** Streamlit (`streamlit_app_v2.py`), entrada por CUI y elección de motor V1 / V2.
- **Usuario objetivo:** especialista en financiamiento sostenible o analista de inversión pública.
- **Salida:** diagnóstico preliminar documentado, categoría potencial, incertidumbres, requisitos de información, acciones recomendadas, herramientas, plan y trayectoria exportable en JSON.
- **Comunicación:** interfaz web con estado y auditoría; no pretende ser conversación general de propósito abierto.

## 2. DOMAIN DEFINITION — Problema
El Perú contiene un universo histórico aproximado de **500 mil proyectos de inversión pública**. Existe un **subconjunto de 121,477 CUIs** del archivo `Data 23_26.xlsx`, seleccionado por condiciones operativas definidas externamente, que incluyen actividad en 2023–2026 u otros criterios. Dentro de ese subconjunto hay **66,224 proyectos con devengado positivo** y **55,253 sin devengado positivo en dicho período**; los últimos pueden corresponder a proyectos aún no ejecutados y **no deben eliminarse** por defecto. Un conjunto separado de **423 CUIs históricamente clasificados** sirve para evaluación offline. Las reglas completas de selección del subconjunto no están formalizadas dentro del prototipo.

**Problema AS-IS:** un analista recibe un CUI, recupera datos y asigna una categoría del Marco del Bono Sostenible del Perú (2021), proceso susceptible de automatización repetitiva.

**Problema TO-BE:** investigar autónomamente hipótesis de elegibilidad y brechas de evidencia de cada inversión, especialmente cuando la documentación, la interpretación normativa o el estado de ejecución son ambiguos.

## 3. OBJECTIVES DEFINITION — Objetivos
1. Formular y **revisar planes de investigación** en función de observaciones y evidencia disponible.
2. Contrastar fichas de inversión pública, brechas de servicios y criterios de las **ocho categorías verdes** del Marco 2021 mediante RAG.
3. Activar de manera condicionada herramientas de visión y contraste experto, evitando llamadas innecesarias.
4. Identificar **evidencia documentada**, **incertidumbres**, **documentación requerida** y **acciones recomendadas**.
5. Permitir abstención/revisión humana, evitar filtración de etiquetas y registrar una trayectoria auditable.
6. Evaluar el beneficio de la autonomía frente al workflow de clasificación V1.

## 4. ENVIRONMENT — Datos y herramientas
| Recurso | Uso previsto | Limitación |
|---|---|---|
| `data/dataset_limpio_agente_sostenible.xlsx` | Variables y brechas de 423 CUIs; sin leer `GROUND_TRUTH` | Muestra histórica reducida |
| `Data 23_26.xlsx` → SQLite indexada local | Consulta por CUI de 121,477 proyectos | El XLSX no se publica; se requiere conversión previa |
| `rag.py` + Marco 2021 | Consultas por similitud o categoría a las ocho páginas normativas | No incorpora aún todos los criterios sociales y normas recientes |
| `consultar_marco_logico` | Extracción visual opcional si existe imagen | La implementación original utiliza una imagen por CUI |
| Dos especialistas LLM independientes | Contraste normativo/técnico cuando es útil | No constituye consenso documental ni debate multi-turno |
| `graph.py` V1 | Benchmark y comparación | Pipeline de clasificación estructurado |

**Herramientas expuestas al supervisor:** `normativa`, `vision`, `debate` (contraste especializado) y `finalizar`.

## 5. AUTONOMY — Decisiones no deterministas
El supervisor LLM recibe el estado del caso y produce una decisión estructurada con `accion`, `objetivo`, `motivo`, `plan_actualizado`, `consulta` y `categoria`. Tras cada observación, el control vuelve al supervisor: puede replantear consultas, activar otra herramienta o terminar. **La elección no está forzada a ejecutar todas las herramientas.**

**Guardrails deterministas:** máximo 6 pasos (configurable hasta 10), 3 búsquedas normativas, 1 visión y 1 contraste; páginas citadas deben estar entre las recuperadas; categorías sin página recuperada se degradan a información insuficiente.

**Autonomía real del prototipo:** planificación ligera y selección adaptativa. **No** es un sistema completamente autónomo con negociación multiagente compleja ni capacidad garantizada de investigar expedientes ajenos a los datos disponibles.

## 6. MEMORY AND REASONING — Estado y contexto
- **Corto plazo:** estado de ejecución en LangGraph: ficha, plan vigente, decisiones, evidencias, opiniones, contadores y trayectoria.
- **Largo plazo:** Marco 2021 y bases de datos externas persistidas; **no hay aprendizaje continuo ni memoria episódica**.
- **Razonamiento visible:** motivos breves de cada decisión y registro de acciones, nunca cadena de pensamiento privada.

## 7. CRITICALITY — Riesgos y mitigación
- **Falsos positivos / sobreconfianza:** etiqueta siempre *preliminar*, sin certificar ni aprobar financiamiento.
- **Evidencia inexistente / alucinación:** control de páginas recuperadas, abstención y revisión humana.
- **Ground-truth leakage:** excluir columnas históricas de cualquier herramienta de inferencia.
- **Prompt injection documental:** contenidos recuperados se tratan como datos, no instrucciones.
- **Costo / loops:** límites explícitos de pasos y herramientas; no ejecutar análisis masivos agénticos automáticamente.
- **Datos y privacidad:** base de 121k proyectos indexada localmente y excluida del repositorio; restringir un eventual despliegue público.
- **Falsa afirmación sobre consenso:** dos opiniones no son prueba; la conclusión requiere evidencia y posibilidad de desacuerdo.

## 8. HUMAN-IN-THE-LOOP — Intervención humana
La V2 **señala revisión humana**, pero **no implementa aún un flujo de aprobación/editado por especialista con reanudación de LangGraph**. El estado de revisión es una recomendación operativa, no una autorización institucional. La revisión formal y una política de escalamiento quedan como mejoras posteriores.

## 9. METRICS — Evaluación propuesta
**Baseline:** `graph.py` V1, mismos CUIs y corpus.  
**Set de pruebas:** CUIs con evidencia suficiente, ambigüedad normativa y evidencia incompleta (incluyendo proyectos aún sin devengado).  
**Métricas:** cobertura, precisión selectiva donde exista etiqueta comparable, abstenciones, hallazgos justificados, calidad de requerimientos documentales revisada por un especialista, pertinencia de llamadas, revisiones del plan, tiempo y costo por CUI, incidentes de citas inventadas.

**Advertencia:** los 423 CUIs no constituyen una muestra representativa de todas las categorías. La etiqueta histórica no determina por sí sola si las brechas documentales detectadas son correctas.

## 10. SUCCESS CRITERIA — Criterios de aceptación
La V2 debe mostrar, mediante trazas reales, al menos dos planes sustancialmente diferentes frente a casos de dificultad distinta, sin uso excesivo de herramientas, sin fuga de etiquetas y sin inventar criterios. **No se ha validado todavía contra la API ni con evaluación experta; no se afirma superioridad sobre V1.**
