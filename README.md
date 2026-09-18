# Agente para clasificación sostenible de proyectos públicos

Proyecto desarrollado para clasificar proyectos de inversión pública según las categorías verdes del **Marco del Bono Sostenible del Perú 2021**.

La idea es que el sistema no dependa únicamente de una clasificación hecha directamente por un LLM. El agente puede consultar información del proyecto, revisar sus brechas, buscar criterios dentro del Marco 2021 y, cuando está disponible, revisar imágenes del marco lógico del proyecto.

Si la información no es suficiente para sustentar una clasificación, el sistema puede abstenerse y enviar el caso a revisión humana.

## Estructura general

```text
CUI
 │
 ▼
Agente
 │
 ├─ obtener_proyecto(CUI)
 ├─ buscar_criterios_marco(query, categoria?)
 └─ consultar_marco_logico(CUI)
 │
 ▼
Clasificación propuesta
 │
 ▼
Validación
 │
 ▼
Verificación
 │
 ├─ resultado válido → salida final
 └─ resultado débil → feedback → nueva iteración

## Arquitectura del sistema

La siguiente figura resume el flujo general del agente. El sistema recibe un CUI, consulta información estructurada del proyecto, busca criterios del Marco del Bono Sostenible del Perú 2021 y, cuando es necesario, revisa imágenes del marco lógico. Luego genera una clasificación estructurada, aplica validaciones y pasa por un verificador semántico. Si la salida no es suficientemente sólida, el sistema entrega feedback al agente para una nueva iteración.

![Arquitectura del agente](assets/arquitectura_agente.png)
