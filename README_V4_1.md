# Ajuste puntual V4.1 — calidad del RAG y trazabilidad

Se instala SOBRE V4, sin modificar V1/V2/V3, sin reemplazar los 423 CUIs,
los 121K registros ni el índice SQLite de la biblioteca.

Corrige los problemas detectados en la trayectoria real del CUI 2045301:
1. Los proyectos de saneamiento recuperan páginas pertinentes de INEI agua,
   MEF brechas y fuentes climáticas, no boletines eléctricos por búsquedas OR indiscriminadas.
2. El supervisor no repite la misma consulta textual a marco/contexto ya realizada.
   Si lo propone, finaliza y registra por qué; no garantiza otras formas de redundancia.
3. `fuentes_contexto` se obtiene de los resultados realmente recuperados y Streamlit
   las rotula como "fuentes recuperadas", no como citas específicas por afirmación.

No convierte alineamiento con NDC en requisitos jurídicos del Marco 2021. Las
recomendaciones siguen siendo preliminares y requieren revisión técnica.

## Instalar en PowerShell

En la raíz del repo local, detener Streamlit con Ctrl+C y ejecutar:

```powershell
cd "C:\Users\Sebastian\Downloads\agente-sostenible-utec"
Expand-Archive "$HOME\Downloads\agente_sostenible_v4_1_patch.zip" -DestinationPath . -Force
python -m unittest discover -s tests -p "test_v4_1_offline.py" -v
streamlit run streamlit_app_v2.py
```

CUI de prueba: **2045301**, modo **Investigador V4**. La inferencia cuesta API;
la prueba de unittest es gratuita. No es necesario reindexar PDFs.

Para demostrar las tres ramas puedes utilizar CUIs obtenidos con
`python seleccionar_casos_v4.py`. Recuerda verificar el estado de gasto en
la ficha, sin deducir actividad solo desde gasto cero 2023–2026.
