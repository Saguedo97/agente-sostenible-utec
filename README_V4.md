# V4 · Agente investigador de elegibilidad sostenible (3 casos + RAG multifuente)

## Demo en 15 minutos

Este parche se instala encima del repositorio que YA tiene V1/V2/V3. **No sobrescribe el motor V3**: crea `investigacion_v4.py` y modifica solamente la interfaz `streamlit_app_v2.py`. El índice de 15 PDFs se entrega precalculado; no necesitas copiar ni cargar de nuevo esos PDFs para la demo.

**En PowerShell:**

```powershell
cd "C:\Users\Sebastian\Downloads\agente-sostenible-utec"
# Detener Streamlit antes: Ctrl+C
git switch -c feature/v4-tres-casos-rag
Expand-Archive "$HOME\Downloads\agente_sostenible_v4_patch.zip" -DestinationPath . -Force
python -m unittest discover -s tests -p "test_v4_offline.py" -v
python -c "from rag_multifuente import buscar_contexto; print([r['fuente'] for r in buscar_contexto('agua saneamiento adaptación cambio climático',departamento='Junin')])"
streamlit run streamlit_app_v2.py
```

En la barra lateral elegir **Investigador V4 (3 casos + RAG multifuente)**. Primero CUI `2017723` (caso A). Para hallar otros dos ejemplos en tu SQLite local ejecutar en otra terminal:

```powershell
python seleccionar_casos_v4.py
```

Ingresar CUI `B` y luego CUI `C`, si hay. **Ejecutar investigación** efectúa llamadas de OpenAI; **Consultar ficha (sin IA)** es gratis.

## Qué incluye

- `router_cui.py`: consulta LOS DOS datasets por CUI, fusiona variables y brechas, preserva procedencia y oculta clasificación histórica.
- `rag_marco_completo.py`: búsqueda de criterios en TODO el PDF Marco 2021 local, no solamente ocho páginas verdes. NO sustituye la inspección de los requisitos reales.
- `rag_multifuente.py`: índice SQLite FTS5 de 15 PDFs de NDC, ENCC, biodiversidad, MEF, INEI, CENEPRED, tesoro, ley presupuestaria. `data/biblioteca_v4.sqlite` ya está precargada para uso inmediato.
- `investigacion_v4.py`: LangGraph con plan, supervisor, herramientas, reflexión, auditoría de cierre, JSON y trayectoria.
- `streamlit_app_v2.py`: agrega opción V4, indicador del caso, propuestas de mejora, fuentes citadas; V1/V2/V3 permanecen seleccionables.
- `seleccionar_casos_v4.py`: encuentra proyectos del universo con gasto y sin inicio según los campos disponibles.
- `tests/test_v4_offline.py`: 8 pruebas offline sin créditos API.

## Criterios de diseño

**A**: proyecto en los 423, inferencia ciega; después se compara la salida con `GROUND_TRUTH` FUERA del motor. Si el CUI también está en 2023–2026, se suman variables recientes conservando fuentes.

**B**: CUI no etiquetado con ejecución observada. Evaluación de pertinencia de categoría Marco 2021 según propósito y componentes disponibles; gasto no acredita elegibilidad.

**C**: CUI no etiquetado sin inicio confirmado; se dan recomendaciones prospectivas conforme al Marco y políticas relevantes. Si solo hay gasto cero reciente sin evidencia de inicio, se marca **prospectivo por confirmar**, NO "nunca ejecutado".

**Normativo vs contextual**: el Marco 2021 es la fuente para clasificar requisitos; la NDC 3.0 de 2025 y demás estrategias sirven como sugerencias actuales y no como requisitos obligatorios retrospectivos.

**Cobertura geográfica**: el informe CENEPRED sobre La Libertad solo se recupera para proyectos de ese departamento. INEI/MEF nacionales no prueban el impacto de un CUI particular. La duplicación del informe CENEPRED fue eliminada al indexar.

**No hay conexión en vivo a API Invierte.pe**: se usan las dos extracciones Excel/SQLite locales. El `ground truth` no se emplea en la inferencia.

## Dependencias y cuidados

Se reutilizan `langgraph`, `langchain-openai`, `pypdf`, `pydantic`, `python-dotenv`, `streamlit` y bibliotecas del proyecto. El índice FTS usa SQLite estándar, NO embeddings y NO genera costos de API al buscar. Es una primera versión de RAG léxico, **no un buscador vectorial híbrido**.

`data/*.sqlite` ya está ignorado en `.gitignore` del repositorio. No subas el índice documental, datos Excel ni `.env` a GitHub. Confirma con `git status` antes del commit.

El motor pasó tests offline de router y recuperación. **No está probado todavía con OpenAI real ni con las tres ramas completas**, así que ante `Traceback`, copiar únicamente el error sin clave. El modelo V4 por defecto es `gpt-4.1-mini`; cambiar con `V4_MODEL` en `.env` solo si el nuevo identificador está disponible.

## GitHub luego de verificar

```powershell
git add router_cui.py rag_marco_completo.py rag_multifuente.py investigacion_v4.py seleccionar_casos_v4.py streamlit_app_v2.py README_V4.md tests/test_v4_offline.py
git commit -m "feat: add three-case sustainability investigation and multisource RAG"
git push -u origin feature/v4-tres-casos-rag
```

**Límites conocidos**: las recomendaciones aún requieren validación especializada; no hay evaluación masiva de los 423 en esta entrega; el detector C se basa en los flags disponibles, que pueden ser imprecisos; RAG léxico puede recuperar páginas semánticamente adyacentes; estadísticas agregadas no son indicadores de impacto CUI.
