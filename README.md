# Agente de IA para elegibilidad sostenible de proyectos públicos del Perú

**Proyecto académico · UTEC · LangGraph + RAG multifuente + Streamlit**

Prototipo de investigación documental que analiza proyectos de inversión pública por **Código Único de Inversión (CUI)** y evalúa su potencial alineamiento con el **Marco del Bono Sostenible del Perú (2021)**. Cuando la información es insuficiente, identifica vacíos de evidencia; para proyectos prospectivos, propone mejoras de documentación y diseño respaldadas en documentos de política pública.

> **Alcance:** herramienta de preevaluación. No certifica elegibilidad, no aprueba financiamiento y no sustituye el juicio de especialistas.

## Tres escenarios de investigación

| Caso | Población | Objetivo |
| --- | --- | --- |
| **A — Histórico** | 423 proyectos clasificados en emisiones anteriores | Inferencia sin revelar la etiqueta histórica; comparación posterior pendiente de evaluación masiva |
| **B — Con ejecución** | Proyectos del universo 2023–2026 sin etiqueta histórica y con ejecución observada | Proponer categoría elegible o abstenerse si falta evidencia |
| **C — Prospectivo** | Proyectos sin inicio confirmado, o por confirmar según datos disponibles | Recomendar información, indicadores o mejoras que fortalezcan su posible elegibilidad |

La base de proyectos del universo proviene de una **extracción local de Invierte.pe**, no de una consulta en vivo a su API. El gasto no determina por sí mismo la sostenibilidad, y no registrar devengado en 2023–2026 **no demuestra** ausencia de ejecución anterior.

## Cómo funciona V4

```text
CUI
  └─ router_cui.py: consulta ambas bases + determina escenario A/B/C
      └─ investigacion_v4.py: planificar → decidir siguiente acción
          ├─ consultar criterios de elegibilidad (Marco 2021)
          ├─ recuperar políticas y estadísticas (RAG contextual)
          ├─ inspeccionar datos disponibles del proyecto
          └─ reflexionar, actualizar plan, auditar cierre
              └─ diagnóstico preliminar + evidencia + trayectoria + recomendaciones
```

**Dos capas de fuentes, distintos roles:** el **Marco 2021** fundamenta criterios de elegibilidad; las **NDC, ENCC, estrategias de biodiversidad, MEF e INEI** aportan contexto y posibles recomendaciones. Las políticas nuevas **no se convierten automáticamente en requisitos** para proyectos históricos. El RAG contextual actual utiliza **SQLite FTS5 (búsqueda léxica)**, no búsqueda vectorial semántica.

La arquitectura mantiene los motores previos para comparación; **V4 es el motor recomendado para la demo**.

## Ejecutar localmente

**Requisitos:** Python, dependencias de `requirements.txt`, credenciales de OpenAI, la base histórica de muestra y, para B/C, la base SQLite local del universo. El índice documental local es necesario para recuperación contextual completa.

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Editar .env y configurar OPENAI_API_KEY. Nunca publicar .env.
streamlit run streamlit_app_v2.py
```

En la barra lateral, seleccionar **Investigador V4 (3 casos + RAG multifuente)** y escribir un CUI. **Consultar ficha (sin IA)** permite validar la ruta sin gastar créditos; **Ejecutar investigación** invoca modelos y consume API.

Si todavía no existe la base local del universo, prepararla desde la extracción original:

```powershell
python universo_v2.py preparar "RUTA_AL_EXCEL_ORIGINAL.xlsx"
```

El repositorio **no contiene** la base masiva de proyectos, documentos grandes, índice local ni claves. Por eso un clon limpio requiere esos archivos para reproducir exactamente las pruebas B/C y el RAG ampliado. El código fuente y la lógica sí están versionados.

## Evidencia de pruebas de funcionamiento

| Escenario | CUI usado en pruebas manuales | Observación |
| --- | --- | --- |
| A | `2017723` — saneamiento, Acolla | Ruta histórica operativa; una ejecución V4 anterior confundió tipología PIP con categoría sostenible; se incorporó control de categorías en V4.2 |
| B | `2000846` — electrificación, Chilete | Ruta con ejecución operativa; se abstuvo por evidencia insuficiente |
| C | `2045301` — desagüe, Chilca | Ruta prospectiva operativa; realizó consultas al Marco y contexto, con reflexión y recomendaciones |

Los tests `tests/test_v4_offline.py`, `tests/test_v4_1_offline.py` y `tests/test_v4_2_offline.py` comprueban componentes sin consumir API. **No equivalen a una evaluación cuantitativa completa frente a los 423 proyectos etiquetados**.

```powershell
python -m unittest discover -s tests -p "test_v4*_offline.py" -v
```

## Código principal

| Archivo | Responsabilidad |
| --- | --- |
| `streamlit_app_v2.py` | Interfaz Streamlit que permite seleccionar V1–V4 |
| `investigacion_v4.py` | Supervisor, planificación, herramientas, reflexión y auditoría |
| `router_cui.py` | Integración de las dos fuentes y enrutamiento A/B/C |
| `rag_marco_completo.py` | Recuperación del texto del Marco 2021 |
| `rag_multifuente.py` | Consulta al índice de políticas y estadísticas |
| `universo_v2.py` | Preparación y consulta del universo desde SQLite |
| `toolbox.py` | Acceso a ficha histórica y marcos lógicos disponibles |
| `tests/` | Tests automatizados |

Las versiones V1, V2 y V3 se conservan en la raíz **para no romper los imports existentes**. Su historia y limitaciones están documentadas en [docs/EVOLUCION.md](docs/EVOLUCION.md). La documentación antigua puede archivarse bajo `docs/historico/` sin modificar la ejecución.

## Limitaciones

- Evaluación humana indispensable para cualquier decisión real de elegibilidad.
- Disponibilidad irregular de expedientes y marcos lógicos; datos estructurados incompletos.
- Riesgos de selección incorrecta de páginas, afirmaciones demasiado generales y consultas repetidas.
- Evaluación masiva de exactitud, precisión y abstención contra los 423 casos: **pendiente**.
- La presencia de una fuente recuperada no implica que respalde todas las afirmaciones del dictamen.

**Trabajo futuro:** robustecer citas por afirmación, evaluación ciega en los 423 casos, control de consultas redundantes, ingestión reproducible del corpus, manejo de documentos técnicos y mejora de trazabilidad del razonamiento observable.
