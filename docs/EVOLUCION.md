# Evolución del prototipo

| Versión | Propósito | Diferencia principal |
| --- | --- | --- |
| V1 | Clasificador de proyectos | Flujo secuencial, extracción y verificación |
| V2 | Investigador adaptativo | Supervisor elige herramientas según incertidumbres |
| V3 | Planificación y reflexión | Tareas explícitas, cambios de plan y auditoría de cierre |
| V4 | Dos bases, tres casos, RAG multifuente | Históricos, proyectos en ejecución y recomendaciones prospectivas |
| V4.1 | Recuperación contextual | Relevancia temática, deduplicación de búsquedas y registro de fuentes recuperadas |
| V4.2 | Control de categorías | Restringe clasificación a categorías admitidas y evita presentar tipologías Invierte.pe como elegibilidad |

## Decisiones metodológicas

- Los 423 CUIs tienen etiquetas históricas, pero estas no deben incorporarse al contexto de inferencia.
- El universo 2023–2026 contiene CUIs sin etiquetas, con y sin gasto reportado en el período.
- Un mismo CUI puede figurar en ambas fuentes; se integran atributos conservando procedencia.
- Marco del Bono Sostenible del Perú 2021: criterios de elegibilidad. Políticas y estadísticas posteriores: información contextual y recomendaciones, no reglas retroactivas.
- Los dictámenes son preliminares. La evidencia insuficiente es una respuesta permitida, no un error del sistema.

## Limitaciones observadas en ejecuciones reales

- V3 tendía a auditar repetidamente un cierre sin obtener nueva evidencia.
- La primera V4 consultó fuentes contextuales redundantes para un proyecto de saneamiento.
- Una ejecución del caso A confundió `PIP Mayor` con una categoría elegible del marco; motivó V4.2.
- Las fuentes recuperadas no siempre respaldan todas las recomendaciones generadas.

El éxito funcional de las rutas A/B/C no debe confundirse con exactitud de clasificación medida. No se ha completado la evaluación ciega masiva de los 423 registros.

## Documentación histórica

Los README anteriores se conservan en `docs/historico/` para reproducibilidad y trazabilidad de parches. El punto de entrada para usuarios es el `README.md` principal.
