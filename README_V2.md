# V2 — Agente de investigación de elegibilidad sostenible

**Extensión experimental para el repositorio** `Saguedo97/agente-sostenible-utec`. Mantiene `graph.py`, `agent.py`, `rag.py` y `evaluate.py` sin modificaciones. La V1 sigue disponible como baseline.

## Instalación y ejecución en Windows PowerShell

```powershell
cd C:\ruta\agente-sostenible-utec
pip install -r requirements.txt
# Configurar OPENAI_API_KEY en .env (no subir .env a GitHub)
$env:V2_MODEL = "gpt-4.1-mini"
streamlit run streamlit_app_v2.py
```

Prueba sin API: en el sidebar elige **Consultar ficha (sin IA)**.

## Preparar los 121,477 proyectos (una vez)

Coloca el archivo `Data 23_26.xlsx` **fuera de GitHub** en un directorio local. Ejecuta:

```powershell
python universo_v2.py preparar "C:\ruta\Data 23_26.xlsx"
python universo_v2.py consultar 2000846
```

El índice SQLite se genera en `data/universo_2023_2026.sqlite` (definible con `UNIVERSE_DB_PATH`). El archivo **debe permanecer fuera del control de versiones**: añadir `data/*.sqlite` y `data/*.sqlite*` al `.gitignore`.

La conversión utiliza `openpyxl` en modo streaming para no cargar las 121 mil filas de Excel simultáneamente. La primera ejecución puede demorar; luego la consulta por CUI está indexada. En la primera consulta al dataset de 423 se carga su Excel local una vez.

## Dos modos en el frontend

- **Investigador V2:** `investigacion_v2.py` propone planes, elige normativa / visión / contraste / finalizar y produce diagnóstico documental trazable.
- **Clasificador V1:** `graph.py` permanece como baseline para comparaciones.

En V2 se muestra: plan vigente, decisiones, evidencia consultada, dictámenes independientes, documentación faltante y descargas JSON. No es una certificación de elegibilidad verde ni una aprobación de financiamiento.

## Pruebas

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python investigacion_v2.py 2017723 --trace
```

La segunda prueba realiza llamadas pagadas a OpenAI. Requiere credenciales y saldo. Una validación completa debe correr 3 escenarios distintos y comparar contra V1 con resultados medidos.

## Seguridad antes de publicar Streamlit

1. Guardar `OPENAI_API_KEY` exclusivamente en Streamlit Secrets (o entorno local).
2. Añadir autenticación, límites por usuario y presupuesto por ejecución. **No** exponer una app pública con llamadas a modelos pagadas sin controles.
3. Mantener las bases de 121k CUIs fuera de GitHub; verificar licencia/origen antes de compartirlas.
4. No ingresar columnas de emisiones ni etiquetas históricas en inferencia.

## Archivos V2

- `universo_v2.py`: ingesta streaming e índice SQLite.
- `investigacion_v2.py`: grafo agéntico de investigación.
- `streamlit_app_v2.py`: frontend.
- `docs/AGENT_CARD_V2.md`: perfil de agente para exposición.
- `docs/ARQUITECTURA_V2.md`: diagrama Mermaid y arquitectura de componentes.
- `tests/`: pruebas de reglas y de ingesta sin acceso a API.

## Referencias didácticas

- [Showdown — workflows versus agentes](https://github.com/alzamoralabs/Showdown)
- [Sesión 23 — investigación y subagentes](https://github.com/alzamoralabs/Sesion23)
- [Sesión 24 — contraste y votación](https://github.com/alzamoralabs/Sesion24)
