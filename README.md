# Agente de Clasificación Sostenible — Next Level

Arquitectura híbrida y auditable para clasificar proyectos de inversión pública
contra las categorías verdes del **Marco del Bono Sostenible del Perú 2021**.

## Qué cambió frente al MVP

Esta versión ya no es solo `RAG + tools`.

Incluye:

- agente ReAct que decide dinámicamente qué herramientas usar;
- RAG normativo sobre las 8 categorías verdes;
- tool multimodal opcional para marcos lógicos;
- salida estructurada con Pydantic;
- validación determinista;
- verificador semántico independiente;
- loop de feedback/autocorrección con LangGraph;
- límite de iteraciones y fallback a revisión humana;
- trajectory logging de tool calls y consultas RAG;
- benchmark separado contra ground truth;
- interfaz Streamlit opcional;
- separación explícita anti-leakage.

## Arquitectura

```text
CUI
 │
 ▼
Agente de evidencia (ReAct)
 │
 ├─ obtener_proyecto(CUI)
 ├─ buscar_criterios_marco(query, categoria?)
 └─ consultar_marco_logico(CUI) [opcional]
 │
 ▼
Clasificador estructurado
 │
 ▼
Validación determinista
 │
 ├─ falla ───────────────┐
 │                       │ feedback
 ▼                       │
Verificador semántico    │
 │                       │
 ├─ rechaza ─────────────┘
 │
 ├─ max iteraciones → revisión humana
 ▼
Resultado aprobado
```

La trayectoria no está predefinida: cada proyecto puede generar distintas consultas,
herramientas y número de iteraciones.

## Anti-leakage

Durante inferencia se leen únicamente:

- `PROYECTOS`
- `BRECHAS`
- Marco 2021
- imagen de marco lógico, si existe

`GROUND_TRUTH`, RA2021, RA2023 y RA2024 NO son accesibles al agente.

`evaluate.py` es el único módulo que lee `GROUND_TRUTH`.

## Instalación

```powershell
cd agente_sostenible_next_level

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Copy-Item .env.example .env
```

Agrega tu `OPENAI_API_KEY` a `.env`.

## 1. Tests locales sin gastar API

```powershell
python test_local.py
```

Deberías ver:

```text
✅ Tests locales OK
   423 proyectos
   640 registros de brecha
   423/423 CUIs con brecha
   8 categorías normativas mapeadas
   GROUND_TRUTH aislado de las tools
```

## 2. Primer CUI de punta a punta

```powershell
python main.py 2017723 --trace
```

La primera vez también se generan embeddings del Marco.

## 3. Casos sugeridos

```powershell
python main.py 2017723 --trace
python main.py 2016076 --trace
python main.py 2306120 --trace
```

El último es útil como caso difícil porque el histórico presenta conflicto y el agente
no puede ver ese conflicto.

## 4. Benchmark pequeño

No corras 423 casos de frente.

```powershell
python evaluate.py --limit 10
```

Luego:

```powershell
python evaluate.py --limit 30
```

Y recién cuando el pipeline esté estable:

```powershell
python evaluate.py --all
```

El benchmark calcula:

- coverage,
- abstention rate,
- selective accuracy,
- macro F1,
- confusion matrix,
- iteraciones,
- tool calls,
- consultas al Marco.

## 5. Multimodalidad

Coloca imágenes dentro de:

```text
data/marcos_logicos/
```

El filename debe contener el CUI:

```text
2017723_marco_logico.jpg
```

El agente decide si necesita llamar `consultar_marco_logico`.

## 6. Demo visual

```powershell
streamlit run streamlit_app.py
```

## 7. LangSmith

En `.env`:

```text
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=utec-agente-sostenible
```

Así puedes mostrar trazas reales del agente en la presentación.

## Archivos principales

```text
schemas.py          modelos de salida
rag.py              knowledge base normativa
guardrails.py       validaciones básicas
toolbox.py          tools
agent.py            agente ReAct
graph.py            feedback loop LangGraph
main.py             CLI de inferencia
evaluate.py         benchmark contra ground truth
streamlit_app.py    demo visual opcional
test_local.py       tests sin API
```

## Recomendación de ejecución

Primero `test_local.py`. Luego un CUI con `main.py`. Después 10 casos con
`evaluate.py`. No agregues más complejidad hasta que esos tres pasos pasen.


## Nota OpenAI Responses API

Esta versión usa `ChatOpenAI(..., use_responses_api=True)` porque GPT-5.6 con
function tools y reasoning debe ejecutarse mediante la Responses API. Se mantiene
`reasoning_effort="medium"` para el agente, clasificador, judge y visión.

Si venías de una versión anterior, actualiza primero:

```powershell
python -m pip install -U "langchain-openai>=1.4.1" "openai>=2.0.0"
```


## Documentación para revisión

- `ARCHITECTURE.md`: arquitectura y decisiones de diseño.
- `CODE_WALKTHROUGH.md`: guía para estudiar el código archivo por archivo.
- `GITHUB_SETUP.md`: pasos seguros para subir el repositorio.
- `test_local.py`: smoke tests que no consumen API.

### Semántica de estado

`APROBADO` significa que el pipeline puede cerrar sin revisión humana.
`REVISION_HUMANA` significa que la clasificación requiere validación o que el
agente decidió abstenerse por información insuficiente.
