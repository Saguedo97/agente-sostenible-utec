# V4.2 — control de categorías de elegibilidad (corrección crítica)

Este parche corrige el error observado en el CUI 2017723: el LLM devolvió «PIP Mayor» / una descripción del tipo de proyecto como si fuese una **categoría elegible** del Marco 2021, con certeza alta, sin citar la página sectorial 35.

Cambios:
- `Dictamen.clasificacion_preliminar` ahora solo permite una de las categorías del Marco 2021 (o `No aplica` / `Información insuficiente`). Incluye las 8 categorías verdes del proyecto y las 3 categorías sociales de la Tabla 3 del Marco 2021; no permite `PIP Mayor` ni un párrafo.
- El plan y el dictamen exigen distinguir tipología Invierte.pe de categoría de elegibilidad.
- La búsqueda del Marco se enriquece con nombre/función del CUI y da prioridad a páginas sectoriales relacionadas con el tema, sin presuponer elegibilidad.
- Si una categoría propuesta no cita su página sectorial realmente recuperada, se convierte conservadoramente en `Información insuficiente`; no se inventa el soporte.
- Si el dictamen informa incertidumbres o documentos requeridos, no permite certeza `alta` en elegibilidad preliminar.

## Instalar

En PowerShell, desde el repositorio donde YA instalaste V4/V4.1:

```powershell
cd "C:\Users\Sebastian\Downloads\agente-sostenible-utec"
Expand-Archive "$HOME\Downloads\agente_sostenible_v4_2_patch.zip" -DestinationPath . -Force
python -m unittest discover -s tests -p "test_v4_2_offline.py" -v
streamlit run streamlit_app_v2.py
```

Repetir una sola vez CUI `2017723` seleccionando V4. Una ejecución real consume API.

**Nota de calidad:** estas pruebas son offline. La corrección reduce dos errores de salida y búsqueda pero no acredita por sí sola exactitud jurídica/técnica, que requiere revisión humana. No se modifican las dos bases, ground truth, el índice de contexto ni otros motores.
