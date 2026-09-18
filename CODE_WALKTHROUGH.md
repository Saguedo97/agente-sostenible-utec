# Guía para entender el código

Lee los archivos en este orden.

## 1. `schemas.py`

Define el contrato de salida con Pydantic.

Conceptos:
- lista cerrada de categorías;
- salida estructurada;
- diferencia entre clasificación, evidencia suficiente y revisión humana.

No llama a ningún modelo.

## 2. `rag.py`

Convierte las páginas normativas del Marco 2021 en documentos recuperables.

Funciones clave:
- `cargar_documentos_marco()`: extrae las páginas de categorías verdes;
- `obtener_vectorstore()`: crea el índice semántico una vez;
- `buscar_marco()`: recupera normativa por similitud o por categoría exacta.

Pregunta para revisión: ¿por qué el RAG solo usa el Marco 2021 y no los reportes
2021/2023/2024? Respuesta: para evitar leakage de las etiquetas históricas.

## 3. `toolbox.py`

Contiene las herramientas que el agente puede usar.

- `obtener_proyecto(cui)`: devuelve variables de PROYECTOS y sus BRECHAS;
- `buscar_criterios_marco(...)`: consulta `rag.py`;
- `consultar_marco_logico(cui)`: encuentra todas las imágenes del CUI y las
  analiza conjuntamente con visión.

La función `_cargar_datos()` no abre GROUND_TRUTH.

## 4. `agent.py`

Es la parte propiamente agéntica.

`create_agent(...)` recibe:
- un modelo;
- las tres tools;
- un system prompt.

El LLM decide durante la ejecución qué herramienta necesita y en qué orden.

`ejecutar_agente_evidencia()` además extrae:
- tool calls;
- consultas RAG;
- outputs de herramientas.

Eso permite observabilidad sin guardar chain-of-thought.

## 5. `guardrails.py`

Reglas simples que conviene resolver con código:
- formato de CUI;
- evidencia mínima;
- páginas normativas válidas;
- inconsistencias básicas de salida.

## 6. `graph.py`

Orquesta el sistema completo con LangGraph.

Nodos:
1. `nodo_agente`
2. `nodo_clasificador`
3. `nodo_validacion`
4. `nodo_verificador`
5. `nodo_finalizar` / `nodo_revision_humana`

El loop ocurre si el verificador rechaza el candidato y todavía quedan
iteraciones. El feedback vuelve al agente para que cambie su búsqueda.

## 7. `main.py`

CLI mínimo:

```powershell
python main.py 2017723 --trace
```

No contiene inteligencia; solo llama a `clasificar_cui()` e imprime el resultado.

## 8. `evaluate.py`

Es deliberadamente independiente de inferencia.

Aquí sí se abre `GROUND_TRUTH` para comparar la predicción con las etiquetas
históricas después de que el agente terminó.

Métricas:
- coverage;
- abstention rate;
- selective accuracy;
- macro-F1;
- matriz de confusión;
- iteraciones y tool calls.

## Cómo explicar el sistema en 30 segundos

"Separé la arquitectura en una capa agéntica y una capa de control. El agente
decide dinámicamente qué evidencia necesita y qué herramientas consultar. Un
clasificador estructurado propone la salida, reglas deterministas validan
consistencia y un verificador semántico puede devolver feedback y provocar una
nueva iteración. El ground truth está aislado y solo se usa al evaluar."
