# Investigador de elegibilidad sostenible · V3 (planificación + reflexión)

Esta versión **no reemplaza** el clasificador V1 ni el investigador V2. Los conserva como baselines en `streamlit_app_v2.py`.

## Problema detectado con CUI 2017723

En la V2, el supervisor generó tres tareas, consultó normativa una vez y decidió finalizar. No constaba si las otras tareas se resolvieron o quedaron bloqueadas. La V3 agrega gestión explícita del plan y auditoría antes de cerrar.

## Algoritmo

1. `cargar`: consulta el CUI (base 423, o SQLite 2023–2026).
2. `planificar`: crea 1–4 preguntas verificables (T1, T2...).
3. `decidir`: elige la próxima acción útil para una tarea pendiente, o pide finalizar.
4. `normativa` / `vision` / `debate`: ejecuta solo la herramienta elegida; registra E1, E2... y, cuando corresponda, referencias a páginas `E1:p35`.
5. `reflexionar`: resume el hallazgo, actualiza estados, y puede crear nuevas tareas. Un control determinista **rechaza tareas resueltas sin fuentes válidas**.
6. `auditar_cierre`: revisa cada pendiente; o autoriza continuar investigando o declara tareas bloqueadas con motivos. Si la salida deja tareas pendientes sin justificación, **veta el cierre**. Límites de pasos evitan bucles sin fin.
7. `finalizar`: reutiliza las validaciones de páginas normativas y la generación de diagnóstico preliminar de V2. Adjunta `plan_auditado` y `motivo_cierre`.

### Estado de las tareas

- **Pendiente**: la pregunta aún no está resuelta ni justificada como inaccesible.
- **Resuelta**: existe evidencia identificable (D0 = ficha, E1 = primera herramienta, `E1:p35` = página normativa recuperada).
- **Bloqueada**: requiere información no disponible o se alcanzó un límite; no equivale a no elegible.

Nota: una referencia valida procedencia técnica, **no demuestra que el modelo haya interpretado correctamente el criterio**. Se necesita revisión experta.

## Archivos añadidos/cambiados

- `investigacion_v3.py` (nuevo)
- `streamlit_app_v2.py` (actualizado, modos V3/V2/V1)
- `tests/test_investigacion_v3.py` y `tests/run_offline_smoke_v3.py` (nuevos)
- `docs/ARQUITECTURA_V3.md` y `docs/AGENT_CARD_V3.md` (nuevos)

No se modifican V1/V2, `rag.py`, `toolbox.py`, bases de datos ni etiquetas históricas.

## Cómo ejecutar

```powershell
cd "C:\Users\Sebastian\Downloads\agente-sostenible-utec"
python -m unittest discover -s tests -p "test_*.py" -v
streamlit run streamlit_app_v2.py
```

O ejecución de consola con trayectoria:

```powershell
python investigacion_v3.py 2017723 --trace
```

### Configuración opcional en `.env`

```dotenv
V3_MODEL=gpt-4.1-mini
V3_MAX_STEPS=5
```

Por defecto se utiliza `V2_MODEL` o `gpt-4.1-mini`; V1/V2 pueden usar modelos distintos. Nunca versionar `.env`.

## Cómo evaluar el comportamiento no determinista

Use 3–5 CUIs de dificultad diversa. Compare V1, V2 y V3 con los mismos datos, e inspeccione:

- Secuencia efectiva de herramientas y número de decisiones.
- Cambios de plan y nuevas preguntas generadas.
- Tareas resueltas / bloqueadas, evidencia por tarea y vetos de cierre.
- Calidad del diagnóstico y necesidad de revisión humana (evaluación experta).
- Tokens/costo/latencia obtenidos desde trazas de facturación o LangSmith, no estimaciones inventadas.

No basta con demostrar que el LLM produce resultados diferentes: hay que demostrar **decisiones justificadas por observaciones diferentes** y que esas decisiones mejoran el diagnóstico frente al workflow.

**Límites:** sin acceso automático a expedientes externos, criterio normativo no verificado semánticamente más allá de citas de página, sin prueba real de precisión sobre universo 121K, dos especialistas independientes pero no protocolo completo de debate con consenso.
